# Carga Alta · EVCOMX

App em Streamlit sobre a predição de **carga alta** no forno elétrico a arco da EVCOMX, com a identidade visual da apresentação final.
A leitura parte dos dados de EDA em `dados-bootcamp/` e das evidências de modelagem em
`projeto-bootcamp/`: 1.799 corridas, 43.405 camadas, 3.501 cestos com composição e um holdout
temporal de 352 cestos.

## O que o app cobre

- **Visão geral** — o problema, a tese (composição > volume) e o que o holdout entrega.
- **Diagnóstico** — frequência e duração das paradas, cesto 1 vs. cesto 2, composição, missing do
  cesto 2 e qualidade dos dados.
- **Modelo** — split cronológico, métricas oficiais, curva de precisão-recall e um explorador
  interativo de limiar.
- **Erros & casos** — perfil de VP, FP, FN e VN, calibração e uma tabela filtrável dos 352 casos.
- **Simulador** — edite a receita de um cestão e veja o risco se mover. Usa um modelo didático
  separado, declarado no app; o ensemble oficial continua sendo a referência da seção Modelo.
- **Negócio & piloto** — cenários de ganho, semáforo, plano de 8 semanas, monitoramento e decisões.
- **Dados & método** — fontes, premissas, reprodutibilidade e limites.

## Como rodar

O projeto usa [uv](https://docs.astral.sh/uv/) e Python 3.12.

```bash
uv sync
uv run python scripts/train_simulator.py   # opcional: regenera os artefatos do simulador
uv run streamlit run app.py
```

O app abre em `http://localhost:8501`.

### Docker

```bash
docker build -t evcomx-carga-alta .
docker run --rm -p 8501:8501 --name evcomx-app evcomx-carga-alta
```

Ou:

```bash
docker compose up --build -d
docker compose logs -f
```

Para deploy em VM com HTTPS (Caddy) e no Streamlit Community Cloud, veja
[`deploy/README.md`](deploy/README.md).

### Artefatos gerados

- `data/app/features_cestos.parquet` — 3.501 cestos com os 70 atributos físicos.
- `data/app/reference_scores.csv` — scores de referência para os percentis do simulador.
- `data/app/simulator_metrics.json` — métricas do modelo didático.
- `models/app_simulator.joblib` — pipeline do simulador.

Esses arquivos já estão versionados no diretório para o app abrir sem treinar nada. O script
`scripts/train_simulator.py` reproduz exatamente os mesmos artefatos.

## Identidade visual

A interface segue a identidade da apresentação final da EVCOMX: carvão `#2F363E`,
laranja `#FF4000`, cinzas neutros, tipografia Arial e o logo EVCOMX em
`evcomx_app/assets/`. A capa da Visão geral retoma as diagonais da capa do PPTX;
as demais páginas usam a faixa branca com régua laranja dos slides de conteúdo.

## Apoio à apresentação final

A pasta `apresentacao/` reúne o material para o bloco de 15 minutos + 10 de perguntas:

- `roteiro_demo_2min.md` — roteiro da demo curta do Streamlit, com o que falar em cada passo.
- `prints/` — capturas das telas principais para o plano B do anexo.
- `README.md` — mapa dos critérios do guia para cada seção do app.

O app também traz um atalho **“Abrir demo de 2 minutos”** na Visão geral e um roteiro de demonstração dentro do Simulador. A demo usa um caso real de risco alto e uma ação de pátio ilustrativa; não é uma recomendação operacional validada.

## Estrutura

```text
app.py                         entrada do Streamlit
evcomx_app/
  config.py                    caminhos e paleta
  data.py                      leitura, agregações e métricas
  features.py                  engenharia de atributos (base + simulador)
  simulator.py                 modelo didático, explicabilidade e percentis
  charts.py                    gráficos Plotly
  ui.py                        CSS e componentes da identidade EVCOMX
  assets/                      logos EVCOMX (claro e escuro)
  sections/                    uma seção por página
scripts/train_simulator.py     treino do modelo didático
data/app/                      artefatos do simulador
models/                        modelo didático do simulador
dados-bootcamp/                bases, EDA e apresentações do projeto
projeto-bootcamp/              modelagem, relatórios e artefato do ensemble
apresentacao/                  roteiro da demo e prints de plano B
deploy/                        Caddy + compose de produção e instruções
Dockerfile                     imagem do app Streamlit
docker-compose.yml             execução local em container
requirements.txt / runtime.txt suporte ao Streamlit Community Cloud
```

## Nota metodológica

As métricas oficiais do ensemble (PR-AUC 0,350; ROC-AUC 0,687; recall 56,1% e precisão 28,3% no
limiar 0,45; 32 VP, 81 FP, 25 FN e 214 VN) vêm dos relatórios complementares atualizados em
`projeto-bootcamp/relatorios_complementares/`, regenerados a partir do notebook de modelagem em
06/11/2026. O cenário base do piloto vale R$ 1,31 mi por ano, com faixa de R$ 0,32 a 2,48 mi.
O simulador do app é uma **regressão logística didática** treinada nos 3.149 cestos fora do holdout,
com PR-AUC 0,369 e ROC-AUC 0,664 no mesmo teste. Ele existe para permitir edição em tempo real e
não substitui o ensemble oficial.

A reexecução local usa o ambiente do app (scikit-learn 1.6.1). Pequenas diferenças nos últimos
décimos em relação às métricas impressas no Colab são esperadas por versão de biblioteca; os
arquivos em `relatorios_complementares/` são a fonte usada pelo app.

A análise é observacional. O piloto de 8 semanas no pátio é o teste que falta para separar
associação de causalidade.

## Fonte dos dados

- `dados-bootcamp/data/raw/` — `VariavelResposta.csv`, `infos_camadas.csv`, `infos_materiais.csv`.
- `dados-bootcamp/data/processed/` — tabelas da EDA (`dataset_modelagem.csv`,
  `dataset_carregamentos.csv`, `associacoes_carregamentos.csv`, `taxas_mensais.csv`).
- `projeto-bootcamp/relatorios_complementares/` — métricas, casos do holdout, comparações de
  limiar e auditoria de features.
- `projeto-bootcamp/data/raw/dicionario_tipo_material.csv` — classes Leve / Misto / Pesado.
