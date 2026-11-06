"""Erros e casos: onde o modelo acerta, onde erra e o que investigar."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .. import charts, config, data, ui


def _br(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render() -> None:
    cases = data.load_cases()
    ui.hero(
        "ERROS & CASOS · HOLDOUT",
        "O modelo erra em 4 de cada 10 cargas altas — e os falsos alarmes são cestos de risco.",
        "Um alerta errado não é só uma métrica: é uma checagem no pátio. Um evento perdido é uma parada que "
        "o forno paga. Esta seção abre os dois lados.",
        "352 cestos · 57 eventos · limiar operacional 0,45",
    )

    ui.kpi_row(
        [
            {"value": "33", "label": "eventos detectados", "note": "VP · 120,8 min de parada antecipados", "tone": "blue"},
            {"value": "95", "label": "alarmes falsos", "note": "FP · 0 min de parada observada", "tone": "amber"},
            {"value": "24", "label": "eventos perdidos", "note": "FN · 55,5 min de parada não avisados", "tone": "red"},
            {"value": "200", "label": "normais acertados", "note": "VN · 0 min de parada", "tone": "green"},
        ]
    )

    ui.section(
        "01",
        "Os scores se sobrepõem — e é isso que o limiar administra.",
        "Distribuição das probabilidades no holdout, separada por desfecho real. A linha tracejada é o limiar 0,45.",
    )
    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        ui.chart_header(
            "Há eventos com score baixo e normais com score alto",
            "Contagem de cestos por faixa de probabilidade. Sobreposição é esperada em um problema com sinal modesto.",
        )
        st.plotly_chart(
            charts.probability_hist(cases, 0.45),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source("Fonte: 05_casos_para_investigar.csv. Scores do ensemble original.")
    with right:
        ui.callout(
            "O modelo não separa perfeitamente os grupos. O ROC-AUC de 0,669 e o PR-AUC de 0,327 "
            "mostram um sinal útil, mas modesto. O limiar escolhe quais erros a operação prefere.",
            kind="blue",
            title="O que o gráfico diz",
        )
        ui.callout(
            "Falsos positivos se concentram em cestos de baixa densidade e pouco material pesado — "
            "fisicamente parecidos com os verdadeiros positivos. Não são alertas aleatórios.",
            kind="amber",
            title="Um achado importante",
        )

    ui.section(
        "02",
        "Os falsos positivos parecem cestos de risco. Os falsos negativos, não.",
        "Perfil mediano dos 352 cestos do holdout por resultado do modelo. Quatro quadrantes, quatro histórias operacionais.",
    )
    profile = data.error_profile().copy()
    order = ["VN", "FP", "FN", "VP"]
    profile["ordem"] = profile["resultado"].map({k: i for i, k in enumerate(order)})
    profile = profile.sort_values("ordem")
    display_profile = profile[
        [
            "resultado_label",
            "n",
            "prob_media",
            "pesado_mediana",
            "densidade_mediana",
            "parada_media_min",
            "volume_mediana",
            "peso_mediana",
        ]
    ].copy()
    display_profile["prob_media"] = (display_profile["prob_media"] * 100).round(1)
    display_profile["pesado_mediana"] = (display_profile["pesado_mediana"] * 100).round(1)
    st.dataframe(
        display_profile,
        width="stretch",
        hide_index=True,
        column_config={
            "resultado_label": "Resultado",
            "n": "Cestos",
            "prob_media": st.column_config.NumberColumn("Score médio (%)", format="%.1f"),
            "pesado_mediana": st.column_config.NumberColumn("% pesado (mediana)", format="%.1f"),
            "densidade_mediana": st.column_config.NumberColumn("Densidade (mediana)", format="%.3f"),
            "parada_media_min": st.column_config.NumberColumn("Parada média (min)", format="%.1f"),
            "volume_mediana": st.column_config.NumberColumn("Volume (m³)", format="%.1f"),
            "peso_mediana": st.column_config.NumberColumn("Massa (t)", format="%.1f"),
        },
    )
    ui.source("Fonte: 05_casos_para_investigar.csv. Medianas e médias descritivas; não há teste de diferença entre quadrantes.")

    cols = st.columns(3, gap="large")
    with cols[0]:
        ui.chart_header("Material pesado", "mediana da proporção na massa")
        st.plotly_chart(
            charts.outcome_bars(profile, "pesado_mediana", "proporção de pesado", percent=True),
            width="stretch",
            config={"displayModeBar": False},
        )
    with cols[1]:
        ui.chart_header("Densidade efetiva", "massa / volume estimado")
        st.plotly_chart(
            charts.outcome_bars(profile, "densidade_mediana", "densidade (t/m³)"),
            width="stretch",
            config={"displayModeBar": False},
        )
    with cols[2]:
        ui.chart_header("Parada média", "minutos por cestão")
        st.plotly_chart(
            charts.outcome_bars(profile, "parada_media_min", "minutos"),
            width="stretch",
            config={"displayModeBar": False},
        )

    ui.callout(
        "<strong>FP e VP têm perfil físico parecido:</strong> pouca sucata pesada e densidade baixa. "
        "O modelo está sinalizando cestos genuinamente arriscados que, naquele dia, não travaram a tampa. "
        "Já os <strong>FN</strong> são mais densos e param menos: o fator geométrico de uma peça específica "
        "não está capturado pela densidade média.",
        kind="red",
        title="A leitura operacional dos erros",
    )

    ui.section(
        "03",
        "A calibração é razoável, mas não perfeita.",
        "Probabilidade média prevista vs. fração real de eventos, em oito faixas de score. Um modelo perfeitamente calibrado ficaria na diagonal.",
    )
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.plotly_chart(
            charts.calibration(data.calibration_table(), brier=0.189),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source("Fonte: 05_casos_para_investigar.csv. Brier = 0,189; 8 faixas de quantis.")
    with right:
        ui.render_html(
            """
            <div style="padding-top:0.8rem;">
            <p style="font-family:'Source Serif 4',Georgia,serif;font-size:1.2rem;line-height:1.4;">
            O score é útil para ordenar risco, mas não deve ser lido como uma probabilidade exata.</p>
            <p style="color:#6E685D;font-size:0.9rem;line-height:1.65;">
            Em faixas altas, a taxa observada sobe; em faixas baixas, cai. A inclinação é a direção certa,
            mas os pontos não estão todos sobre a diagonal. Para decisão operacional, o limiar e o custo
            dos erros importam mais do que o valor absoluto do score.
            </p>
            </div>
            """
        )
        ui.callout(
            "A calibração pode mudar com a receita. O teste já mostrou mudança de composição nos meses "
            "finais; por isso o monitoramento mensal e o retreino são parte do plano.",
            kind="amber",
            title="Monitorar",
        )

    ui.section(
        "04",
        "Casos para investigar, um a um.",
        "Filtre os 352 cestos do holdout e abra um caso para comparar o risco com o desfecho e o perfil físico.",
    )
    f1, f2, f3 = st.columns([0.7, 1.0, 1.4])
    with f1:
        basket_filter = st.selectbox("Cesto", ["Todos", "Cesto 1", "Cesto 2"], key="err_basket")
    with f2:
        outcome_filter = st.multiselect(
            "Resultado",
            ["VP", "FP", "FN", "VN"],
            default=["VP", "FP", "FN", "VN"],
            key="err_outcome",
        )
    with f3:
        prob_range = st.slider(
            "Faixa de risco (%)",
            min_value=0,
            max_value=100,
            value=(0, 100),
            step=1,
            format="%d%%",
            key="err_prob",
        )

    filtered = cases.copy()
    if basket_filter != "Todos":
        filtered = filtered.loc[filtered["nu_carregamento"] == int(basket_filter[-1])]
    if outcome_filter:
        filtered = filtered.loc[filtered["resultado"].isin(outcome_filter)]
    filtered = filtered.loc[
        (filtered["probabilidade"] >= prob_range[0] / 100)
        & (filtered["probabilidade"] <= prob_range[1] / 100)
    ]
    filtered = filtered.sort_values("probabilidade", ascending=False)

    minutos = f"{filtered['parada_min'].sum():.1f}".replace(".", ",")
    ui.render_html(
        f"<p style='font-size:0.82rem;color:#6E685D;'>{len(filtered)} casos no filtro · "
        f"{int(filtered['carga_alta'].sum())} eventos reais · {minutos} min de parada.</p>"
    )

    if filtered.empty:
        st.info("Nenhum caso com esses filtros. Ajuste a faixa de risco ou o resultado.")
    else:
        show = filtered[
            [
                "cd_corrida",
                "nu_carregamento",
                "inicio_utc",
                "probabilidade",
                "resultado_label",
                "carga_alta",
                "parada_min",
                "peso_total",
                "volume_estimado",
                "prop_pesado",
                "densidade_media_cesto",
            ]
        ].copy()
        show["inicio_utc"] = pd.to_datetime(show["inicio_utc"]).dt.strftime("%d/%m/%Y")
        show["probabilidade"] = (show["probabilidade"] * 100).round(1)
        show["prop_pesado"] = (show["prop_pesado"] * 100).round(1)
        show = show.rename(
            columns={
                "cd_corrida": "Corrida",
                "nu_carregamento": "Cesto",
                "inicio_utc": "Data",
                "probabilidade": "Risco (%)",
                "resultado_label": "Resultado",
                "carga_alta": "Evento real",
                "parada_min": "Parada (min)",
                "peso_total": "Massa (t)",
                "volume_estimado": "Volume (m³)",
                "prop_pesado": "Pesado (%)",
                "densidade_media_cesto": "Densidade",
            }
        )
        st.dataframe(
            show,
            width="stretch",
            hide_index=True,
            column_config={
                "Risco (%)": st.column_config.ProgressColumn(
                    "Risco (%)", min_value=0, max_value=100, format="%.1f%%"
                ),
                "Evento real": st.column_config.CheckboxColumn("Evento real"),
                "Parada (min)": st.column_config.NumberColumn(format="%.1f"),
                "Massa (t)": st.column_config.NumberColumn(format="%.1f"),
                "Volume (m³)": st.column_config.NumberColumn(format="%.1f"),
                "Pesado (%)": st.column_config.NumberColumn(format="%.1f"),
                "Densidade": st.column_config.NumberColumn(format="%.3f"),
            },
        )

        labels = [
            f"{row.cd_corrida} · Cesto {int(row.nu_carregamento)} · {row.probabilidade:.0%} · {row.resultado_label}"
            for row in filtered.itertuples()
        ]
        selected = st.selectbox("Abrir um caso", labels, key="err_case")
        row = filtered.iloc[labels.index(selected)]
        pct = (cases["probabilidade"] < row["probabilidade"]).mean()
        pill_kind = {"VP": "blue", "FP": "amber", "FN": "red", "VN": "gray"}.get(row["resultado"], "gray")
        def _br(value: float, digits: int = 1) -> str:
            return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")

        stats = [
            ("Risco do modelo", f"{row['probabilidade']:.1%}".replace(".", ",")),
            ("Desfecho real", "carga alta" if row["carga_alta"] == 1 else "normal"),
            ("Parada", f"{_br(row['parada_min'])} min"),
            ("Massa", f"{_br(row['peso_total'])} t"),
            ("Volume", f"{_br(row['volume_estimado'])} m³"),
            ("Densidade", _br(row["densidade_media_cesto"], 3)),
            ("Pesado", f"{row['prop_pesado']:.1%}".replace(".", ",")),
            ("Percentil de risco", f"{pct:.0%}"),
        ]
        ui.case_card(
            f"Corrida {row['cd_corrida']} · Cesto {int(row['nu_carregamento'])}",
            f"{row['inicio_utc'].strftime('%d/%m/%Y %H:%M')} UTC · {row['resultado_label']} · "
            f"parada de {_br(row['parada_min'])} min",
            stats,
            pill_html=ui.pill(row["resultado_label"], pill_kind),
        )
        st.download_button(
            "Baixar os casos filtrados (CSV)",
            data=filtered.to_csv(index=False).encode("utf-8-sig"),
            file_name="evcomx_casos_filtrados.csv",
            mime="text/csv",
        )

    ui.section(
        "05",
        "O que os erros ensinam para o piloto.",
        "A operação precisa de uma regra clara para agir no amarelo e no vermelho, e de um registro do que foi feito.",
    )
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        ui.callout(
            "Os FP são cestos de baixa densidade e pouco pesado. A checagem no pátio pode ser rápida: "
            "olhar o topo e a compactação antes de liberar.",
            kind="amber",
            title="Alarme falso",
        )
    with c2:
        ui.callout(
            "Os FN são mais densos e param menos. O fator geométrico de uma peça específica não aparece "
            "na média. O piloto deve registrar esses casos para melhorar a próxima versão.",
            kind="red",
            title="Evento perdido",
        )
    with c3:
        ui.callout(
            "O limiar 0,45 privilegia recall. Se o custo da checagem subir, o limiar pode subir; se o custo "
            "da parada subir, pode cair. A decisão é da operação, com o histórico na mão.",
            kind="blue",
            title="Limiar",
        )

    ui.source(
        "Fonte: 05_casos_para_investigar.csv, 06_resumo_erros.csv e relatórios complementares. "
        "As associações são descritivas e não identificam causalidade."
    )
