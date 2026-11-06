"""Modelo didático do simulador, explicabilidade e percentis de referência."""

from __future__ import annotations

import warnings
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from . import config

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


FEATURE_LABELS = {
    "nu_carregamento": "Cesto (1 ou 2)",
    "peso_total": "Massa total",
    "volume_estimado": "Volume estimado",
    "densidade_media_cesto": "Densidade efetiva",
    "num_camadas": "Número de camadas",
    "num_materiais_distintos": "Materiais distintos",
    "n_baias": "Baias usadas",
    "massa_max_camada": "Maior camada",
    "massa_std_camada": "Variação da massa entre camadas",
    "dens_min_camada": "Densidade mínima",
    "dens_max_camada": "Densidade máxima",
    "dens_std_camada": "Variação da densidade",
    "peso_por_camada": "Massa por camada",
    "volume_por_camada": "Volume por camada",
    "prop_leve": "Proporção de leve (massa)",
    "prop_misto": "Proporção de misto (massa)",
    "prop_pesado": "Proporção de pesado (massa)",
    "prop_volume_leve": "Proporção de leve (volume)",
    "prop_volume_misto": "Proporção de misto (volume)",
    "prop_volume_pesado": "Proporção de pesado (volume)",
    "topo_pesado": "Topo com material pesado",
    "fundo_leve": "Fundo com material leve",
    "topo_leve": "Topo com material leve",
    "pos_rel_media_leve": "Posição média do leve",
    "pos_rel_media_misto": "Posição média do misto",
    "pos_rel_media_pesado": "Posição média do pesado",
    "prop_massa_base": "Massa na base",
    "prop_vol_base": "Volume na base",
    "dens_base": "Densidade na base",
    "prop_leve_base": "Leve na base",
    "prop_pesado_base": "Pesado na base",
    "prop_massa_meio": "Massa no meio",
    "prop_vol_meio": "Volume no meio",
    "dens_meio": "Densidade no meio",
    "prop_pesado_meio": "Pesado no meio",
    "vol_colchao_leve_meio": "Volume de leve no meio",
    "prop_massa_topo": "Massa no topo",
    "prop_vol_topo": "Volume no topo",
    "prop_leve_topo": "Leve no topo",
    "prop_pesado_topo": "Pesado no topo",
    "violacao_fundo_nao_leve": "Fundo fora da regra leve",
    "violacao_topo_nao_leve": "Topo fora da regra leve",
    "violacao_leve_no_meio": "Leve excessivo no meio",
    "score_violacao_ordem": "Score de violação da ordem",
    "razao_leve_pesado_vol": "Razão volume leve/pesado",
    "cesto1_peso_total": "Cesto 1: massa",
    "cesto1_volume_estimado": "Cesto 1: volume",
    "cesto1_densidade_media_cesto": "Cesto 1: densidade",
    "cesto1_prop_pesado": "Cesto 1: pesado",
    "cesto1_prop_leve": "Cesto 1: leve",
    "dia_semana": "Dia da semana",
    "turno": "Turno",
    "feriado_nacional": "Feriado nacional",
}


def _label(feature: str) -> str:
    if feature in FEATURE_LABELS:
        return FEATURE_LABELS[feature]
    if feature.startswith("mat_prop_"):
        return f"Participação de {feature.replace('mat_prop_', '')}"
    return feature.replace("_", " ").capitalize()


def _family(feature: str) -> str:
    if feature.startswith("mat_prop_"):
        return "Composição por material"
    if feature.startswith("cesto1_"):
        return "Contexto do cesto 1"
    if feature in {"dia_semana", "turno", "feriado_nacional"}:
        return "Contexto operacional"
    if "dens" in feature or feature in {"volume_estimado", "peso_total", "peso_por_camada", "volume_por_camada"}:
        return "Massa, volume e densidade"
    if any(k in feature for k in ["prop_", "topo_", "fundo_", "pos_rel", "violacao", "razao", "colchao"]):
        return "Composição e ordem das camadas"
    return "Outros"


@st.cache_resource(show_spinner=False)
def load_model() -> dict:
    return joblib.load(config.APP_MODEL_PATH)


@st.cache_data(show_spinner=False)
def reference_scores() -> pd.DataFrame:
    path = config.APP_DATA / "reference_scores.csv"
    if not path.exists():
        return pd.DataFrame(columns=["score"])
    return pd.read_csv(path, dtype={"cd_corrida": "string"})


def predict(features_df: pd.DataFrame) -> float:
    artifact = load_model()
    X = features_df[artifact["features"]]
    return float(artifact["model"].predict_proba(X)[:, 1][0])


def percentile(score: float) -> float:
    ref = reference_scores()
    if ref.empty:
        return 0.5
    return float((ref["score"] < score).mean())


def risk_band(score: float) -> tuple[str, str]:
    """Faixa relativa por percentil, não os cortes 30/45 do ensemble oficial."""
    p = percentile(score)
    if p < 0.50:
        return "baixo", "green"
    if p < 0.75:
        return "atenção", "amber"
    return "alto", "red"


def physical_summary(features_df: pd.DataFrame) -> dict:
    row = features_df.iloc[0]
    return {
        "peso": float(row["peso_total"]),
        "volume": float(row["volume_estimado"]),
        "densidade": float(row["densidade_media_cesto"]),
        "pesado": float(row["prop_pesado"]),
        "leve": float(row["prop_leve"]),
        "camadas": int(row["num_camadas"]),
        "materiais": int(row["num_materiais_distintos"]),
        "cesto": int(row["nu_carregamento"]),
    }


def contributions(features_df: pd.DataFrame) -> pd.Series:
    """Contribuição de cada atributo no log-odds do componente logístico."""
    artifact = load_model()
    model = artifact["model"]
    imputer = model.named_steps["imputer"]
    scaler = model.named_steps["scaler"]
    clf = model.named_steps["clf"]
    X = features_df[artifact["features"]]
    X_imp = imputer.transform(X)
    X_sc = scaler.transform(X_imp)
    values = X_sc[0] * clf.coef_[0]
    return pd.Series(values, index=artifact["features"])


def explain(features_df: pd.DataFrame, top_n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    contrib = contributions(features_df)
    out = pd.DataFrame(
        {
            "feature": contrib.index,
            "label": [_label(f) for f in contrib.index],
            "family": [_family(f) for f in contrib.index],
            "contrib": contrib.values,
        }
    )
    out["abs"] = out["contrib"].abs()
    top = out.sort_values("abs", ascending=False).head(top_n).sort_values("contrib")
    fam = (
        out.groupby("family", as_index=False)["contrib"]
        .sum()
        .assign(abs=lambda d: d["contrib"].abs())
        .sort_values("abs", ascending=False)
        .drop(columns="abs")
    )
    return top.drop(columns="abs"), fam


def reference_context() -> dict:
    metrics = load_model().get("metrics", {})
    ref = reference_scores()
    if ref.empty:
        return metrics
    out = dict(metrics)
    out["score_p50"] = float(ref["score"].quantile(0.50))
    out["score_p75"] = float(ref["score"].quantile(0.75))
    out["score_p90"] = float(ref["score"].quantile(0.90))
    return out


def metric_text() -> str:
    m = reference_context()
    pr = m.get("test_pr_auc")
    roc = m.get("test_roc_auc")
    brier = m.get("test_brier")
    if pr is None:
        return "Métricas do simulador indisponíveis."

    def _num(value: float) -> str:
        return f"{value:.3f}".replace(".", ",")

    return (
        f"Holdout de 352 cestos: PR-AUC {_num(pr)} · ROC-AUC {_num(roc)} · Brier {_num(brier)}. "
        "Modelo didático, não o ensemble oficial."
    )
