"""Treina o modelo didático usado no simulador do app.

O modelo oficial do projeto é o ensemble reportado em
`projeto-bootcamp/relatorios_complementares/`. Para o simulador, usamos uma
regressão logística transparente com os mesmos atributos e o mesmo holdout
temporal, permitindo editar a receita do cestão em tempo real.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evcomx_app import config, features  # noqa: E402


def make_pipeline(c: float) -> Pipeline:
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    C=c,
                    class_weight=None,
                    max_iter=3000,
                    random_state=42,
                ),
            ),
        ]
    )


def main() -> None:
    config.APP_DATA.mkdir(parents=True, exist_ok=True)
    config.APP_MODELS.mkdir(parents=True, exist_ok=True)

    print("Construindo a tabela de atributos dos cestos...")
    table = features.build_feature_table()
    table["inicio_utc"] = pd.to_datetime(table["inicio_utc"], utc=True, errors="coerce")
    print(f"  {len(table):,} cestos; {table['is_test'].sum():,} no holdout")

    train_pool = table.loc[~table["is_test"]].copy()
    test = table.loc[table["is_test"]].copy()

    # Validação interna: últimos 15% das corridas do pool de treino.
    order = (
        train_pool.groupby("cd_corrida")["inicio_utc"]
        .min()
        .sort_values()
        .index.tolist()
    )
    n_val = max(1, int(len(order) * 0.15))
    val_corridas = set(order[-n_val:])
    inner_train = train_pool.loc[~train_pool["cd_corrida"].isin(val_corridas)]
    inner_val = train_pool.loc[train_pool["cd_corrida"].isin(val_corridas)]

    grid = [0.01, 0.02, 0.05, 0.1, 0.2]
    rows = []
    best = None
    for c in grid:
        model = make_pipeline(c)
        model.fit(inner_train[features.FEATURES], inner_train["carga_alta"])
        p = model.predict_proba(inner_val[features.FEATURES])[:, 1]
        pr = average_precision_score(inner_val["carga_alta"], p)
        roc = roc_auc_score(inner_val["carga_alta"], p)
        rows.append({"C": c, "val_pr_auc": pr, "val_roc_auc": roc})
        print(f"  C={c:<4} val PR-AUC={pr:.4f}  ROC-AUC={roc:.4f}")
        if best is None or pr > best[1]:
            best = (c, pr, roc)

    chosen_c = best[0]
    print(f"C escolhido pela validação: {chosen_c}")

    model = make_pipeline(chosen_c)
    model.fit(train_pool[features.FEATURES], train_pool["carga_alta"])
    p_test = model.predict_proba(test[features.FEATURES])[:, 1]

    metrics = {
        "modelo": "Regressão logística didática (app)",
        "C": chosen_c,
        "n_train": int(len(train_pool)),
        "n_test": int(len(test)),
        "eventos_treino": int(train_pool["carga_alta"].sum()),
        "eventos_teste": int(test["carga_alta"].sum()),
        "test_pr_auc": float(average_precision_score(test["carga_alta"], p_test)),
        "test_roc_auc": float(roc_auc_score(test["carga_alta"], p_test)),
        "test_brier": float(brier_score_loss(test["carga_alta"], p_test)),
        "validacao": rows,
        "treinado_em": datetime.now(timezone.utc).isoformat(),
    }
    print(
        "Holdout do simulador: "
        f"PR-AUC={metrics['test_pr_auc']:.4f}  "
        f"ROC-AUC={metrics['test_roc_auc']:.4f}  "
        f"Brier={metrics['test_brier']:.4f}"
    )

    # Scores de referência para percentis do simulador.
    scores = model.predict_proba(table[features.FEATURES])[:, 1]
    reference = table[["cd_corrida", "nu_carregamento", "carga_alta", "parada_s", "is_test"]].copy()
    reference["score"] = scores
    quantiles = {
        "p50": float(np.quantile(scores, 0.50)),
        "p75": float(np.quantile(scores, 0.75)),
        "p90": float(np.quantile(scores, 0.90)),
        "p95": float(np.quantile(scores, 0.95)),
    }
    metrics["quantis_referencia"] = quantiles

    artifact = {
        "model": model,
        "features": features.FEATURES,
        "metrics": metrics,
        "target": "carga_alta",
        "note": (
            "Modelo didático do simulador. Não substitui o ensemble oficial; "
            "as métricas oficiais estão nos relatórios do projeto."
        ),
    }
    joblib.dump(artifact, config.APP_MODEL_PATH)
    table.to_parquet(config.APP_DATA / "features_cestos.parquet", index=False)
    reference.to_csv(config.APP_DATA / "reference_scores.csv", index=False)
    (config.APP_DATA / "simulator_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2)
    )

    print(f"Artefato salvo em {config.APP_MODEL_PATH}")
    print(f"Tabela salva em {config.APP_DATA / 'features_cestos.parquet'}")


if __name__ == "__main__":
    main()
