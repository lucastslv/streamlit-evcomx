"""Visão geral: o problema, a tese e o que o holdout mostra."""

from __future__ import annotations

import streamlit as st

from .. import charts, config, data, ui


def _go(section_key: str) -> None:
    """Callback: mantém o rádio da sidebar sincronizado com o atalho."""
    label = config.SECTION_LABELS[section_key]
    st.session_state.section = label
    st.session_state.nav_widget = label


def _go_demo() -> None:
    _go("simulator")
    st.session_state.sim_demo_open = True


def _br(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render() -> None:
    s = data.summary()
    m45 = data.threshold_metrics(0.45)
    scenarios = data.business_scenarios()
    base = scenarios.loc[scenarios["cenario"] == "Base"].iloc[0]
    cenario_min = scenarios["modelo"].min()
    cenario_max = scenarios["modelo"].max()
    horas = f"{s['horas_paradas']:.1f}".replace(".", ",")
    mediana = f"{s['parada_mediana_min']:.1f}".replace(".", ",")
    ui.hero(
        "EVCOMX · MODELAGEM PREDITIVA",
        "A carga alta avisa antes de parar o forno.",
        "Um modelo que lê a composição do cestão de sucata e estima o risco antes do despejo — "
        "para o pátio agir em minutos, não depois.",
        f"{s['n_corridas']:,} corridas · {s['n_cestos']:,} cestos com composição · "
        f"{s['periodo_inicio']} a {s['periodo_fim']} · leitura observacional".replace(",", "."),
        variant="cover",
    )

    ui.kpi_row(
        [
            {
                "value": "3 em 10",
                "label": "corridas tiveram carga alta",
                "note": f"{s['n_eventos']} de {s['n_corridas']:,} corridas na amostra".replace(",", "."),
                "tone": "red",
            },
            {
                "value": f"{horas} h",
                "label": "de forno parado no período",
                "note": f"mediana de {mediana} min por corrida afetada",
                "tone": "red",
            },
            {
                "value": f"{m45['recall'] * 10:.0f} em 10",
                "label": "cargas altas avisadas antes do despejo",
                "note": f"{m45['vp']} de {m45['eventos']} eventos no holdout; {m45['recall']:.1%} de recall com limiar 0,45".replace(".", ","),
                "tone": "blue",
            },
            {
                "value": f"R$ {base['modelo']:.1f} mi".replace(".", ","),
                "label": "ganho líquido por ano",
                "note": f"cenário base; faixa de R$ {cenario_min:.1f} a {cenario_max:.1f} mi por ano".replace(".", ","),
                "tone": "green",
            },
        ]
    )

    ui.source(
        f"Os três números-âncora: <strong>3 em 10</strong> corridas · "
        f"<strong>{m45['recall'] * 10:.0f} em 10</strong> cargas altas avisadas · "
        f"<strong>R$ {base['modelo']:.1f} mi</strong> por ano no cenário base.".replace(".", ",")
    )
    ui.callout(
        "Aprovar um <strong>piloto de 8 semanas</strong> no pátio de metálicos, com o semáforo como aviso e ação nos cestos vermelhos. "
        "Dono, custo e acesso aos dados da balança precisam ser definidos com a empresa.",
        kind="red",
        title="O pedido",
    )
    b1, b2 = st.columns([1, 1])
    with b1:
        st.button(
            "Ver o plano do piloto →",
            key="ov_business",
            on_click=_go,
            args=("business",),
        )
    with b2:
        st.button(
            "Abrir demo de 2 minutos →",
            key="ov_demo",
            on_click=_go_demo,
        )

    ui.section(
        "01",
        "O problema em 30 segundos",
        "A decisão acontece no pátio, antes do cestão chegar ao forno. O app traduz a física do processo em uma leitura de risco.",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### O forno")
        st.markdown(
            "O forno elétrico a arco recebe sucata no cestão. Quando a carga é alta, a tampa não fecha "
            "e a operação injeta oxigênio para queimar material: são minutos de forno aberto."
        )
    with c2:
        st.markdown("#### O cestão")
        st.markdown(
            "Cada corrida tem até dois cestos sólidos. O cesto 2 encontra o forno já parcialmente preenchido "
            "e tem uma taxa de evento maior. Cada cesto é uma decisão separada."
        )
    with c3:
        st.markdown("#### O alerta")
        st.markdown(
            "No fechamento da balança, pesos, camadas e composição já estão registrados. O modelo estima "
            "o risco e aciona o semáforo antes da ponte rolante."
        )

    ui.callout(
        "A pergunta não é só “quanto espaço a carga ocupa”. É <strong>como a carga está composta e acomodada</strong>. "
        "O volume mediano quase não diferencia os grupos; a proporção de material pesado, sim.",
        kind="red",
        title="A tese",
    )

    ui.section(
        "02",
        "A composição pesa mais que o volume",
        "Mediana da participação de material pesado na massa do cestão. Cestos com carga alta têm menos material pesado — especialmente no cesto 2.",
    )
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        ui.chart_header(
            "Cestos com carga alta são menos compactados por material pesado",
            "Cada barra é a mediana do grupo; o número de cestos aparece no hover.",
        )
        st.plotly_chart(
            charts.heavy_by_event(data.heavy_by_event()),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source("Fonte: infos_camadas + cadastro de materiais. Associação observada; não prova causalidade.")
    with right:
        ui.render_html(
            """
            <div style="padding-top:1.4rem;">
            <p style="font-family:Arial,'Liberation Sans',sans-serif;font-size:1.35rem;line-height:1.35;">
            <strong>−3,1 p.p.</strong> no cesto 1.<br>
            <strong>−9,1 p.p.</strong> no cesto 2.</p>
            <p style="color:var(--muted);font-size:0.9rem;line-height:1.6;">
            A diferença é maior no segundo cesto. O volume mediano, por outro lado, fica quase igual:
            +0,6 m³ no cesto 1 e −0,1 m³ no cesto 2.
            </p>
            <p style="color:var(--muted);font-size:0.9rem;line-height:1.6;">
            É essa combinação — massa, densidade, proporção de classes e ordem das camadas — que o modelo usa.
            </p>
            </div>
            """
        )
        st.button(
            "Ver o diagnóstico completo →",
            key="ov_diag",
            on_click=_go,
            args=("diagnosis",),
        )

    ui.section(
        "03",
        "O que o holdout mostra",
        "O teste usa as 180 corridas mais recentes, que o modelo nunca viu. O limiar operacional é 0,45.",
    )
    m = m45
    mcols = st.columns(4)
    metrics = [
        ("Recall", f"{m['recall']:.1%}".replace(".", ","), "cargas altas avisadas"),
        ("Precisão", f"{m['precision']:.1%}".replace(".", ","), "alertas que eram evento"),
        ("PR-AUC", _br(m["pr_auc"], 3), f"vs. {_br(m['prevalencia'], 3)} de prevalência"),
        ("ROC-AUC", _br(m["roc_auc"], 3), "capacidade de separação"),
    ]
    for col, (label, value, note) in zip(mcols, metrics):
        with col:
            ui.kpi_row([{"value": value, "label": label, "note": note, "tone": "blue"}])

    left, right = st.columns([0.9, 1.1], gap="large")
    with left:
        ui.chart_header("A matriz de confusão do teste", "352 cestos; 57 eventos reais.")
        ui.confusion_matrix(m["tn"], m["fp"], m["fn"], m["vp"])
        ui.render_html(
            f"<p style='font-size:0.82rem;color:var(--muted);line-height:1.55;'>"
            f"O modelo avisou <strong>{m['vp']} de {m['eventos']} eventos</strong> e antecipou "
            f"<strong>{m['vp_min_share']:.0%} de todo o tempo de parada</strong> "
            f"({_br(m['vp_min'])} de {_br(m['total_min'])} min). "
            f"Os {m['fp']} alarmes falsos são o custo operacional do alerta.</p>"
        )
    with right:
        ui.chart_header(
            "A curva de precisão-recall",
            "Quanto mais alertas, maior o recall e menor a precisão. A escolha do limiar é uma decisão operacional.",
        )
        st.plotly_chart(
            charts.pr_curve(data.pr_curve(), ap=m["pr_auc"]),
            width="stretch",
            config={"displayModeBar": False},
        )
        ui.source(
            f"Fonte: 05_casos_para_investigar.csv (holdout de 352 cestos). PR-AUC = {_br(m['pr_auc'], 3)}."
        )
        st.button(
            "Explorar o modelo e o limiar →",
            key="ov_model",
            on_click=_go,
            args=("model",),
        )

    ui.section("04", "Continue a leitura")
    cards = [
        ("01", "Diagnóstico", "Frequência, duração e composição. O que os dados mostram — e o que não mostram.", "diagnosis"),
        ("02", "Modelo", "Split cronológico, atributos, curvas e a comparação entre versões.", "model"),
        ("03", "Erros & casos", "Quem são os falsos positivos e falsos negativos. Casos reais para investigar.", "errors"),
        ("04", "Simulador", "Monte ou edite um cestão e veja o risco se mover com a composição.", "simulator"),
        ("05", "Negócio & piloto", "Quanto vale, o que monitorar e o que precisa ser decidido.", "business"),
    ]
    cols = st.columns(5, gap="small")
    for col, (num, title, text, key) in zip(cols, cards):
        with col:
            ui.render_html(
                f"""
                <div class="nav-card">
                    <div class="nav-kicker">{num}</div>
                    <div class="nav-title">{title}</div>
                    <div class="nav-text">{text}</div>
                </div>
                """
            )
            st.button(
                "Abrir",
                key=f"nav_{key}",
                width="stretch",
                on_click=_go,
                args=(key,),
            )

    ui.source(
        "Fontes: VariavelResposta.csv, infos_camadas.csv, infos_materiais.csv, dataset_modelagem.csv; "
        "relatórios complementares do projeto. O app é uma leitura dos dados e não substitui validação operacional."
    )
