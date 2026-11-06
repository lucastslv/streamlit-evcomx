"""Dados e método: fontes, premissas, reprodutibilidade e limites."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .. import config, data, ui


def render() -> None:
    ui.hero(
        "DADOS & MÉTODO",
        "De onde vêm os números — e o que eles não dizem.",
        "Um mapa das fontes, das premissas e das decisões de modelagem. Tudo que aparece no app pode ser "
        "conferido nos arquivos e notebooks do projeto.",
        "Dados de ago/2025 a ago/2026 · projeto EVCOMX · bootcamp",
    )

    ui.section(
        "01",
        "As fontes.",
        "O app lê as bases brutas, as tabelas processadas da EDA e os relatórios complementares da modelagem.",
    )
    sources = pd.DataFrame(
        [
            ("VariavelResposta.csv", "1.799 × 7", "Evento e tempo de parada por corrida; base do rótulo."),
            ("infos_camadas.csv", "43.405 × 9", "Camadas, materiais, pesos, baias e horários."),
            ("infos_materiais.csv", "30 × 4", "Densidade, energia e rendimento de catálogo."),
            ("dicionario_tipo_material.csv", "24 × 3", "Classe Leve / Misto / Pesado por material."),
            ("dataset_modelagem.csv", "1.799 × 91", "Consolidação por corrida usada na EDA."),
            ("dataset_carregamentos.csv", "3.598 × 31", "Uma linha por cesto; composição e evento do mesmo carregamento."),
            ("05_casos_para_investigar.csv", "352 × 12", "Holdout: score do ensemble, desfecho e perfil físico."),
            ("02_metricas_teste.csv", "1 × 16", "Métricas oficiais no limiar 0,45."),
            ("03_desempenho_por_cesto.csv", "2 × 10", "Recall, precisão e PR-AUC por cesto."),
            ("04_desempenho_mensal.csv", "2 × 10", "Desempenho por mês no holdout."),
            ("06_resumo_erros.csv", "4 × 5", "Resumo de VP, FP, FN e VN."),
            ("07_intervalos_confianca.csv", "5 × 4", "Bootstrap de PR-AUC, ROC-AUC, recall, precisão e F2."),
            ("08_walk_forward.csv", "5 × 5", "Backtesting temporal em cinco blocos."),
            ("09_drift.csv", "5 × 6", "Teste KS de composição entre treino e teste."),
            ("12_custo_financeiro.csv", "3 × 14", "Custo sem alertas, residual e economia simulada."),
            ("13_comparacao_modelos_teste.csv", "9 × 10", "Todos os modelos avaliados no mesmo holdout."),
            ("14_cenarios_negocio.csv", "6 × 8", "Ensemble e regra por volume nos três cenários."),
            ("15 e 16_comparação...", "2 arquivos", "Validação temporal e conjuntos de atributos."),
            ("10 e 11_comparação...", "2 arquivos", "Histórico: ensemble original vs. v2 e estratégias de limiar."),
            ("evcomx_carga_alta_pipeline.joblib", "1,4 MB", "Artefato do ensemble da rodada anterior, preservado."),
        ],
        columns=["Arquivo", "Dimensão", "Uso no app"],
    )
    st.dataframe(sources, width="stretch", hide_index=True)
    ui.source(
        "Caminhos: dados-bootcamp/data/ e projeto-bootcamp/. Os arquivos brutos não foram alterados pelo app."
    )

    ui.section(
        "02",
        "As premissas.",
        "Algumas escolhas são do projeto e precisam ser confirmadas com a operação antes de qualquer implantação.",
    )
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(
            """
            - **Peso em kg** na base bruta; o app apresenta toneladas.
            - **Rendimento em fração**, apesar do nome original “%”.
            - **Densidade em t/m³**; o volume é estimado por massa / densidade de catálogo.
            - **Horários em UTC**; a conversão para America/Sao_Paulo é uma hipótese a confirmar.
            - **Turnos ilustrativos**: 0h–8h, 8h–16h e 16h–24h.
            """
        )
    with c2:
        st.markdown(
            """
            - **Duplicatas**: apenas linhas idênticas foram removidas (2 registros).
            - **Pesos zero** preservados na inspeção; não entram na composição ativa.
            - **Materiais sem densidade** (RECC/RECG) usam a mediana da classe Pesado.
            - **Cestos ausentes** não são imputados; o missing do cesto 2 é tratado como sinal.
            - **Volume** não mede compactação, expansão ou capacidade real do forno.
            """
        )

    ui.section(
        "03",
        "Como o modelo oficial foi validado.",
        "A validação é cronológica e agrupada por corrida. Os dois cestos da mesma corrida ficam juntos.",
    )
    st.markdown(
        """
        - **Split**: 75% das corridas para treino, 15% para validação e 10% para teste (as mais recentes).
        - **Validação cruzada**: `StratifiedGroupKFold` com 5 folds, agrupado por `cd_corrida`.
        - **Seleção**: 74 atributos escolhidos entre 96 candidatas; variância, colinearidade (|r| > 0,85) e relevância univariada só no treino.
        - **Capacidade volumétrica**: P90 do volume no treino vira referência para a razão volume/capacidade do cestão.
        - **Modelo**: `VotingClassifier` soft com regressão logística, gradient boosting e random forest.
        - **Métrica de escolha**: F2, que dá o dobro de peso ao recall. Em operação, perder um evento custa mais que um alarme falso.
        - **Teste**: 180 corridas, 352 cestos e 57 eventos; lido uma única vez.
        """
    )
    ui.source("Fonte: notebook de modelagem e relatórios complementares. As métricas oficiais são as do holdout reportado.")

    ui.section(
        "04",
        "Como o simulador funciona.",
        "O simulador é uma ferramenta separada, para explorar a direção dos sinais. Ele não substitui o ensemble.",
    )
    st.markdown(
        """
        O app reconstrói os atributos físicos a partir das camadas editadas: massa, volume estimado,
        densidade efetiva, proporções de leve/misto/pesado, posição das classes, regras de base–meio–topo
        e contexto do cesto 1. Esses atributos alimentam uma **regressão logística transparente**,
        treinada nos 3.149 cestos fora do holdout.

        A faixa do simulador é **relativa à população**: baixo até o percentil 50, atenção até o 75 e alto acima disso.
        Os cortes 30%/45% do ensemble oficial são outra escala e aparecem na seção Modelo.
        """
    )
    metrics = data.load_simulator_metrics()
    if metrics:
        st.dataframe(
            pd.DataFrame(
                [
                    ("C", metrics.get("C")),
                    ("Cestos de treino", metrics.get("n_train")),
                    ("Cestos de teste", metrics.get("n_test")),
                    ("PR-AUC no holdout", metrics.get("test_pr_auc")),
                    ("ROC-AUC no holdout", metrics.get("test_roc_auc")),
                    ("Brier no holdout", metrics.get("test_brier")),
                ],
                columns=["Métrica do simulador", "Valor"],
            ),
            width="stretch",
            hide_index=True,
        )
        ui.source("Fonte: data/app/simulator_metrics.json. Modelo didático, não o ensemble oficial.")

    ui.section(
        "05",
        "Como reproduzir.",
        "O app é um projeto uv. As bases ficam nos diretórios originais; os artefatos do simulador são gerados por um script.",
    )
    st.code(
        """# na raiz do projeto
uv sync
uv run python scripts/train_simulator.py
uv run streamlit run app.py""",
        language="bash",
    )
    st.caption(
        "Para container e deploy, veja `deploy/README.md`: Docker local, VM com HTTPS via Caddy "
        "e Streamlit Community Cloud."
    )
    st.markdown(
        """
        **Estrutura**
        ```
        app.py
        evcomx_app/
          config.py      caminhos e paleta
          data.py        leitura e métricas
          features.py    engenharia de atributos
          simulator.py   modelo didático e explicabilidade
          charts.py      gráficos Plotly
          ui.py          CSS e componentes editoriais
          sections/      uma seção por página
        scripts/train_simulator.py
        data/app/        features e scores de referência
        models/          modelo didático do simulador
        ```
        """
    )

    ui.section(
        "06",
        "O que o app não faz.",
        "A leitura é honesta sobre o que está fora do escopo.",
    )
    st.markdown(
        """
        - **Não opera o forno.** O app é uma interface de análise e comunicação.
        - **Não prova causalidade.** As associações não mostram que mudar a receita evita a parada.
        - **Não substitui o piloto.** A ação no pátio precisa ser testada com e sem intervenção.
        - **Não usa dados em tempo real.** A extração é histórica; a integração com a balança é parte do piloto.
        - **Não esconde a mudança de receita.** O desempenho cai fora do tempo; monitoramento e retreino são necessários.
        - **Não substitui o anexo técnico.** VIF, importância de variáveis e curvas completas ficam nos notebooks e relatórios; o app prioriza a leitura de decisão.
        - **Não é o pipeline Docker do modelo.** Este app é o entregável Streamlit; o pipeline oficial está em `projeto-bootcamp/` e precisa ser empacotado separadamente.
        """
    )

    ui.section(
        "07",
        "Onde cada critério do guia aparece.",
        "O guia da apresentação final pede resposta e pedido nos primeiros minutos, teste no futuro, comparação com alternativa simples, impacto em cenários e uma demo curta. Este é o mapa.",
    )
    criterios = pd.DataFrame(
        [
            ("Resposta e pedido nos primeiros minutos", "Visão geral"),
            ("Regra dos 3 números", "Visão geral"),
            ("Problema com número que dói", "Diagnóstico"),
            ("Teste em período posterior", "Modelo"),
            ("Métrica traduzida em “de cada 10”", "Visão geral e Modelo"),
            ("Comparação com alternativa simples", "Modelo e Negócio & piloto"),
            ("Impacto em três cenários com premissas", "Negócio & piloto"),
            ("Recomendação com dono, prazo e custo", "Negócio & piloto"),
            ("Riscos e forma de monitorar", "Negócio & piloto"),
            ("Demo curta de 1–2 minutos, sem digitar ao vivo", "Simulador · roteiro de demonstração"),
            ("Anexo técnico: dados, features e limitações", "Dados & método"),
        ],
        columns=["Critério do guia", "Onde ver no app"],
    )
    st.dataframe(criterios, width="stretch", hide_index=True)
    ui.callout(
        "O guia pede <strong>15 minutos de fala + 10 de perguntas</strong>; o app é o apoio do professor e a demo curta, "
        "não substitui a narrativa. Para a reunião, use o roteiro de 2 minutos do simulador e mantenha os prints como plano B.",
        kind="amber",
        title="Como usar na apresentação",
    )

    ui.callout(
        "Os relatórios e os scores do holdout foram regenerados a partir do notebook atualizado, com o ambiente "
        "do app (scikit-learn 1.6.1). O artefato <code>.joblib</code> em <code>projeto-bootcamp/models/</code> é da "
        "rodada anterior e fica preservado como registro; o app não o usa para prever. O simulador usa um modelo "
        "didático separado, declarado como tal.",
        kind="blue",
        title="Rastreabilidade",
    )
    ui.source(
        "Nota de reprodutibilidade: a reexecução local de 06/11/2026 reproduz o pipeline do notebook, mas pode "
        "diferir nos últimos décimos das métricas impressas no Colab por versão de biblioteca. "
        "Os arquivos em relatorios_complementares/ são a fonte usada pelo app."
    )
    ui.source("Projeto EVCOMX · modelagem preditiva de carga alta · novembro de 2026.")
