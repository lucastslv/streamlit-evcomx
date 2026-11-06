"""Negócio e piloto: valor, semáforo, monitoramento e decisão."""

from __future__ import annotations

import streamlit as st

from .. import charts, config, data, ui


def _br(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render() -> None:
    m45 = data.threshold_metrics(0.45)
    scenarios = data.business_scenarios()
    base = scenarios.loc[scenarios["cenario"] == "Base"].iloc[0]
    cenario_min = scenarios["modelo"].min()
    cenario_max = scenarios["modelo"].max()
    reducao_fp = (291 - m45["fp"]) / 291
    ui.hero(
        "NEGÓCIO & PILOTO",
        f"O piloto vale R$ {base['modelo']:.1f} mi por ano no cenário base.".replace(".", ","),
        "O modelo não fecha a tampa do forno. Ele compra tempo para o pátio agir. O valor está nos minutos "
        "de parada evitados, descontado o custo de checar os alarmes.",
        f"Faixa de R$ {cenario_min:.1f} a {cenario_max:.1f} mi por ano · premissas de custo a validar com a empresa".replace(".", ","),
    )

    ui.kpi_row(
        [
            {"value": f"{m45['vp_min_share']:.0%}", "label": "do tempo de parada antecipado", "note": f"{_br(m45['vp_min'])} de {_br(m45['total_min'])} min no holdout", "tone": "green"},
            {"value": f"−{reducao_fp:.0%}", "label": "alarmes falsos vs. regra por volume", "note": f"{m45['fp']} contra 291 no teste", "tone": "blue"},
            {"value": f"R$ {base['modelo']:.1f} mi".replace(".", ","), "label": "ganho líquido anual (base)", "note": "R$ 2.000 por minuto de forno parado", "tone": "green"},
            {"value": "8 semanas", "label": "piloto proposto no pátio", "note": "alerta, ação e comparação com e sem ação", "tone": "amber"},
        ]
    )

    ui.section(
        "01",
        "O valor depende de três premissas.",
        "Taxa de sucesso da ação no pátio, custo do minuto parado e custo de checar um alarme falso. O cenário base é o centro da faixa.",
    )
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        ui.chart_header(
            "O ensemble supera a regra por volume no cenário conservador",
            "Ganho líquido anualizado, já descontando a checagem dos alarmes falsos. Barras abaixo de zero são prejuízo.",
        )
        st.plotly_chart(
            charts.business_bars(scenarios),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source("Fonte: notebook de modelagem e apresentação final. Premissas de custo a validar com a empresa.")
    with right:
        compact = scenarios[["cenario", "sucesso", "custo_min", "minutos"]].copy()
        compact["sucesso"] = (compact["sucesso"] * 100).round(0).astype(int).astype(str) + "%"
        compact["custo_min"] = compact["custo_min"].map(lambda x: f"R$ {x:,.0f}".replace(",", "."))
        compact["minutos"] = compact["minutos"].map(lambda x: f"{x:,.0f}".replace(",", "."))
        compact = compact.rename(
            columns={
                "cenario": "Cenário",
                "sucesso": "Sucesso",
                "custo_min": "Minuto",
                "minutos": "Min./ano",
            }
        )
        st.dataframe(compact, width="stretch", hide_index=True)
        st.caption(
            "O ganho do ensemble já desconta 0,2 a 0,5 min de checagem por alarme falso. "
            "A regra por volume alerta quase todos os cestos e só ganha no cenário otimista."
        )
        with st.expander("Ver a tabela completa, com as duas abordagens"):
            full = scenarios.copy()
            full["sucesso"] = (full["sucesso"] * 100).round(0).astype(int).astype(str) + "%"
            full["custo_min"] = full["custo_min"].map(lambda x: f"R$ {x:,.0f}".replace(",", "."))
            full["minutos"] = full["minutos"].map(lambda x: f"{x:,.0f}".replace(",", "."))
            full["modelo"] = full["modelo"].map(lambda x: f"R$ {x:+.1f} mi".replace(".", ","))
            full["regra_volume"] = full["regra_volume"].map(lambda x: f"R$ {x:+.1f} mi".replace(".", ","))
            full = full.rename(
                columns={
                    "cenario": "Cenário",
                    "sucesso": "Sucesso da ação",
                    "custo_min": "Minuto parado",
                    "minutos": "Minutos ganhos/ano",
                    "modelo": "Ensemble",
                    "regra_volume": "Regra por volume",
                }
            )
            st.dataframe(full, width="stretch", hide_index=True)

    ui.section(
        "02",
        "O semáforo transforma o score em ação.",
        "Os cortes são 30% e 45% no ensemble oficial. A ação é diferente para cada faixa — e o custo do alarme falso é assumido.",
    )
    ui.semaforo_cards()
    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        ui.chart_header(
            "No holdout, o vermelho concentra os eventos",
            "Distribuição dos 352 cestos pelos cortes 30%/45% e taxa de evento observada em cada faixa.",
        )
        st.plotly_chart(
            charts.band_stacked(data.band_stats()),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source(
            "Fonte: 05_casos_para_investigar.csv. A distribuição por faixa depende do limiar e da versão do score."
        )
    with right:
        bands = data.band_stats().copy()
        red_rate = float(bands.loc[bands["banda"] == "vermelho", "taxa"].iloc[0])
        green_rate = float(bands.loc[bands["banda"] == "verde", "taxa"].iloc[0])
        bands["taxa"] = bands["taxa"].map(lambda x: f"{x*100:.1f}".replace(".", ","))
        st.dataframe(
            bands.rename(columns={"banda": "Faixa", "n": "Cestos", "eventos": "Eventos", "taxa": "Taxa de evento (%)"}),
            width="stretch",
            hide_index=True,
        )
        st.caption(
            f"O vermelho tem {_br(red_rate * 100)}% de evento no holdout; o verde, {_br(green_rate * 100)}%. "
            "O amarelo fica no meio. A taxa não é uma garantia individual: é a frequência observada na faixa."
        )

    ui.section(
        "03",
        "O piloto de 8 semanas é o teste que falta.",
        "O modelo estima risco; a ação no pátio é uma hipótese. Só o piloto mostra se agir no vermelho reduz a parada.",
    )
    steps = [
        ("Semanas 1–2", "Ligar o semáforo à balança", "Só como aviso. Registrar o que o modelo recomendou e o que o pátio fez."),
        ("Semanas 3–6", "Agir nos cestos vermelhos", "Compactar o topo ou adicionar 2–3 t de pesado. Registrar a ação e o tempo gasto."),
        ("Semanas 7–8", "Comparar com e sem ação", "Paradas nos cestos vermelhos, alarmes falsos por turno e tempo de checagem."),
        ("Decisão", "Manter, ajustar ou encerrar", "Com dados do piloto, revisar limiar, ação e custo. Só então escalar."),
    ]
    cols = st.columns(4, gap="small")
    for col, (period, title, text) in zip(cols, steps):
        with col:
            ui.render_html(
                f"""
                <div class="nav-card" style="min-height:190px;">
                    <div class="nav-kicker">{period}</div>
                    <div class="nav-title" style="font-size:1.02rem;">{title}</div>
                    <div class="nav-text">{text}</div>
                </div>
                """
            )
    ui.source("Fonte: plano de implantação proposto no projeto. Prazos e responsáveis são uma proposta a ajustar com a empresa.")

    ui.section(
        "04",
        "O que pode mudar o resultado.",
        "Três riscos precisam estar no painel de monitoramento desde o primeiro dia.",
    )
    drift = data.drift_table()
    if not drift.empty:
        pesado = drift.loc[drift["Atributo"] == "prop_pesado"].iloc[0]
        pesado_treino = float(pesado["Mediana (Treino)"]) * 100
        pesado_teste = float(pesado["Mediana (Teste)"]) * 100
    else:
        pesado_treino, pesado_teste = 31.3, 20.3
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown("#### A receita muda")
        st.markdown(
            f"A proporção de sucata pesada caiu de **{_br(pesado_treino)}%** no treino para "
            f"**{_br(pesado_teste)}%** no teste. O modelo perdeu desempenho fora do tempo. "
            "Monitorar a composição mensal e retreinar."
        )
        ui.kpi_row(
            [
                {"value": f"−{_br(pesado_treino - pesado_teste)} p.p.", "label": "de pesado no período recente", "note": f"{_br(pesado_treino)}% → {_br(pesado_teste)}%", "tone": "red"},
            ]
        )
    with c2:
        st.markdown("#### Alarmes falsos")
        st.markdown(
            f"No limiar 0,45, **{m45['fp']} de {m45['alerts']} alertas** não eram evento. Cada checagem custa tempo. "
            "Medir alertas por turno e o tempo real de checagem no piloto."
        )
    with c3:
        st.markdown("#### Causalidade não provada")
        st.markdown(
            f"O modelo encontra associação. **{m45['fn'] / m45['eventos'] * 10:.0f} de cada 10** cargas altas passam sem aviso. "
            "Só o piloto confirma se a ação no pátio evita a parada."
        )

    with st.expander("Limitações e o que o modelo não faz"):
        st.markdown(
            """
            - **Associação, não causalidade.** O modelo estima risco condicional; não prova que mudar a receita evita o evento.
            - **Densidade de catálogo.** A densidade é uma média estática por material e não captura geometria de peças longas ou retorcidas.
            - **Cesto 2 subnotificado.** 97 corridas não têm camadas do cesto 2; o missing é não aleatório.
            - **Mudança de receita.** O desempenho no teste futuro é menor que na validação cruzada; retreino mensal é parte do plano.
            - **Limiar é decisão.** O ponto 0,45 privilegia recall; o custo de cada erro precisa ser validado.
            - **Disponibilidade dos atributos.** Três features têm suspeita de informação tardia e precisam de confirmação operacional.
            """
        )
        ui.source("Fonte: relatórios complementares, notebook de modelagem e apresentação final.")

    ui.section(
        "05",
        "O custo financeiro, linha a linha.",
        "A conta do notebook: custo histórico sem alertas contra o custo residual com o ensemble. "
        "VP paga a parcela não evitada; FN paga a parada inteira; FP paga a checagem.",
    )
    custo = data.financial_cost()
    if not custo.empty:
        base_cost = custo.loc[custo["Cenario"].str.contains("Base", na=False)].iloc[0]
        show_cost = custo[
            [
                "Cenario",
                "Custo sem alertas (R$)",
                "Custo residual dos VP (R$)",
                "Custo integral dos FN (R$)",
                "Custo dos FP (R$)",
                "CUSTO TOTAL com Ensemble (R$)",
                "Economia liquida simulada (R$)",
                "Economia anual projetada x12 (R$)",
            ]
        ].copy()
        for col in show_cost.columns[1:]:
            show_cost[col] = show_cost[col].map(lambda x: f"R$ {x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.dataframe(
            show_cost.rename(
                columns={
                    "Cenario": "Cenário",
                    "Custo sem alertas (R$)": "Sem alertas",
                    "Custo residual dos VP (R$)": "VP residual",
                    "Custo integral dos FN (R$)": "FN integral",
                    "Custo dos FP (R$)": "FP (checagem)",
                    "CUSTO TOTAL com Ensemble (R$)": "Com ensemble",
                    "Economia liquida simulada (R$)": "Economia/mês",
                    "Economia anual projetada x12 (R$)": "Economia/ano",
                }
            ),
            width="stretch",
            hide_index=True,
        )
        ui.callout(
            f"No cenário base, o custo sem alertas seria <strong>{show_cost.loc[base_cost.name, 'Custo sem alertas (R$)']}</strong>; "
            f"com o ensemble, <strong>{show_cost.loc[base_cost.name, 'CUSTO TOTAL com Ensemble (R$)']}</strong>. "
            f"A economia simulada é de <strong>{show_cost.loc[base_cost.name, 'Economia liquida simulada (R$)']}</strong> "
            f"por mês, ou <strong>{show_cost.loc[base_cost.name, 'Economia anual projetada x12 (R$)']}</strong> por ano. "
            "São hipóteses de eficácia e custo, não economia observada.",
            kind="green",
            title="A conta do cenário base",
        )
    ui.source(
        "Fonte: 12_custo_financeiro.csv. Anualização ×12 sem sazonalidade; premissas de sucesso e de checagem "
        "são hipóteses do projeto."
    )

    ui.section(
        "06",
        "O que precisa ser decidido.",
        "O pedido é um piloto, não uma implantação definitiva.",
    )
    asks = [
        ("1", "Aprovar o piloto", "8 semanas no pátio de metálicos, com o semáforo como aviso e ação nos vermelhos."),
        ("2", "Definir responsáveis", "Proposta: gerência do pátio como dona do piloto; analista de dados na leitura semanal."),
        ("3", "Validar o custo", "R$ 2.000/min como premissa; 0,2 a 0,5 min de checagem por alarme falso."),
    ]
    cols = st.columns(3, gap="large")
    for col, (num, title, text) in zip(cols, asks):
        with col:
            ui.render_html(
                f"""
                <div class="nav-card" style="min-height:160px;">
                    <div class="nav-kicker">Pedido {num}</div>
                    <div class="nav-title">{title}</div>
                    <div class="nav-text">{text}</div>
                </div>
                """
            )

    ui.callout(
        "Proposta do grupo: <strong>gerência do pátio</strong> como dona do piloto, <strong>analista de dados</strong> na leitura semanal, "
        "<strong>8 semanas</strong> e custo de checagem de <strong>0,2 a 0,5 min por alarme falso</strong>. O valor do minuto parado "
        "e o acesso à balança precisam ser confirmados pela empresa.",
        kind="red",
        title="Governança proposta",
    )
    ui.source(
        "Fontes: apresentação final, notebook de modelagem e relatórios complementares. "
        "Valores financeiros são premissas do projeto, não medições contábeis."
    )
