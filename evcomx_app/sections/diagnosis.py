"""Diagnóstico: frequência, duração, composição e qualidade dos dados."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .. import charts, config, data, ui


def _br(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render() -> None:
    s = data.summary()
    profiles = data.basket_profiles()
    ui.hero(
        "DIAGNÓSTICO · EDA",
        "Três em cada dez corridas param o forno — e a composição ajuda a explicar.",
        "Frequência, duração e composição dos cestos. Uma leitura observacional para formular hipóteses — "
        "não para provar causalidade.",
        "1.799 corridas · 43.405 camadas · ago/2025 a ago/2026",
    )

    ui.kpi_row(
        [
            {"value": f"{s['n_eventos']}", "label": "corridas com carga alta", "note": f"{s['taxa_evento']:.1%} da amostra".replace(".", ","), "tone": "red"},
            {"value": f"{s['horas_paradas']:.1f} h".replace(".", ","), "label": "de forno parado", "note": "soma do tempo de parada registrado", "tone": "red"},
            {"value": f"{s['parada_mediana_min']:.1f} min".replace(".", ","), "label": "parada mediana", "note": "entre as corridas afetadas", "tone": "amber"},
            {"value": f"{s['parada_p95_min']:.1f} min".replace(".", ","), "label": "95% das paradas até aqui", "note": f"máximo observado: {s['parada_max_min']:.1f} min".replace(".", ","), "tone": "amber"},
        ]
    )

    ui.section(
        "01",
        "A taxa fica perto de 30% e é estável no período.",
        "As pontas da série são meses parciais e devem ser lidas com cautela.",
    )
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        ui.chart_header(
            "A taxa mensal de carga alta fica perto de 30%",
            "Linha: taxa mensal. Faixa: intervalo de confiança de 95% (Wilson).",
        )
        st.plotly_chart(
            charts.monthly_rate(data.load_taxas()),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source("Fonte: VariavelResposta.csv. Meses de ago/2025 e ago/2026 são parciais na extração.")
    with right:
        ui.chart_header(
            "As paradas são curtas na maioria das vezes",
            "Distribuição do tempo de parada entre as 541 corridas afetadas.",
        )
        st.plotly_chart(
            charts.downtime_hist(data.load_response()),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source("Fonte: VariavelResposta.csv. Mediana de 3,0 min; 95% das corridas até 11,9 min.")

    left, right = st.columns([1, 1], gap="large")
    with left:
        ui.chart_header("Junho concentra o maior tempo de forno parado da amostra.")
        st.plotly_chart(
            charts.monthly_downtime(data.load_taxas()),
            width="stretch",
            config={"displayModeBar": False},
        )
    with right:
        ui.callout(
            "A carga alta não é um evento raro: 541 corridas e <strong>36,8 horas</strong> de forno parado. "
            "A mediana é curta, mas a cauda chega a 20,7 minutos. É essa cauda que o alerta tenta antecipar.",
            kind="red",
            title="Por que isso importa",
        )
        ui.callout(
            "A taxa mensal é descritiva. Receita, mix de sucata e cobertura da extração podem explicar "
            "variações entre meses; não há teste confirmatório nesta etapa.",
            kind="amber",
            title="Leitura honesta",
        )

    ui.section(
        "02",
        "Cesto 1 e cesto 2 são processos diferentes.",
        "O cesto 1 é maior e mais pesado; o cesto 2 entra no forno já parcialmente preenchido. Comparar os dois juntos esconde essa diferença.",
    )
    cols = st.columns(3, gap="large")
    with cols[0]:
        ui.chart_header("Massa mediana", "toneladas por cesto")
        st.plotly_chart(
            charts.bar_pair(profiles, "massa", label="massa", y_title="toneladas", color=config.BLUE),
            width="stretch",
            config={"displayModeBar": False},
        )
    with cols[1]:
        ui.chart_header("Volume estimado", "massa / densidade de catálogo")
        st.plotly_chart(
            charts.bar_pair(profiles, "volume", label="volume", y_title="m³", color=config.BLUE),
            width="stretch",
            config={"displayModeBar": False},
        )
    with cols[2]:
        ui.chart_header("Camadas ativas", "mediana por cesto")
        st.plotly_chart(
            charts.bar_pair(profiles, "camadas", label="camadas", y_title="camadas", color=config.BLUE),
            width="stretch",
            config={"displayModeBar": False},
        )
    ui.source("Fonte: dataset_carregamentos.csv. Medianas dos cestos com composição registrada; volume é estimado, não medido.")

    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        ui.chart_header(
            "O volume mediano é quase o mesmo com e sem carga alta.",
            "Volume estimado mediano por cesto e presença de evento. Barras cinza: sem evento; vermelhas: com evento.",
        )
        st.plotly_chart(
            charts.volume_by_event(data.volume_by_event()),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source("Fonte: dataset_carregamentos.csv. Volume = soma de massa / densidade de catálogo.")
    with right:
        ui.render_html(
            f"""
            <div style="padding-top:1.2rem;">
            <p style="font-family:'Source Serif 4',Georgia,serif;font-size:1.15rem;line-height:1.45;">
            O volume mediano é praticamente o mesmo com e sem carga alta. A diferença aparece na
            <strong>composição</strong> e na <strong>densidade efetiva</strong>.</p>
            <p style="color:#6E685D;font-size:0.9rem;line-height:1.65;">
            No cesto 2, a mediana de pesado cai de 24,1% para 15,0% quando há evento.
            No cesto 1, a queda é menor: de 32,1% para 29,0%. Isso é associação, não prova de que mudar a receita reduz o evento.
            </p>
            </div>
            """
        )
        ui.callout(
            "O guia do projeto já alertava: o volume é uma hipótese, não uma conclusão. A análise "
            "mostra que ele sozinho não separa os grupos.",
            kind="amber",
            title="O que não funciona",
        )

    ui.chart_header(
        "Pesado e densidade andam mais junto com a carga alta do que o volume.",
        "Correlação ponto-bisserial com o evento do mesmo carregamento. Valores negativos indicam que a característica tende a ser menor nos eventos.",
    )
    st.plotly_chart(
        charts.association_bars(data.load_associacoes()),
        width="stretch",
        config={"displayModeBar": False},
    )
    ui.source(
        "Fonte: associacoes_carregamentos.csv. Correlação sem ajuste por massa, receita ou período; "
        "cestos da mesma corrida não são independentes."
    )

    ui.section(
        "03",
        "Corridas sem o cesto 2 registrado têm mais carga alta.",
        "O missing não é aleatório: 97 corridas não têm camadas do cesto 2. Sete delas tiveram evento no próprio cesto 2.",
    )
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        ui.chart_header(
            "51,5% de evento quando o cesto 2 não aparece",
            "Barras: taxa de carga alta por corrida. Traços: intervalo de confiança de 95% (Wilson).",
        )
        st.plotly_chart(
            charts.missing_c2(data.missing_c2()),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source("Fonte: VariavelResposta.csv + dataset_modelagem.csv.")
    with right:
        ui.render_html(
            """
            <div style="padding-top:1.3rem;">
            <p style="font-family:'Source Serif 4',Georgia,serif;font-size:1.3rem;line-height:1.4;">
            O missing do cesto 2 é um sinal operacional, não um detalhe de planilha.</p>
            <p style="color:#6E685D;font-size:0.9rem;line-height:1.65;">
            Corridas com dois cestos registrados têm 28,8% de evento (491 de 1.702). Sem o registro do cesto 2,
            a taxa sobe para 51,5% (50 de 97). Parte disso pode refletir operação com cesto único e mais gusa líquido;
            o dado não permite separar causas.
            </p>
            </div>
            """
        )
        ui.callout(
            "Antes de operacionalizar o modelo, é preciso definir como tratar cestos ausentes e confirmar "
            "se a ausência é operacional ou falha de registro.",
            kind="blue",
            title="Próximo passo",
        )

    ui.section(
        "04",
        "A base é boa, mas tem arestas conhecidas.",
        "Nenhum tratamento foi escondido: os pontos abaixo afetam a leitura e devem entrar no piloto.",
    )
    q = data.data_quality()
    st.dataframe(
        q,
        width="stretch",
        hide_index=True,
        column_config={
            "checagem": st.column_config.TextColumn("Checagem", width="medium"),
            "resultado": st.column_config.TextColumn("Resultado", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "leitura": st.column_config.TextColumn("Leitura", width="large"),
        },
    )
    ui.source("Fonte: bases brutas e enriquecidas; relatório preliminar de EDA e auditoria de features.")

    with st.expander("Apêndice · calendário externo e materiais"):
        left, right = st.columns([1, 1], gap="large")
        with left:
            ui.chart_header(
                "Datas do calendário sugerem uma hipótese, não um efeito",
                "Taxa de carga alta por corrida em datas do calendário vs. demais dias.",
            )
            st.plotly_chart(
                charts.holiday_bars(data.holiday_rates()),
                width="stretch",
                config={"displayModeBar": False},
            )
            ui.source("Fonte: BrasilAPI 2025/2026 + horários do cesto 1. Fuso a confirmar; calendário não é escala da planta.")
        with right:
            ui.chart_header("Materiais mais frequentes nas camadas")
            top = data.top_materials().copy()
            top["rotulo"] = top["material_code"].astype(str)
            st.dataframe(
                top[["rotulo", "ds_descricao_material", "camadas"]],
                width="stretch",
                hide_index=True,
                column_config={
                    "rotulo": "Código",
                    "ds_descricao_material": "Descrição",
                    "camadas": st.column_config.NumberColumn("Camadas", format="%d"),
                },
            )
            ui.source("Fonte: camadas_clean_enriched.csv. 21 códigos observados; materiais raros exigem cautela.")
