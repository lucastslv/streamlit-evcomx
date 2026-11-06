# Relatórios complementares

Arquivos gerados a partir do notebook `projeto-bootcamp/notebooks/lucas_predicao.ipynb`.

- **Rodada atual:** 06/11/2026, com o ambiente do app (Python 3.12, scikit-learn 1.6.1).
- **Holdout:** 180 corridas, 352 cestos e 57 eventos; limiar operacional 0,45.
- **Fonte de verdade do app:** `02_metricas_teste.csv` e `05_casos_para_investigar.csv`.
- **Artefato `.joblib`:** o arquivo em `projeto-bootcamp/models/` é da rodada anterior e foi preservado;
  o app não o usa para prever.

Os arquivos `10_comparacao_ensemble_original_vs_v2.csv` e `11_comparacao_limiares.csv` mantêm a
comparação histórica com a versão revisada e as estratégias de limiar. Pequenas diferenças nos
últimos décimos em relação às saídas impressas no Colab são esperadas por versão de biblioteca.
