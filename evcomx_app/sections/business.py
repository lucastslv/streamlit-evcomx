"""Negócio e piloto: valor, semáforo, monitoramento e decisão."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .. import charts, config, data, ui


def render() -> None:
    ui.hero(
        "NEGÓCIO & PILOTO",
        "O piloto vale R$ 1,4 mi por ano no cenário base.",
        "O modelo não fecha a tampa do forno. Ele compra tempo para o pátio agir. O valor está nos minutos "
        "de parada evitados, descontado o custo de checar os alarmes.",
        "Faixa de R$ 0,3 a 2,6 mi por ano · premissas de custo a validar com a empresa",
    )

    ui.kpi_row(
        [
            {"value": "69%", "label": "do tempo de parada antecipado", "note": "120,8 de 176,3 min no holdout", "tone": "green"},
            {"value": "−67%", "label": "alarmes falsos vs. regra por volume", "note": "95 contra 291 no teste", "tone": "blue"},
            {"value": "R$ 1,4 mi", "label": "ganho líquido anual (base)", "note": "R$ 2.000 por minuto de forno parado", "tone": "green"},
            {"value": "8 semanas", "label": "piloto proposto no pátio", "note": "alerta, ação e comparação com e sem ação", "tone": "amber"},
        ]
    )

    ui.section(
        "01",
        "O valor depende de três premissas.",
        "Taxa de sucesso da ação no pátio, custo do minuto parado e custo de checar um alarme falso. O cenário base é o centro da faixa.",
    )
    scenarios = pd.DataFrame(
        [
            {"cenario": "Conservador", "sucesso": 0.50, "custo_min": 1500, "minutos": 220, "modelo": 0.3, "regra_volume": -1.0},
            {"cenario": "Base", "sucesso": 0.70, "custo_min": 2000, "minutos": 680, "modelo": 1.4, "regra_volume": 0.7},
            {"cenario": "Otimista", "sucesso": 0.85, "custo_min": 2500, "minutos": 1030, "modelo": 2.6, "regra_volume": 2.8},
        ]
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
        bands["taxa"] = bands["taxa"].map(lambda x: f"{x*100:.1f}".replace(".", ","))
        st.dataframe(
            bands.rename(columns={"banda": "Faixa", "n": "Cestos", "eventos": "Eventos", "taxa": "Taxa de evento (%)"}),
            width="stretch",
            hide_index=True,
        )
        st.caption(
            "O vermelho tem 25,8% de evento no holdout; o verde, 4,9%. O amarelo fica no meio. "
            "A taxa não é uma garantia individual: é a frequência observada na faixa."
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
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown("#### A receita muda")
        st.markdown(
            "A proporção de sucata pesada caiu de **31,3%** no treino para **20,3%** no teste. "
            "O modelo perdeu desempenho fora do tempo. Monitorar a composição mensal e retreinar."
        )
        ui.kpi_row(
            [
                {"value": "−11,0 p.p.", "label": "de pesado no período recente", "note": "31,3% → 20,3%", "tone": "red"},
            ]
        )
    with c2:
        st.markdown("#### Alarmes falsos")
        st.markdown(
            "No limiar 0,45, **95 de 128 alertas** não eram evento. Cada checagem custa tempo. "
            "Medir alertas por turno e o tempo real de checagem no piloto."
        )
    with c3:
        st.markdown("#### Causalidade não provada")
        st.markdown(
            "O modelo encontra associação. **Quatro de cada dez** cargas altas passam sem aviso. "
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
