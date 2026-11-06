"""Simulador didático: edite a receita do cestão e veja o risco se mover."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from .. import charts, config, data, features, simulator, ui

DAY_NAMES = {
    0: "segunda",
    1: "terça",
    2: "quarta",
    3: "quinta",
    4: "sexta",
    5: "sábado",
    6: "domingo",
}
TURNO_NAMES = {0: "0h–8h (madrugada)", 1: "8h–16h (manhã/tarde)", 2: "16h–24h (noite)"}


@st.cache_data(show_spinner=False)
def _preset_catalog() -> list[dict]:
    cases = data.load_cases()

    def pick(mask: pd.Series, sort_col: str, ascending: bool) -> pd.Series | None:
        sub = cases.loc[mask].sort_values(sort_col, ascending=ascending)
        for _, row in sub.iterrows():
            layers = features.preset_layers(row["cd_corrida"], int(row["nu_carregamento"]))
            if len(layers) > 0:
                return row
        return None

    picks = [
        ("Cesto 1 · normal acertado", pick((cases["resultado"] == "VN") & (cases["nu_carregamento"] == 1), "probabilidade", True)),
        ("Cesto 2 · evento detectado", pick((cases["resultado"] == "VP") & (cases["nu_carregamento"] == 2), "probabilidade", False)),
        ("Cesto 2 · alarme falso", pick((cases["resultado"] == "FP") & (cases["nu_carregamento"] == 2), "probabilidade", False)),
        ("Cesto 1 · evento perdido", pick((cases["resultado"] == "FN") & (cases["nu_carregamento"] == 1), "parada_s", False)),
    ]
    catalog = []
    for prefix, row in picks:
        if row is None:
            continue
        corrida = str(row["cd_corrida"])
        basket = int(row["nu_carregamento"])
        layers = features.preset_layers(corrida, basket)
        meta = features.preset_metadata(corrida, basket)
        if layers["consumed_at_utc"].notna().any():
            span = layers["consumed_at_utc"].max() - layers["consumed_at_utc"].min()
            meta["duracao_montagem_min"] = span.total_seconds() / 60.0
        label = (
            f"{prefix} · {corrida} · risco {row['probabilidade']:.0%} · "
            f"{'evento' if int(row['carga_alta']) == 1 else 'normal'}"
        )
        catalog.append(
            {
                "label": label,
                "corrida": corrida,
                "basket": basket,
                "layers": layers,
                "meta": meta,
                "oficial": float(row["probabilidade"]),
                "real": int(row["carga_alta"]),
                "parada_s": float(row["parada_s"]),
            }
        )
    return catalog


def _reset_editor(preset: dict) -> None:
    st.session_state.sim_layers = preset["layers"].copy()
    st.session_state.sim_loaded_preset = preset["label"]
    st.session_state.sim_basket_choice = preset["basket"]
    meta = preset["meta"]
    turno = meta.get("turno")
    dia = meta.get("dia_semana")
    duracao = meta.get("duracao_montagem_min")
    st.session_state.sim_turno = int(turno) if turno is not None and not pd.isna(turno) else 1
    st.session_state.sim_dia = int(dia) if dia is not None and not pd.isna(dia) else 0
    st.session_state.sim_feriado = bool(meta.get("feriado_nacional") or 0)
    st.session_state.sim_duracao = (
        float(duracao) if duracao is not None and not pd.isna(duracao) else 24.0
    )
    if meta.get("cesto1"):
        c1 = meta["cesto1"]
        st.session_state.sim_c1_peso = float(c1["peso_total"])
        st.session_state.sim_c1_dens = float(c1["densidade_media_cesto"])
        st.session_state.sim_c1_pesado = float(c1["prop_pesado"])
        st.session_state.sim_c1_leve = float(c1["prop_leve"])
    st.session_state.sim_editor_version = st.session_state.get("sim_editor_version", 0) + 1


def _ensure_state(catalog: list[dict]) -> None:
    if not catalog:
        return
    if "sim_layers" not in st.session_state:
        _reset_editor(catalog[0])


def _zero_recipe() -> None:
    st.session_state.sim_layers = pd.DataFrame(
        {
            "nu_camada": [1],
            "material_code": ["SHRE"],
            "weight_t": [10.0],
            "descricao": ["SHREDDER"],
            "classe": ["Leve"],
        }
    )
    st.session_state.sim_editor_version = st.session_state.get("sim_editor_version", 0) + 1


def _open_preset(preset: dict) -> None:
    st.session_state.sim_preset = preset["label"]
    _reset_editor(preset)


def _apply_yard_action() -> None:
    layers = st.session_state.get("sim_layers")
    if layers is None or layers.empty:
        return
    catalogo = features.material_catalog()
    class_map = catalogo.set_index("material_code")["classe"].to_dict()
    out = layers.copy()
    classes = out["material_code"].map(class_map)
    mask = classes.eq("Leve")
    out.loc[mask, "material_code"] = "GUSS"
    if "classe" in out:
        out.loc[mask, "classe"] = "Pesado"
    if "descricao" in out:
        out.loc[mask, "descricao"] = "GUSA SOLIDO"
    st.session_state.sim_layers = out
    st.session_state.sim_editor_version = st.session_state.get("sim_editor_version", 0) + 1


def _score(feats: pd.DataFrame) -> tuple[float, float, str, str]:
    score = simulator.predict(feats)
    pct = simulator.percentile(score)
    band, tone = simulator.risk_band(score)
    return score, pct, band, tone


def render() -> None:
    ui.hero(
        "SIMULADOR · LEITURA DIDÁTICA",
        "Monte o cestão. Veja o risco se mover.",
        "Edite materiais, pesos e camadas e acompanhe como a composição muda a leitura de risco. "
        "Use um caso real do holdout como ponto de partida.",
        "Modelo didático separado do ensemble oficial · 3.501 cestos de referência",
    )

    table = data.load_features_table()
    if table is None or not config.APP_MODEL_PATH.exists():
        st.warning(
            "O modelo do simulador ainda não foi gerado. Rode `uv run python scripts/train_simulator.py` "
            "e recarregue o app."
        )
        return

    ui.callout(
        "Esta é uma <strong>leitura didática</strong>, não o ensemble oficial. Para permitir edição em tempo real, "
        "o app usa uma regressão logística transparente treinada com os mesmos atributos e o mesmo holdout. "
        f"{simulator.metric_text()}",
        kind="blue",
        title="Antes de mexer",
    )

    catalog = _preset_catalog()
    _ensure_state(catalog)
    high_risk = next((p for p in catalog if "evento detectado" in p["label"]), catalog[0])
    with st.expander(
        "Roteiro de demonstração de 2 minutos",
        expanded=bool(st.session_state.get("sim_demo_open", False)),
    ):
        st.markdown(
            "**1.** Abra o caso real de risco alto.  "
            "**2.** Aplique uma ação de pátio ilustrativa: trocar os materiais leves por gusa sólido.  "
            "**3.** Compare o risco antes e depois e mostre o que puxou o risco."
        )
        d1, d2 = st.columns(2)
        with d1:
            st.button(
                "1. Abrir caso de risco alto",
                key="sim_demo_high",
                on_click=_open_preset,
                args=(high_risk,),
                width="stretch",
            )
        with d2:
            st.button(
                "2. Aplicar ação de pátio",
                key="sim_demo_action",
                on_click=_apply_yard_action,
                width="stretch",
            )
        st.caption(
            "A ação é uma ilustração para mostrar a direção do sinal; não é uma recomendação operacional validada. "
            "O roteiro evita digitar ao vivo durante a apresentação."
        )

    labels = [p["label"] for p in catalog]
    current = st.session_state.get("sim_loaded_preset", labels[0])
    if current not in labels:
        current = labels[0]
        st.session_state.sim_loaded_preset = current
    if st.session_state.get("sim_preset") not in labels:
        st.session_state.sim_preset = current

    preset = catalog[labels.index(current)]
    chosen = st.selectbox("Começar de um caso real", labels, key="sim_preset")
    if chosen != st.session_state.get("sim_loaded_preset"):
        _reset_editor(catalog[labels.index(chosen)])
        st.rerun()

    preset = catalog[labels.index(chosen)]

    # Baseline do preset: calculado uma vez por receita de origem.
    if st.session_state.get("sim_baseline_preset") != preset["label"]:
        try:
            base_feats = features.build_basket_features(
                preset["layers"][["nu_camada", "material_code", "weight_t"]],
                int(preset["basket"]),
                context={
                    "dia_semana": int(preset["meta"].get("dia_semana") or 0),
                    "turno": int(preset["meta"].get("turno") or 1),
                    "feriado_nacional": int(preset["meta"].get("feriado_nacional") or 0),
                },
                cesto1_summary=preset["meta"].get("cesto1"),
                duracao_montagem_min=(
                    float(preset["meta"]["duracao_montagem_min"])
                    if preset["meta"].get("duracao_montagem_min") is not None
                    and not pd.isna(preset["meta"]["duracao_montagem_min"])
                    else 24.0
                ),
            )
            st.session_state.sim_baseline_score = simulator.predict(base_feats)
            st.session_state.sim_baseline_preset = preset["label"]
        except Exception:
            st.session_state.sim_baseline_score = np.nan

    # ------------------------------------------------------------------
    # controles
    # ------------------------------------------------------------------
    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown("#### 1. Receita do cestão")
        c1, c2, c3 = st.columns([1, 1, 1])
        st.session_state.setdefault("sim_basket_choice", preset["basket"])
        st.session_state.setdefault("sim_turno", 1)
        st.session_state.setdefault("sim_dia", 0)
        st.session_state.setdefault("sim_feriado", False)
        st.session_state.setdefault("sim_duracao", 24.0)
        with c1:
            basket = st.selectbox("Cesto", [1, 2], key="sim_basket_choice")
        with c2:
            turno = st.selectbox(
                "Turno",
                list(TURNO_NAMES.keys()),
                format_func=lambda x: TURNO_NAMES[x],
                key="sim_turno",
            )
        with c3:
            dia = st.selectbox(
                "Dia",
                list(DAY_NAMES.keys()),
                format_func=lambda x: DAY_NAMES[x],
                key="sim_dia",
            )
        c4, c5 = st.columns([1, 1])
        with c4:
            feriado = st.checkbox("Feriado nacional", key="sim_feriado")
        with c5:
            duracao = st.slider(
                "Duração da montagem (min)",
                min_value=0,
                max_value=90,
                step=1,
                key="sim_duracao",
            )  # valor vem do Session State

        if basket == 2:
            with st.expander("Cesto 1 · contexto usado pelo modelo", expanded=False):
                st.caption(
                    "O cesto 2 é avaliado com o resumo do cesto 1 já montado. Estes valores entram como contexto."
                )
                st.session_state.setdefault("sim_c1_peso", 58.0)
                st.session_state.setdefault("sim_c1_dens", 0.84)
                st.session_state.setdefault("sim_c1_pesado", 0.31)
                st.session_state.setdefault("sim_c1_leve", 0.30)
                k1, k2 = st.columns(2)
                with k1:
                    c1_peso = st.slider(
                        "Massa do cesto 1 (t)",
                        min_value=20.0,
                        max_value=100.0,
                        step=0.5,
                        key="sim_c1_peso",
                    )
                    c1_pesado = st.slider(
                        "Pesado no cesto 1",
                        min_value=0.0,
                        max_value=0.60,
                        step=0.01,
                        key="sim_c1_pesado",
                    )
                with k2:
                    c1_dens = st.slider(
                        "Densidade do cesto 1 (t/m³)",
                        min_value=0.40,
                        max_value=1.30,
                        step=0.01,
                        key="sim_c1_dens",
                    )
                    c1_leve = st.slider(
                        "Leve no cesto 1",
                        min_value=0.0,
                        max_value=0.60,
                        step=0.01,
                        key="sim_c1_leve",
                    )
                c1_volume = c1_peso / c1_dens if c1_dens else np.nan
                st.caption(f"Volume implícito do cesto 1: {c1_volume:.1f} m³".replace(".", ","))
            cesto1_summary = {
                "peso_total": c1_peso,
                "volume_estimado": c1_volume,
                "densidade_media_cesto": c1_dens,
                "prop_pesado": c1_pesado,
                "prop_leve": c1_leve,
            }
        else:
            cesto1_summary = None

        catalogo = features.material_catalog()
        material_options = (
            catalogo.sort_values(["classe", "material_code"])["material_code"].astype(str).tolist()
        )
        desc_map = catalogo.set_index("material_code")["descricao"].to_dict()
        class_map = catalogo.set_index("material_code")["classe"].to_dict()

        layers = st.session_state.sim_layers.copy()
        layers["descricao"] = layers["material_code"].map(desc_map).fillna("—")
        layers["classe"] = layers["material_code"].map(class_map).fillna("—")
        editor_key = f"sim_editor_{st.session_state.get('sim_editor_version', 0)}"
        edited = st.data_editor(
            layers[["nu_camada", "material_code", "weight_t", "classe"]],
            num_rows="dynamic",
            width="stretch",
            hide_index=True,
            key=editor_key,
            column_config={
                "nu_camada": st.column_config.NumberColumn("Camada", min_value=1, step=1, required=True),
                "material_code": st.column_config.SelectboxColumn(
                    "Material", options=material_options, required=True
                ),
                "weight_t": st.column_config.NumberColumn(
                    "Peso (t)", min_value=0.0, max_value=60.0, step=0.05, format="%.2f", required=True
                ),
                "classe": st.column_config.TextColumn("Classe", disabled=True),
            },
        )
        edited = edited.dropna(subset=["material_code", "weight_t"]).copy()
        if edited.empty:
            st.warning("Adicione ao menos uma camada com material e peso.")
            return
        edited["nu_camada"] = edited["nu_camada"].fillna(
            pd.Series(range(1, len(edited) + 1), index=edited.index)
        )
        edited["weight_t"] = pd.to_numeric(edited["weight_t"], errors="coerce").fillna(0.0)
        if (edited["weight_t"] > 0).sum() == 0:
            st.warning("Adicione ao menos uma camada com peso maior que zero para calcular o risco.")
            return
        # Atualiza descrição/classe após uma troca de material.
        edited["descricao"] = edited["material_code"].map(desc_map).fillna("—")
        edited["classe"] = edited["material_code"].map(class_map).fillna("—")
        st.session_state.sim_layers = edited.copy()

        with st.expander("Dicionário de materiais e densidades"):
            dic = catalogo[["material_code", "descricao", "classe", "densidade"]].sort_values(
                ["classe", "material_code"]
            )
            st.dataframe(
                dic,
                width="stretch",
                hide_index=True,
                column_config={
                    "material_code": "Código",
                    "descricao": "Descrição",
                    "classe": "Classe",
                    "densidade": st.column_config.NumberColumn("Densidade (t/m³)", format="%.2f"),
                },
            )
            st.caption(
                "A massa é assumida em toneladas; o volume é massa / densidade de catálogo. "
                "RECC e RECG usam a mediana da classe Pesado."
            )

        context = {
            "dia_semana": int(dia),
            "turno": int(turno),
            "feriado_nacional": int(feriado),
        }
        try:
            feats = features.build_basket_features(
                edited[["nu_camada", "material_code", "weight_t"]],
                int(basket),
                context=context,
                cesto1_summary=cesto1_summary,
                duracao_montagem_min=float(duracao),
            )
        except Exception as exc:  # pragma: no cover - proteção para edição livre
            st.error(f"Não foi possível calcular os atributos desse cestão: {exc}")
            return

        score, pct, band, tone = _score(feats)

    # ------------------------------------------------------------------
    # resultado
    # ------------------------------------------------------------------
    with right:
        st.markdown("#### 2. Leitura de risco")
        band_label = {"baixo": "baixo", "atenção": "atenção", "alto": "alto"}[band]
        caption = (
            "A faixa é relativa à população de referência (percentis 50 e 75). "
            "O número grande é a probabilidade estimada pelo modelo didático; "
            "não use os cortes 30%/45% do ensemble oficial nesta escala."
        )
        ui.risk_scale(
            pct,
            low_cut=0.50,
            high_cut=0.75,
            label=f"Risco estimado · faixa {band_label}",
            value_text=f"{score:.1%}".replace(".", ","),
            caption=caption,
        )

        phys = simulator.physical_summary(feats)
        ref = table.loc[table["nu_carregamento"] == int(basket)]
        med = ref[["peso_total", "volume_estimado", "densidade_media_cesto", "prop_pesado", "num_camadas"]].median()

        def _br(value: float, digits: int = 1) -> str:
            return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")

        stats = [
            ("Massa", f"{_br(phys['peso'])} t", f"mediana: {_br(med['peso_total'])} t"),
            ("Volume", f"{_br(phys['volume'])} m³", f"mediana: {_br(med['volume_estimado'])} m³"),
            ("Densidade", _br(phys["densidade"], 3), f"mediana: {_br(med['densidade_media_cesto'], 3)}"),
            ("Pesado", f"{_br(phys['pesado']*100)}%", f"mediana: {_br(med['prop_pesado']*100)}%"),
            ("Camadas", f"{phys['camadas']}", f"mediana: {med['num_camadas']:.0f}"),
        ]
        ui.render_html(
            "<div class='case-grid'>"
            + "".join(
                f"<div class='case-stat'><div class='case-stat-label'>{k}</div>"
                f"<div class='case-stat-value'>{v}</div>"
                f"<div class='case-stat-label' style='text-transform:none;letter-spacing:0;font-weight:400;'>{note}</div></div>"
                for k, v, note in stats
            )
            + "</div>"
        )

        if preset["basket"] == int(basket):
            delta = score - st.session_state.get("sim_baseline_score", score)
            real_txt = "carga alta" if preset["real"] == 1 else "normal"
            delta_txt = f"{delta:+.1%}".replace(".", ",") if pd.notna(delta) else "—"
            oficial_txt = f"{preset['oficial']:.1%}".replace(".", ",")
            ui.render_html(
                f"<p style='font-size:0.78rem;color:var(--muted);line-height:1.55;margin-top:0.7rem;'>"
                f"Caso de origem: <strong>{preset['corrida']} · cesto {preset['basket']}</strong> · "
                f"score oficial do ensemble <strong>{oficial_txt}</strong> · desfecho real: <strong>{real_txt}</strong>"
                + (f" · parada de <strong>{preset['parada_s']/60:.1f} min</strong>".replace(".", ",") if preset["parada_s"] else "")
                + f".<br>Variação desde a receita original: <strong>{delta_txt}</strong>."
                + "</p>"
            )

        st.markdown("#### 3. O que puxa o risco")
        top, fam = simulator.explain(feats, top_n=9)
        st.plotly_chart(
            charts.contribution_bars(top),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source(
            "Contribuições do componente logístico (valor padronizado × coeficiente). "
            "Vermelho aumenta o risco; azul reduz. Não é uma explicação causal."
        )

        with st.expander("Ver contribuições por família"):
            st.plotly_chart(
                charts.family_bars(fam),
                width="stretch",
                config={"displayModeBar": False},
            )

        b1, b2 = st.columns(2)
        with b1:
            st.button(
                "Restaurar receita original",
                width="stretch",
                key="sim_restore",
                on_click=_reset_editor,
                args=(preset,),
            )
        with b2:
            st.button(
                "Recalcular do zero",
                width="stretch",
                key="sim_zero",
                on_click=_zero_recipe,
            )

    ui.callout(
        "O simulador serve para <strong>explorar a direção dos sinais</strong>, não para liberar ou bloquear um cestão. "
        "A decisão operacional exige o modelo validado, o limiar acordado e o piloto no pátio.",
        kind="amber",
        title="Limite de uso",
    )
    ui.source(
        "Modelo didático: regressão logística com 70 atributos físicos, treinada nos 3.149 cestos fora do holdout. "
        "A base de referência tem 3.501 cestos. O ensemble oficial está na seção Modelo."
    )
