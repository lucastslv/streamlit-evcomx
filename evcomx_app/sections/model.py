"""Modelo: decisão, split temporal, métricas e limiar."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .. import charts, config, data, ui


def _fmt(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(value: float) -> str:
    return f"{value:.1%}".replace(".", ",")


def _num(value: float) -> str:
    return f"{value:.3f}".replace(".", ",")


def render() -> None:
    ui.hero(
        "MODELO · HOLDOUT TEMPORAL",
        "Testado no futuro, o modelo avisa 6 de cada 10 cargas altas.",
        "Uma linha por cestão. O teste são as 180 corridas mais recentes, intocadas até a avaliação final. "
        "O limiar operacional é 0,45.",
        "Split cronológico 75% / 15% / 10% · 352 cestos e 57 eventos no teste",
    )

    ui.section(
        "01",
        "A unidade de decisão é o cestão, não a corrida.",
        "O alerta precisa chegar quando a balança fecha a última camada, antes de a ponte rolante levar o cesto ao forno.",
    )
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown("#### O momento")
        st.markdown(
            "Pesos, materiais e ordem das camadas já estão registrados. Tempo de parada e desfecho "
            "ficam de fora: são consequência, não preditor."
        )
    with c2:
        st.markdown("#### A unidade")
        st.markdown(
            "Cada carregamento sólido (cesto 1 e cesto 2) tem seu próprio evento. O cesto 2 entra "
            "com o forno já parcialmente preenchido e concentra mais eventos."
        )
    with c3:
        st.markdown("#### A validação")
        st.markdown(
            "Treino e teste são separados por tempo, não por sorteio. Assim, o modelo é avaliado "
            "em corridas futuras ao período de ajuste."
        )

    ui.section(
        "02",
        "A validação respeita a ordem do tempo.",
        "O teste só é usado uma vez, no final. A validação escolhe o limiar e verifica o desempenho fora do tempo.",
    )
    ui.render_html(
        """
        <div style="display:grid;grid-template-columns:1.6fr 0.9fr 0.7fr;gap:6px;margin:0.6rem 0 0.3rem 0;">
            <div style="background:#E9E2D4;padding:1rem;border-top:4px solid #1C1B18;">
                <div style="font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:#6E685D;font-weight:700;">Treino · 75%</div>
                <div style="font-family:'Source Serif 4',Georgia,serif;font-size:1.7rem;font-weight:700;">1.349 corridas</div>
                <div style="font-size:0.8rem;color:#6E685D;line-height:1.45;">Ajuste dos modelos, seleção de atributos e validação cruzada agrupada por corrida.</div>
            </div>
            <div style="background:#EFE9DC;padding:1rem;border-top:4px solid #2E657C;">
                <div style="font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:#6E685D;font-weight:700;">Validação · 15%</div>
                <div style="font-family:'Source Serif 4',Georgia,serif;font-size:1.7rem;font-weight:700;">270 corridas</div>
                <div style="font-size:0.8rem;color:#6E685D;line-height:1.45;">Escolha do limiar operacional e checagem fora do tempo.</div>
            </div>
            <div style="background:#F4DDD5;padding:1rem;border-top:4px solid #B6452F;">
                <div style="font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:#6E685D;font-weight:700;">Teste · 10%</div>
                <div style="font-family:'Source Serif 4',Georgia,serif;font-size:1.7rem;font-weight:700;">180 corridas</div>
                <div style="font-size:0.8rem;color:#6E685D;line-height:1.45;">352 cestos e 57 eventos. Intocado até a avaliação final.</div>
            </div>
        </div>
        """
    )
    ui.source("Fonte: notebook de modelagem e relatórios complementares. O holdout cobre jul–ago/2026 na amostra.")

    ui.section(
        "03",
        "As métricas do holdout, em linguagem de gestão.",
        "Com o limiar 0,45, o ensemble combina regressão logística, gradient boosting e random forest.",
    )
    m45 = data.threshold_metrics(0.45)
    ui.kpi_row(
        [
            {"value": _pct(m45["recall"]), "label": "recall", "note": f"{m45['vp']} de {m45['eventos']} eventos avisados", "tone": "red"},
            {"value": _pct(m45["precision"]), "label": "precisão", "note": f"{m45['alerts']} alertas; {m45['fp']} falsos positivos", "tone": "amber"},
            {"value": _num(m45["f2"]), "label": "F2-score", "note": "peso maior para recall", "tone": "blue"},
            {"value": "0,327", "label": "PR-AUC", "note": "prevalência no teste: 16,2%", "tone": "blue"},
            {"value": "0,669", "label": "ROC-AUC", "note": "0,189 de Brier", "tone": "blue"},
        ]
    )
    ui.callout(
        "Em linguagem de gestão: <strong>de cada 10 cargas altas, o modelo avisa 6</strong>. "
        "De cada 10 alertas, 2,6 eram carga alta; os outros 7,4 custam uma checagem no pátio. "
        "O teste foi feito nas corridas mais recentes, que o modelo nunca viu.",
        kind="blue",
        title="Traduzindo as métricas",
    )

    left, right = st.columns([0.95, 1.05], gap="large")
    with left:
        ui.chart_header("Matriz de confusão no limiar 0,45")
        ui.confusion_matrix(m45["tn"], m45["fp"], m45["fn"], m45["vp"])
        ui.render_html(
            f"<p style='font-size:0.82rem;color:#6E685D;line-height:1.55;'>"
            f"O modelo antecipa <strong>69% do tempo de parada</strong> (120,8 de 176,3 min). "
            f"Os falsos positivos são 95 alertas sem evento; cada um custa uma checagem no pátio.</p>"
        )
    with right:
        ui.chart_header(
            "A curva de precisão-recall",
            "O ponto operacional fica no joelho da curva; o limiar escolhido privilegia recall.",
        )
        st.plotly_chart(
            charts.pr_curve(data.pr_curve(), ap=0.327),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source("Fonte: 05_casos_para_investigar.csv. PR-AUC = 0,327; ROC-AUC = 0,669.")

    ui.callout(
        "A alternativa simples — alertar pelo volume do cestão — dispara <strong>291 alarmes falsos</strong> no teste; "
        "o ensemble, <strong>95</strong>. A PR-AUC é <strong>0,327 contra 0,154</strong>. O ganho vem de combinar "
        "composição, densidade e ordem das camadas, não de olhar mais volume.",
        kind="amber",
        title="Comparação com a alternativa simples",
    )
    ui.source("Fonte: apresentação final e notebook de modelagem. A regra por volume é a alternativa simples do projeto.")

    ui.section(
        "04",
        "O limiar é uma escolha operacional.",
        "Mover o limiar troca recall por precisão. A pergunta é quanto custa um alarme falso e quanto custa uma parada não avisada.",
    )
    opcoes_limiar = [f"{v/100:.2f}".replace(".", ",") for v in range(10, 71)]
    limiar_txt = st.select_slider(
        "Limiar de alerta",
        options=opcoes_limiar,
        value="0,45",
        key="model_threshold",
        help="Acima deste valor, o cestão recebe alerta.",
    )
    threshold = float(limiar_txt.replace(",", "."))
    m = data.threshold_metrics(threshold)
    cols = st.columns(4)
    cards = [
        ("Recall", _pct(m["recall"]), f"{m['vp']} de {m['eventos']} eventos"),
        ("Precisão", _pct(m["precision"]), f"{m['alerts']} alertas emitidos"),
        ("F2", _num(m["f2"]), f"{m['fp']} falsos positivos"),
        ("Cobertura de parada", f"{data.load_cases().loc[data.load_cases()['probabilidade'] >= threshold, 'parada_min'].sum():.1f} min".replace(".", ","), "tempo real nos alertas"),
    ]
    for col, (label, value, note) in zip(cols, cards):
        with col:
            ui.kpi_row([{"value": value, "label": label, "note": note, "tone": "blue"}])

    left, right = st.columns([0.95, 1.05], gap="large")
    with left:
        ui.chart_header(
            f"Matriz de confusão no limiar {threshold:.2f}".replace(".", ","),
            "Atualiza com o slider. O custo de cada erro depende da operação.",
        )
        ui.confusion_matrix(m["tn"], m["fp"], m["fn"], m["vp"])
    with right:
        ui.chart_header(
            "Recall, precisão e F2 ao longo do limiar",
            "A linha vertical marca o limiar escolhido. F2 dá o dobro de peso ao recall.",
        )
        st.plotly_chart(
            charts.threshold_curves(data.threshold_curve(), threshold),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source("Fonte: 05_casos_para_investigar.csv. Reclassificação dos 352 cestos do holdout.")

    with st.expander("Ver as estratégias de limiar da versão revisada (v2)"):
        st.caption(
            "Esta tabela é da versão revisada, que removeu três atributos com suspeita de disponibilidade tardia. "
            "O explorador acima usa os scores do ensemble original; as duas escalas não são idênticas."
        )
        limiares = data.threshold_comparison().copy()
        limiares = limiares.rename(
            columns={
                "Estratégia": "Estratégia",
                "Limiar": "Limiar",
                "Precisão teste": "Precisão",
                "Recall teste": "Recall",
                "F2 teste": "F2",
                "Alertas teste": "Alertas",
                "Verdadeiros positivos": "VP",
                "Falsos positivos": "FP",
                "Falsos negativos": "FN",
            }
        )
        st.dataframe(
            limiares,
            width="stretch",
            hide_index=True,
            column_config={
                "Limiar": st.column_config.NumberColumn(format="%.2f"),
                "Precisão": st.column_config.NumberColumn(format="%.3f"),
                "Recall": st.column_config.NumberColumn(format="%.3f"),
                "F2": st.column_config.NumberColumn(format="%.3f"),
            },
        )
        ui.source("Fonte: 11_comparacao_limiares.csv (versão revisada v2). A escolha foi feita na validação; o teste é apenas leitura.")

    ui.section(
        "05",
        "O desempenho é melhor no cesto 2.",
        "O cesto 2 chega com o forno já parcialmente preenchido; o modelo encontra mais sinal. O cesto 1 é mais difícil.",
    )
    by_basket = data.performance_by_basket().copy()
    by_basket["rotulo"] = by_basket["nu_carregamento"].map({1: "Cesto 1", 2: "Cesto 2"})
    st.dataframe(
        by_basket[
            ["rotulo", "n", "eventos", "taxa_eventos", "alertas", "precisao", "recall", "F2", "PR_AUC", "ROC_AUC"]
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "rotulo": "Cesto",
            "n": "Cestos",
            "eventos": "Eventos",
            "taxa_eventos": st.column_config.NumberColumn("Taxa de evento", format="%.3f"),
            "alertas": "Alertas",
            "precisao": st.column_config.NumberColumn("Precisão", format="%.3f"),
            "recall": st.column_config.NumberColumn("Recall", format="%.3f"),
            "F2": st.column_config.NumberColumn("F2", format="%.3f"),
            "PR_AUC": st.column_config.NumberColumn("PR-AUC", format="%.3f"),
            "ROC_AUC": st.column_config.NumberColumn("ROC-AUC", format="%.3f"),
        },
    )
    ui.source("Fonte: 03_desempenho_por_cesto.csv. Limiar 0,45, sem reajuste por segmento.")

    with st.expander("Desempenho mensal no holdout"):
        by_month = data.performance_by_month().copy()
        st.dataframe(
            by_month,
            width="stretch",
            hide_index=True,
            column_config={
                "mes": "Mês",
                "n": "Cestos",
                "eventos": "Eventos",
                "taxa_eventos": st.column_config.NumberColumn("Taxa", format="%.3f"),
                "alertas": "Alertas",
                "precisao": st.column_config.NumberColumn("Precisão", format="%.3f"),
                "recall": st.column_config.NumberColumn("Recall", format="%.3f"),
                "F2": st.column_config.NumberColumn("F2", format="%.3f"),
                "PR_AUC": st.column_config.NumberColumn("PR-AUC", format="%.3f"),
                "ROC_AUC": st.column_config.NumberColumn("ROC-AUC", format="%.3f"),
            },
        )
        st.caption(
            "Agosto/2026 tem apenas 12 cestos e 2 eventos; a métrica do mês é instável e não deve ser lida como tendência."
        )

    ui.section(
        "06",
        "Versões e auditoria: o que ainda precisa ser validado.",
        "O projeto comparou o ensemble original com uma versão revisada, sem três atributos com suspeita de disponibilidade tardia.",
    )
    v2 = data.v2_comparison().copy()
    st.dataframe(
        v2,
        width="stretch",
        hide_index=True,
        column_config={
            "Modelo": "Modelo",
            "Limiar": st.column_config.NumberColumn("Limiar", format="%.3f"),
            "PR-AUC": st.column_config.NumberColumn("PR-AUC", format="%.3f"),
            "ROC-AUC": st.column_config.NumberColumn("ROC-AUC", format="%.3f"),
            "Precisão": st.column_config.NumberColumn("Precisão", format="%.3f"),
            "Recall": st.column_config.NumberColumn("Recall", format="%.3f"),
            "F2": st.column_config.NumberColumn("F2", format="%.3f"),
            "Balanced Accuracy": st.column_config.NumberColumn("Balanced accuracy", format="%.3f"),
        },
    )
    ui.source(
        "Fonte: 10_comparacao_ensemble_original_vs_v2.csv. A versão revisada remove rendimento_efetivo, "
        "energia_especifica e duracao_montagem_min; o limiar 0,205 foi escolhido na validação."
    )
    ui.callout(
        "A versão revisada mantém PR-AUC semelhante, mas com muito mais alertas (recall 96,5% e 264 falsos positivos). "
        "Ela ilustra o trade-off: mais sensibilidade, mais checagem no pátio. A decisão depende do custo operacional.",
        kind="amber",
        title="O que a comparação mostra",
    )

    audit = data.feature_audit()
    suspeitas = audit.loc[audit["suspeita_de_vazamento"].astype(str).str.lower() == "true"]
    with st.expander("Auditoria de features: as 3 variáveis sob suspeita"):
        st.dataframe(
            suspeitas[["feature", "motivo", "acao"]],
            width="stretch",
            hide_index=True,
            column_config={"feature": "Atributo", "motivo": "Motivo", "acao": "Ação"},
        )
        st.caption(
            "A ausência de sinalização automática não comprova ausência de vazamento. A disponibilidade "
            "no momento do fechamento da balança precisa ser confirmada com a operação."
        )

    ui.section(
        "07",
        "O modelo combina quatro famílias de sinal.",
        "A seleção parte de dezenas de atributos físicos. O que entra no ensemble final precisa ser confirmado quanto à disponibilidade antes do despejo.",
    )
    cols = st.columns(4, gap="small")
    families = [
        ("Massa, volume e densidade", "Peso total, volume estimado, densidade efetiva e variação entre camadas."),
        ("Composição", "Proporção de leve, misto e pesado; participação dos materiais mais frequentes."),
        ("Ordem das camadas", "Base, meio e topo; posição média das classes; violações da regra leve–pesado–leve."),
        ("Contexto", "Cesto 1 ou 2, turno, dia da semana e feriado nacional."),
    ]
    for col, (title, text) in zip(cols, families):
        with col:
            ui.render_html(
                f"""
                <div class="nav-card" style="min-height:170px;">
                    <div class="nav-kicker">Família</div>
                    <div class="nav-title" style="font-size:1.05rem;">{title}</div>
                    <div class="nav-text">{text}</div>
                </div>
                """
            )

    ui.source(
        "Fonte: notebook de modelagem, auditoria de features e relatórios complementares. "
        "O app não reajusta o modelo; as métricas são as do holdout reportado."
    )
