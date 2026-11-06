"""Carregamento, agregações e métricas usadas pelas seções do app."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from . import config


# ---------------------------------------------------------------------------
# leitura
# ---------------------------------------------------------------------------


def _read_csv(path: Path, **kwargs) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding="utf-8-sig", **kwargs)
    except UnicodeDecodeError:
        return pd.read_csv(path, **kwargs)


@st.cache_data(show_spinner=False)
def load_response() -> pd.DataFrame:
    df = _read_csv(
        config.RAW_PROJETO / "VariavelResposta.csv",
        dtype={"cd_corrida": "string"},
        na_values=["null"],
    )
    return df


@st.cache_data(show_spinner=False)
def load_taxas() -> pd.DataFrame:
    return _read_csv(config.PROCESSED / "taxas_mensais.csv")


@st.cache_data(show_spinner=False)
def load_associacoes() -> pd.DataFrame:
    return _read_csv(config.PROCESSED / "associacoes_carregamentos.csv")


@st.cache_data(show_spinner=False)
def load_baskets() -> pd.DataFrame:
    df = _read_csv(config.PROCESSED / "dataset_carregamentos.csv", dtype={"cd_corrida": "string"})
    df["nu_carregamento"] = pd.to_numeric(df["nu_carregamento"], errors="coerce").astype("Int64")
    return df


@st.cache_data(show_spinner=False)
def load_modelagem() -> pd.DataFrame:
    df = _read_csv(config.PROCESSED / "dataset_modelagem.csv", dtype={"cd_corrida": "string"})
    for col in ("heat_start_utc", "heat_start_local"):
        if col in df:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_layers() -> pd.DataFrame:
    df = _read_csv(
        config.PROCESSED / "camadas_clean_enriched.csv",
        dtype={"cd_corrida": "string", "material_code": "string", "cd_baia": "string"},
    )
    if "consumed_at_utc" in df:
        df["consumed_at_utc"] = pd.to_datetime(df["consumed_at_utc"], utc=True, errors="coerce")
    if "dt_hora_consumo" in df:
        df["dt_hora_consumo"] = pd.to_datetime(df["dt_hora_consumo"], utc=True, errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_materials() -> pd.DataFrame:
    return _read_csv(config.PROCESSED / "materiais_clean.csv", dtype={"material_code": "string"})


@st.cache_data(show_spinner=False)
def load_cases() -> pd.DataFrame:
    df = _read_csv(
        config.REPORTS / "05_casos_para_investigar.csv",
        dtype={"cd_corrida": "string"},
    )
    df["inicio_utc"] = pd.to_datetime(df["inicio_utc"], utc=True, errors="coerce")
    df["mes"] = df["inicio_utc"].dt.strftime("%Y-%m")
    df["resultado"] = df["tipo_resultado"].str.extract(r"^(\w+)")[0]
    df["resultado_label"] = df["resultado"].map(
        {"VN": "normal acertado", "FP": "alarme falso", "FN": "evento perdido", "VP": "evento detectado"}
    )
    df["parada_min"] = df["parada_s"] / 60.0
    df["banda"] = pd.cut(
        df["probabilidade"],
        bins=[-0.01, 0.30, 0.45, 1.01],
        labels=["verde", "amarelo", "vermelho"],
    )
    return df


def _read_optional(name: str) -> pd.DataFrame:
    path = config.REPORTS / name
    if not path.exists():
        return pd.DataFrame()
    return _read_csv(path)


@st.cache_data(show_spinner=False)
def load_reports() -> dict[str, pd.DataFrame]:
    return {
        "metricas": _read_csv(config.REPORTS / "02_metricas_teste.csv"),
        "por_cesto": _read_csv(config.REPORTS / "03_desempenho_por_cesto.csv"),
        "por_mes": _read_csv(config.REPORTS / "04_desempenho_mensal.csv"),
        "resumo_erros": _read_csv(config.REPORTS / "06_resumo_erros.csv"),
        "limiares": _read_optional("11_comparacao_limiares.csv"),
        "v2": _read_optional("10_comparacao_ensemble_original_vs_v2.csv"),
        "auditoria": _read_csv(config.REPORTS / "01_auditoria_features.csv"),
        "intervalos": _read_optional("07_intervalos_confianca.csv"),
        "walk_forward": _read_optional("08_walk_forward.csv"),
        "drift": _read_optional("09_drift.csv"),
        "custo": _read_optional("12_custo_financeiro.csv"),
        "modelos_teste": _read_optional("13_comparacao_modelos_teste.csv"),
        "cenarios": _read_optional("14_cenarios_negocio.csv"),
        "validacao": _read_optional("15_comparacao_validacao.csv"),
        "conjuntos": _read_optional("16_comparacao_conjuntos.csv"),
    }


@st.cache_data(show_spinner=False)
def load_calendar() -> pd.DataFrame:
    frames = []
    for year in (2025, 2026):
        path = config.EXTERNAL / f"brasilapi_calendario_{year}.json"
        if path.exists():
            frames.append(pd.DataFrame(json.loads(path.read_text())))
    if not frames:
        return pd.DataFrame(columns=["date", "name"])
    return pd.concat(frames, ignore_index=True)


@st.cache_data(show_spinner=False)
def load_features_table() -> pd.DataFrame | None:
    path = config.APP_DATA / "features_cestos.parquet"
    if not path.exists():
        return None
    return pd.read_parquet(path)


@st.cache_data(show_spinner=False)
def load_simulator_metrics() -> dict:
    path = config.APP_DATA / "simulator_metrics.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


# ---------------------------------------------------------------------------
# agregações
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def summary() -> dict:
    resp = load_response()
    baskets = load_baskets()
    layers = load_layers()
    mod = load_modelagem()

    positive = resp.loc[resp["is_carga_alta"] == 1, "qt_segundos_parada_carga_alta"] / 60.0
    period_start = mod["heat_start_local"].min()
    period_end = mod["heat_start_local"].max()
    observed = baskets.dropna(subset=["weight_t"])
    meses = {1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun",
             7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez"}

    def _mes_ano(dt):
        return f"{meses[dt.month]}/{dt.year}" if pd.notna(dt) else "—"

    return {
        "n_corridas": int(len(resp)),
        "n_camadas": int(len(layers)),
        "n_camadas_brutas": int(len(layers) + 2),
        "n_cestos": int(len(observed)),
        "n_cestos_possiveis": int(len(baskets)),
        "n_eventos": int(resp["is_carga_alta"].sum()),
        "taxa_evento": float(resp["is_carga_alta"].mean()),
        "n_eventos_c1": int(resp["is_carga_alta_carregamento_1"].sum()),
        "n_eventos_c2": int(resp["is_carga_alta_carregamento_2"].sum()),
        "horas_paradas": float(resp["qt_segundos_parada_carga_alta"].sum() / 3600.0),
        "parada_mediana_min": float(positive.median()),
        "parada_p95_min": float(positive.quantile(0.95)),
        "parada_max_min": float(positive.max()),
        "periodo_inicio": _mes_ano(period_start),
        "periodo_fim": _mes_ano(period_end),
    }


@st.cache_data(show_spinner=False)
def basket_profiles() -> pd.DataFrame:
    df = load_baskets().dropna(subset=["weight_t"]).copy()
    out = (
        df.groupby("nu_carregamento")
        .agg(
            n=("cd_corrida", "size"),
            massa=("weight_t", "median"),
            volume=("volume_est_m3", "median"),
            densidade=("effective_density_t_m3", "median"),
            camadas=("layer_count", "median"),
            pesado=("heavy_share", "median"),
            leve=("light_share", "median"),
            misto=("mixed_share", "median"),
            eventos=("is_carga_alta", "sum"),
            taxa=("is_carga_alta", "mean"),
        )
        .reset_index()
    )
    return out


@st.cache_data(show_spinner=False)
def heavy_by_event() -> pd.DataFrame:
    df = load_baskets().dropna(subset=["weight_t", "heavy_share"]).copy()
    df["grupo"] = np.where(df["is_carga_alta"] == 1, "com carga alta", "sem carga alta")
    out = (
        df.groupby(["nu_carregamento", "grupo"])
        .agg(n=("cd_corrida", "size"), mediana=("heavy_share", "median"), media=("heavy_share", "mean"))
        .reset_index()
    )
    return out


@st.cache_data(show_spinner=False)
def volume_by_event() -> pd.DataFrame:
    df = load_baskets().dropna(subset=["weight_t", "volume_est_m3"]).copy()
    df["grupo"] = np.where(df["is_carga_alta"] == 1, "com carga alta", "sem carga alta")
    return (
        df.groupby(["nu_carregamento", "grupo"])
        .agg(n=("cd_corrida", "size"), mediana=("volume_est_m3", "median"))
        .reset_index()
    )


@st.cache_data(show_spinner=False)
def missing_c2() -> pd.DataFrame:
    mod = load_modelagem()
    out = (
        mod.groupby("complete_two_baskets")
        .agg(n=("cd_corrida", "size"), eventos=("is_carga_alta", "sum"), taxa=("is_carga_alta", "mean"))
        .reset_index()
    )
    out["grupo"] = np.where(out["complete_two_baskets"], "dois cestos registrados", "sem registro do cesto 2")
    return out


@st.cache_data(show_spinner=False)
def band_stats() -> pd.DataFrame:
    cases = load_cases()
    out = (
        cases.groupby("banda", observed=True)
        .agg(n=("carga_alta", "size"), eventos=("carga_alta", "sum"), taxa=("carga_alta", "mean"))
        .reset_index()
    )
    return out


@st.cache_data(show_spinner=False)
def threshold_metrics(threshold: float) -> dict:
    from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

    cases = load_cases()
    y = cases["carga_alta"].astype(int).to_numpy()
    p = cases["probabilidade"].to_numpy()
    pred = (p >= threshold).astype(int)
    tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    vp = int(((pred == 1) & (y == 1)).sum())
    precision = vp / (vp + fp) if (vp + fp) else 0.0
    recall = vp / (vp + fn) if (vp + fn) else 0.0
    f2 = 5 * precision * recall / (4 * precision + recall) if (precision + recall) else 0.0
    parada = cases["parada_min"].to_numpy()
    vp_min = float(parada[(pred == 1) & (y == 1)].sum())
    fn_min = float(parada[(pred == 0) & (y == 1)].sum())
    total_min = float(parada[y == 1].sum())
    return {
        "threshold": threshold,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "vp": vp,
        "alerts": vp + fp,
        "precision": precision,
        "recall": recall,
        "f2": f2,
        "accuracy": (tn + vp) / len(y),
        "eventos": int(y.sum()),
        "n": len(y),
        "pr_auc": float(average_precision_score(y, p)),
        "roc_auc": float(roc_auc_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "vp_min": vp_min,
        "fn_min": fn_min,
        "total_min": total_min,
        "vp_min_share": vp_min / total_min if total_min else 0.0,
        "prevalencia": float(y.mean()),
    }


@st.cache_data(show_spinner=False)
def threshold_curve() -> pd.DataFrame:
    cases = load_cases()
    y = cases["carga_alta"].astype(int).to_numpy()
    p = cases["probabilidade"].to_numpy()
    rows = []
    for t in np.linspace(0.05, 0.80, 76):
        pred = p >= t
        tp = int((pred & (y == 1)).sum())
        fp = int((pred & (y == 0)).sum())
        fn = int(((~pred) & (y == 1)).sum())
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f2 = 5 * prec * rec / (4 * prec + rec) if (prec + rec) else 0.0
        rows.append({"threshold": t, "precision": prec, "recall": rec, "f2": f2, "alerts": tp + fp})
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def pr_curve() -> pd.DataFrame:
    from sklearn.metrics import precision_recall_curve

    cases = load_cases()
    precision, recall, thresholds = precision_recall_curve(cases["carga_alta"], cases["probabilidade"])
    # precision/recall têm um ponto a mais; thresholds alinha com o penúltimo
    return pd.DataFrame(
        {
            "recall": recall[:-1],
            "precision": precision[:-1],
            "threshold": thresholds,
        }
    )


@st.cache_data(show_spinner=False)
def calibration_table(n_bins: int = 8) -> pd.DataFrame:
    cases = load_cases().copy()
    try:
        cases["bin"] = pd.qcut(cases["probabilidade"], q=n_bins, labels=False, duplicates="drop")
    except ValueError:
        cases["bin"] = pd.cut(cases["probabilidade"], bins=n_bins, labels=False)
    out = (
        cases.groupby("bin", observed=True)
        .agg(
            n=("carga_alta", "size"),
            prob_media=("probabilidade", "mean"),
            taxa_observada=("carga_alta", "mean"),
        )
        .reset_index()
    )
    return out


@st.cache_data(show_spinner=False)
def error_profile() -> pd.DataFrame:
    cases = load_cases().copy()
    out = (
        cases.groupby(["resultado", "resultado_label"])
        .agg(
            n=("carga_alta", "size"),
            eventos=("carga_alta", "sum"),
            prob_media=("probabilidade", "mean"),
            prob_mediana=("probabilidade", "median"),
            parada_total_min=("parada_min", "sum"),
            parada_media_min=("parada_min", "mean"),
            peso_mediana=("peso_total", "median"),
            volume_mediana=("volume_estimado", "median"),
            densidade_mediana=("densidade_media_cesto", "median"),
            pesado_mediana=("prop_pesado", "median"),
            leve_vol_mediana=("prop_volume_leve", "median"),
        )
        .reset_index()
        .sort_values("resultado")
    )
    return out


@st.cache_data(show_spinner=False)
def holiday_rates() -> pd.DataFrame:
    mod = load_modelagem().copy()
    cal = load_calendar()
    dates = set(cal["date"].astype(str))
    local = mod["heat_start_local"].dt.tz_convert("America/Sao_Paulo")
    mod["data_local"] = local.dt.strftime("%Y-%m-%d")
    mod["grupo"] = np.where(mod["data_local"].isin(dates), "datas do calendário", "demais dias")
    return (
        mod.groupby("grupo")
        .agg(n=("cd_corrida", "size"), eventos=("is_carga_alta", "sum"), taxa=("is_carga_alta", "mean"))
        .reset_index()
    )


@st.cache_data(show_spinner=False)
def material_counts() -> pd.DataFrame:
    layers = load_layers()
    out = (
        layers.dropna(subset=["material_code"])
        .groupby(["material_code", "ds_descricao_material"], dropna=False)
        .size()
        .reset_index(name="camadas")
        .sort_values("camadas", ascending=False)
    )
    return out


@st.cache_data(show_spinner=False)
def data_quality() -> pd.DataFrame:
    layers = load_layers()
    baskets = load_baskets()
    mod = load_modelagem()
    observed = baskets.dropna(subset=["weight_t"])
    rows = [
        ("Corridas na base", "1.799", "ok", "Uma linha por corrida na variável resposta."),
        ("Camadas brutas", f"{len(layers) + 2:,}".replace(",", "."), "ok", "43.405 linhas antes de remover 2 duplicatas."),
        ("Duplicatas exatas", "2", "atenção", "Dois pares idênticos no carregamento 3."),
        ("Cestos com composição", f"{len(observed):,}".replace(",", "."), "ok", "1.799 cestos 1 e 1.702 cestos 2."),
        ("Códigos de material", "21 observados", "atenção", "24 no dicionário; 21 nas camadas. RECC/RECG sem densidade."),
        ("Peso zero", f"{int((layers['weight_t'] == 0).sum()):,}".replace(",", "."), "atenção", "Preservados; fora da composição ativa."),
        ("Baia ausente", f"{int(layers['cd_baia'].isna().sum()):,}".replace(",", "."), "atenção", "Estrutural no gusa líquido."),
        ("Horário ausente", f"{int(layers['consumed_at_utc'].isna().sum()):,}".replace(",", "."), "atenção", "Afeta duração e turno em parte dos cestos."),
        ("Densidade incompleta", f"{int((baskets['density_coverage'] < 1).sum())}", "atenção", "Volume parcial; sem imputação."),
        ("Cesto 2 ausente", f"{int(mod['c2_weight_t'].isna().sum())}", "atenção", "51,5% com carga alta; missing não aleatório."),
        ("Features sob suspeita", "3", "atenção", "Exigem validação de disponibilidade."),
    ]
    return pd.DataFrame(rows, columns=["checagem", "resultado", "status", "leitura"])


@st.cache_data(show_spinner=False)
def report_metrics() -> pd.DataFrame:
    return load_reports()["metricas"]


@st.cache_data(show_spinner=False)
def v2_comparison() -> pd.DataFrame:
    return load_reports()["v2"]


@st.cache_data(show_spinner=False)
def threshold_comparison() -> pd.DataFrame:
    return load_reports()["limiares"]


@st.cache_data(show_spinner=False)
def performance_by_basket() -> pd.DataFrame:
    return load_reports()["por_cesto"]


@st.cache_data(show_spinner=False)
def performance_by_month() -> pd.DataFrame:
    return load_reports()["por_mes"]


@st.cache_data(show_spinner=False)
def confidence_intervals() -> pd.DataFrame:
    return load_reports()["intervalos"]


@st.cache_data(show_spinner=False)
def walk_forward() -> pd.DataFrame:
    return load_reports()["walk_forward"]


@st.cache_data(show_spinner=False)
def drift_table() -> pd.DataFrame:
    return load_reports()["drift"]


@st.cache_data(show_spinner=False)
def financial_cost() -> pd.DataFrame:
    return load_reports()["custo"]


@st.cache_data(show_spinner=False)
def model_comparison_test() -> pd.DataFrame:
    return load_reports()["modelos_teste"]


@st.cache_data(show_spinner=False)
def validation_comparison() -> pd.DataFrame:
    return load_reports()["validacao"]


@st.cache_data(show_spinner=False)
def feature_set_comparison() -> pd.DataFrame:
    return load_reports()["conjuntos"]


_CENARIO_LABEL = {
    "1. Conservador": "Conservador",
    "2. Base (Referência)": "Base",
    "3. Otimista": "Otimista",
}
_CENARIO_PARAMS = {
    "Conservador": {"sucesso": 0.50, "custo_min": 1500},
    "Base": {"sucesso": 0.70, "custo_min": 2000},
    "Otimista": {"sucesso": 0.85, "custo_min": 2500},
}


@st.cache_data(show_spinner=False)
def business_scenarios() -> pd.DataFrame:
    raw = load_reports().get("cenarios", pd.DataFrame())
    if raw.empty:
        return pd.DataFrame(
            [
                {"cenario": "Conservador", "sucesso": 0.50, "custo_min": 1500, "minutos": 212, "modelo": 0.32, "regra_volume": -1.03},
                {"cenario": "Base", "sucesso": 0.70, "custo_min": 2000, "minutos": 657, "modelo": 1.31, "regra_volume": 0.66},
                {"cenario": "Otimista", "sucesso": 0.85, "custo_min": 2500, "minutos": 993, "modelo": 2.48, "regra_volume": 2.75},
            ]
        )
    raw = raw.copy()
    raw["cenario"] = raw["Cenário"].map(_CENARIO_LABEL)
    ens = raw.loc[raw["Abordagem"].str.contains("Ensemble", na=False)].set_index("cenario")
    regra = raw.loc[raw["Abordagem"].str.contains("Regra de Volume", na=False)].set_index("cenario")
    rows = []
    for cenario in ["Conservador", "Base", "Otimista"]:
        rows.append(
            {
                "cenario": cenario,
                "sucesso": _CENARIO_PARAMS[cenario]["sucesso"],
                "custo_min": _CENARIO_PARAMS[cenario]["custo_min"],
                "minutos": float(ens.loc[cenario, "Ganho Líquido Anual (horas)"]) * 60.0,
                "modelo": float(ens.loc[cenario, "Impacto Financeiro Anual (R$)"]) / 1_000_000.0,
                "regra_volume": float(regra.loc[cenario, "Impacto Financeiro Anual (R$)"]) / 1_000_000.0,
                "modelo_brl": float(ens.loc[cenario, "Impacto Financeiro Anual (R$)"]),
                "regra_brl": float(regra.loc[cenario, "Impacto Financeiro Anual (R$)"]),
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def feature_audit() -> pd.DataFrame:
    return load_reports()["auditoria"]


@st.cache_data(show_spinner=False)
def top_materials() -> pd.DataFrame:
    return material_counts().head(12)
