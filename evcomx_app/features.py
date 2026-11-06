"""Engenharia de atributos compartilhada entre a base e o simulador.

A lógica segue o notebook de modelagem do projeto:
- uma linha por (corrida, carregamento);
- volume = massa / densidade de catálogo;
- classes Leve / Misto / Pesado;
- atributos de composição, ordem das camadas e contexto operacional.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import config, data

CLASS_MAP = {"Light": "Leve", "Mixed": "Misto", "Heavy": "Pesado", "Unclassified": "Unclassified"}
CLASSES = ["Leve", "Misto", "Pesado"]
MATERIAIS_FREQUENTES = [
    "GUSS", "OXIC", "SHRE", "MISM", "ESPS", "PAEP", "194032", "CAVA",
    "MISB", "RECA", "RETL", "SUGU", "118441", "CAFO", "FOFO", "PACB", "ESPR",
]
KEYS = ["cd_corrida", "nu_carregamento"]

FEATURES = [
    "nu_carregamento",
    "peso_total",
    "volume_estimado",
    "densidade_media_cesto",
    "num_camadas",
    "num_materiais_distintos",
    "n_baias",
    "massa_max_camada",
    "massa_std_camada",
    "dens_min_camada",
    "dens_max_camada",
    "dens_std_camada",
    "peso_por_camada",
    "volume_por_camada",
    "prop_leve",
    "prop_misto",
    "prop_pesado",
    "prop_volume_leve",
    "prop_volume_misto",
    "prop_volume_pesado",
    "topo_pesado",
    "fundo_leve",
    "topo_leve",
    "pos_rel_media_leve",
    "pos_rel_media_misto",
    "pos_rel_media_pesado",
    "prop_massa_base",
    "prop_vol_base",
    "dens_base",
    "prop_leve_base",
    "prop_pesado_base",
    "prop_massa_meio",
    "prop_vol_meio",
    "dens_meio",
    "prop_pesado_meio",
    "vol_colchao_leve_meio",
    "prop_massa_topo",
    "prop_vol_topo",
    "prop_leve_topo",
    "prop_pesado_topo",
    "violacao_fundo_nao_leve",
    "violacao_topo_nao_leve",
    "violacao_leve_no_meio",
    "score_violacao_ordem",
    "razao_leve_pesado_vol",
    "cesto1_peso_total",
    "cesto1_volume_estimado",
    "cesto1_densidade_media_cesto",
    "cesto1_prop_pesado",
    "cesto1_prop_leve",
    "dia_semana",
    "turno",
    "feriado_nacional",
] + [f"mat_prop_{m}" for m in MATERIAIS_FREQUENTES]


def material_catalog() -> pd.DataFrame:
    """Cadastro de materiais com classe, densidade, energia e rendimento."""
    dicionario = pd.read_csv(config.RAW_PROJETO / "dicionario_tipo_material.csv", dtype="string")
    dicionario["tp_material"] = dicionario["tp_material"].str.strip()
    materiais = pd.read_csv(config.RAW_PROJETO / "infos_materiais.csv", dtype={"Metálico": "string"})
    for col in ["Energia Elétrica", "Densidade t/m3", "Rendimento Metálico %"]:
        materiais[col] = pd.to_numeric(
            materiais[col].astype("string").str.replace(",", ".", regex=False), errors="coerce"
        )

    catalogo = dicionario.rename(
        columns={"cd_codigo_material": "material_code", "ds_descricao_material": "descricao", "tp_material": "classe"}
    ).merge(
        materiais.rename(
            columns={
                "Metálico": "material_code",
                "Energia Elétrica": "energia",
                "Densidade t/m3": "densidade",
                "Rendimento Metálico %": "rendimento",
            }
        ),
        on="material_code",
        how="left",
    )

    medianas_pesado = catalogo.loc[catalogo["classe"] == "Pesado", ["energia", "densidade", "rendimento"]].median()
    for col in ["energia", "densidade", "rendimento"]:
        catalogo[col] = catalogo[col].fillna(medianas_pesado[col])

    catalogo["classe"] = catalogo["classe"].fillna("Unclassified")
    return catalogo[["material_code", "descricao", "classe", "densidade", "energia", "rendimento"]].drop_duplicates(
        "material_code"
    )


def _prepare_layers(layers: pd.DataFrame, catalogo: pd.DataFrame | None = None) -> pd.DataFrame:
    """Normaliza nomes, classes e propriedades físicas das camadas."""
    catalogo = material_catalog() if catalogo is None else catalogo
    df = layers.copy()
    if "material_code" not in df and "cd_codigo_material" in df:
        df = df.rename(columns={"cd_codigo_material": "material_code"})
    elif "material_code" in df and "cd_codigo_material" in df:
        # RECC/RECG ficam sem material_code na base enriquecida (sem densidade
        # no cadastro), mas o código original preserva a identidade do material.
        df["material_code"] = df["material_code"].fillna(df["cd_codigo_material"])
    if "weight_t" not in df and "qt_peso_carregamento" in df:
        df["weight_t"] = pd.to_numeric(df["qt_peso_carregamento"], errors="coerce") / 1000.0

    if "density_t_m3" not in df:
        df["density_t_m3"] = np.nan
    if "energy_kwh_t" not in df:
        df["energy_kwh_t"] = np.nan
    if "yield_fraction" not in df:
        df["yield_fraction"] = np.nan

    # A classe e as propriedades vêm do cadastro oficial do notebook.
    df = df.merge(
        catalogo.rename(
            columns={
                "classe": "classe_catalogo",
                "densidade": "densidade_catalogo",
                "energia": "energia_catalogo",
                "rendimento": "rendimento_catalogo",
            }
        ),
        on="material_code",
        how="left",
    )
    if "classe" in df:
        df["classe"] = df["classe"].map(CLASS_MAP).fillna(df["classe"])
    df["classe"] = df.get("classe_catalogo", pd.Series(index=df.index, dtype="object")).fillna(
        df.get("classe", pd.Series(index=df.index, dtype="object"))
    )
    df["classe"] = df["classe"].fillna("Unclassified")
    df["density_t_m3"] = df["density_t_m3"].fillna(df["densidade_catalogo"])
    df["energy_kwh_t"] = df["energy_kwh_t"].fillna(df["energia_catalogo"])
    df["yield_fraction"] = df["yield_fraction"].fillna(df["rendimento_catalogo"])

    if "consumed_at_utc" not in df:
        if "dt_hora_consumo" in df:
            df["consumed_at_utc"] = pd.to_datetime(df["dt_hora_consumo"], utc=True, errors="coerce")
        else:
            df["consumed_at_utc"] = pd.NaT
    if "cd_baia" not in df:
        df["cd_baia"] = pd.NA

    df["volume_m3"] = df["weight_t"] / df["density_t_m3"]
    df["energia_mwh"] = df["weight_t"] * df["energy_kwh_t"] / 1000.0
    df["massa_metalica_t"] = df["weight_t"] * df["yield_fraction"]
    return df


def aggregate_features(active: pd.DataFrame, zeros: pd.Series | None = None) -> pd.DataFrame:
    """Agrega camadas ativas em uma linha por cesto."""
    df = active.copy()
    df = df.sort_values(KEYS + ["nu_camada"]).reset_index(drop=True)
    df["ordem_camada"] = df.groupby(KEYS).cumcount()
    df["total_camadas_cesto"] = df.groupby(KEYS)["nu_camada"].transform("count")
    df["pos_relativa"] = df["ordem_camada"] / np.maximum(df["total_camadas_cesto"] - 1, 1)
    df["regiao_cesto"] = pd.cut(
        df["pos_relativa"], bins=[-0.01, 0.334, 0.667, 1.01], labels=["base", "meio", "topo"]
    )
    df["massa_x_pos"] = df["weight_t"] * df["pos_relativa"]
    df["vol_x_pos"] = df["volume_m3"] * df["pos_relativa"]

    g = df.groupby(KEYS)
    feat = g.agg(
        peso_total=("weight_t", "sum"),
        volume_estimado=("volume_m3", "sum"),
        energia_mwh=("energia_mwh", "sum"),
        massa_metalica_t=("massa_metalica_t", "sum"),
        num_camadas=("nu_camada", "nunique"),
        num_materiais_distintos=("material_code", "nunique"),
        n_baias=("cd_baia", "nunique"),
        massa_max_camada=("weight_t", "max"),
        massa_std_camada=("weight_t", "std"),
        vol_max_camada=("volume_m3", "max"),
        dens_min_camada=("density_t_m3", "min"),
        dens_max_camada=("density_t_m3", "max"),
        dens_std_camada=("density_t_m3", "std"),
        massa_x_pos_sum=("massa_x_pos", "sum"),
        vol_x_pos_sum=("vol_x_pos", "sum"),
        inicio_utc=("consumed_at_utc", "min"),
        fim_utc=("consumed_at_utc", "max"),
    )
    feat["densidade_media_cesto"] = feat["peso_total"] / feat["volume_estimado"]
    feat["peso_por_camada"] = feat["peso_total"] / feat["num_camadas"]
    feat["volume_por_camada"] = feat["volume_estimado"] / feat["num_camadas"]
    feat["rendimento_efetivo"] = feat["massa_metalica_t"] / feat["peso_total"]
    feat["energia_especifica"] = feat["energia_mwh"] * 1000.0 / feat["peso_total"]
    feat["centro_massa_pos"] = feat["massa_x_pos_sum"] / feat["peso_total"]
    feat["centro_vol_pos"] = feat["vol_x_pos_sum"] / feat["volume_estimado"]
    feat["duracao_montagem_min"] = (feat["fim_utc"] - feat["inicio_utc"]).dt.total_seconds() / 60.0
    feat = feat.drop(columns=["massa_x_pos_sum", "vol_x_pos_sum"])
    feat["n_baias"] = feat["n_baias"].replace(0, np.nan)

    tp_massa = (
        df.pivot_table(index=KEYS, columns="classe", values="weight_t", aggfunc="sum", fill_value=0.0)
        .reindex(columns=CLASSES, fill_value=0.0)
    )
    tp_vol = (
        df.pivot_table(index=KEYS, columns="classe", values="volume_m3", aggfunc="sum", fill_value=0.0)
        .reindex(columns=CLASSES, fill_value=0.0)
    )
    for classe in CLASSES:
        low = classe.lower()
        feat[f"peso_{low}"] = tp_massa[classe]
        feat[f"prop_{low}"] = tp_massa[classe] / feat["peso_total"]
        feat[f"volume_{low}"] = tp_vol[classe]
        feat[f"prop_volume_{low}"] = tp_vol[classe] / feat["volume_estimado"]

    mat_pivot = df.pivot_table(
        index=KEYS, columns="material_code", values="weight_t", aggfunc="sum", fill_value=0.0
    )
    mat_frac = mat_pivot.div(feat["peso_total"], axis=0)
    for material in MATERIAIS_FREQUENTES:
        feat[f"mat_prop_{material}"] = mat_frac[material] if material in mat_frac.columns else 0.0

    fundo = df.loc[df.groupby(KEYS)["nu_camada"].idxmin()].set_index(KEYS)
    topo = df.loc[df.groupby(KEYS)["nu_camada"].idxmax()].set_index(KEYS)
    feat["fundo_leve"] = (fundo["classe"] == "Leve").astype(int)
    feat["fundo_pesado"] = (fundo["classe"] == "Pesado").astype(int)
    feat["topo_leve"] = (topo["classe"] == "Leve").astype(int)
    feat["topo_pesado"] = (topo["classe"] == "Pesado").astype(int)

    for classe in CLASSES:
        low = classe.lower()
        sub = df.loc[df["classe"] == classe]
        pos_pond = sub.groupby(KEYS)["massa_x_pos"].sum() / sub.groupby(KEYS)["weight_t"].sum()
        feat[f"pos_rel_media_{low}"] = pos_pond.reindex(feat.index, fill_value=0.5)

    for reg in ["base", "meio", "topo"]:
        sub = df.loc[df["regiao_cesto"] == reg]
        rg = sub.groupby(KEYS)
        m_reg = rg["weight_t"].sum()
        v_reg = rg["volume_m3"].sum()
        feat[f"prop_massa_{reg}"] = (m_reg / feat["peso_total"]).fillna(0.0)
        feat[f"prop_vol_{reg}"] = (v_reg / feat["volume_estimado"]).fillna(0.0)
        feat[f"dens_{reg}"] = m_reg / v_reg
        m_leve = sub.loc[sub["classe"] == "Leve"].groupby(KEYS)["weight_t"].sum()
        m_pesado = sub.loc[sub["classe"] == "Pesado"].groupby(KEYS)["weight_t"].sum()
        feat[f"prop_leve_{reg}"] = (m_leve / m_reg).fillna(0.0)
        feat[f"prop_pesado_{reg}"] = (m_pesado / m_reg).fillna(0.0)
        v_leve = sub.loc[sub["classe"] == "Leve"].groupby(KEYS)["volume_m3"].sum()
        feat[f"vol_colchao_leve_{reg}"] = v_leve.reindex(feat.index, fill_value=0.0)

    feat["violacao_fundo_nao_leve"] = (1 - feat["fundo_leve"]).astype(int)
    feat["violacao_topo_nao_leve"] = (1 - feat["topo_leve"]).astype(int)
    feat["violacao_leve_no_meio"] = (feat["prop_leve_meio"] > 0.30).astype(int)
    feat["score_violacao_ordem"] = (
        feat["violacao_fundo_nao_leve"] + feat["violacao_topo_nao_leve"] + feat["violacao_leve_no_meio"]
    )
    feat["razao_leve_pesado_vol"] = feat["volume_leve"] / (feat["volume_pesado"] + 0.5)

    if zeros is None:
        zeros = pd.Series(dtype="int64")
    feat["n_camadas_zero"] = zeros.reindex(feat.index, fill_value=0).astype(int)

    return feat.reset_index()


def add_cesto1(feat: pd.DataFrame, cesto1_summary: dict | None = None) -> pd.DataFrame:
    """Adiciona o resumo do cesto 1 usado como contexto do cesto 2."""
    out = feat.copy()
    cols = ["peso_total", "volume_estimado", "densidade_media_cesto", "prop_pesado", "prop_leve"]
    own = out.loc[out["nu_carregamento"] == 1, ["cd_corrida"] + cols].copy()
    if not own.empty:
        own = own.rename(columns={c: f"cesto1_{c}" for c in cols})
        out = out.merge(own, on="cd_corrida", how="left")
    else:
        for c in cols:
            out[f"cesto1_{c}"] = np.nan

    if cesto1_summary:
        for c in cols:
            out[f"cesto1_{c}"] = cesto1_summary.get(c, np.nan)
    return out


def _time_features(feat: pd.DataFrame, layers: pd.DataFrame | None = None) -> pd.DataFrame:
    out = feat.copy()
    start = pd.to_datetime(out["inicio_utc"], utc=True, errors="coerce")
    if layers is not None and "cd_corrida" in out and "consumed_at_utc" in layers:
        corrida_start = layers.groupby("cd_corrida")["consumed_at_utc"].min().rename("corrida_inicio_utc")
        out = out.merge(corrida_start, on="cd_corrida", how="left")
        fallback = pd.to_datetime(out["corrida_inicio_utc"], utc=True, errors="coerce")
        start = start.fillna(fallback)
    local = start.dt.tz_convert("America/Sao_Paulo")
    out["dia_semana"] = local.dt.dayofweek
    out["turno"] = local.dt.hour // 8
    cal = data.load_calendar()
    dates = set(cal["date"].astype(str)) if not cal.empty else set()
    out["feriado_nacional"] = local.dt.strftime("%Y-%m-%d").isin(dates).astype(int)
    return out


def build_feature_table() -> pd.DataFrame:
    """Uma linha por cesto com composição, contexto e rótulos."""
    layers = data.load_layers()
    catalogo = material_catalog()
    prepared = _prepare_layers(layers, catalogo)
    prepared = prepared.loc[prepared["nu_carregamento"].isin([1, 2])].copy()

    active = prepared.loc[prepared["weight_t"] > 0]
    zeros = (
        prepared.loc[prepared["weight_t"].eq(0)]
        .groupby(KEYS)
        .size()
        .rename("n_zero")
    )
    # aggregate_features espera a série indexada por KEYS
    feat = aggregate_features(active, zeros)
    feat = add_cesto1(feat)
    feat = _time_features(feat, prepared)

    resp = data.load_response()
    labels = pd.concat(
        [
            resp[
                [
                    "cd_corrida",
                    f"is_carga_alta_carregamento_{i}",
                    f"qt_segundos_duracao_parada_carregamento_{i}",
                ]
            ]
            .rename(
                columns={
                    f"is_carga_alta_carregamento_{i}": "carga_alta",
                    f"qt_segundos_duracao_parada_carregamento_{i}": "parada_s",
                }
            )
            .assign(nu_carregamento=i)
            for i in (1, 2)
        ],
        ignore_index=True,
    )
    feat = labels.merge(feat, on=KEYS, how="left")
    feat = feat.dropna(subset=["peso_total"]).reset_index(drop=True)

    cases = data.load_cases()
    test_keys = set(zip(cases["cd_corrida"], cases["nu_carregamento"]))
    feat["is_test"] = [(c, n) in test_keys for c, n in zip(feat["cd_corrida"], feat["nu_carregamento"])]
    return feat


def preset_layers(corrida: str, nu_carregamento: int) -> pd.DataFrame:
    """Camadas reais de um cesto para começar a simulação."""
    layers = data.load_layers()
    catalogo = material_catalog()
    df = _prepare_layers(layers, catalogo)
    df = df.loc[
        (df["cd_corrida"] == corrida)
        & (df["nu_carregamento"] == int(nu_carregamento))
        & (df["weight_t"] > 0)
    ].copy()
    df = df.sort_values("nu_camada")
    out = df[
        ["nu_camada", "material_code", "descricao", "classe", "weight_t", "cd_baia", "consumed_at_utc"]
    ].copy()
    out["nu_camada"] = out["nu_camada"].astype(int)
    out["weight_t"] = out["weight_t"].round(2)
    return out.reset_index(drop=True)


def preset_metadata(corrida: str, nu_carregamento: int) -> dict:
    mod = data.load_modelagem()
    row = mod.loc[mod["cd_corrida"] == corrida]
    cases = data.load_cases()
    case = cases.loc[(cases["cd_corrida"] == corrida) & (cases["nu_carregamento"] == int(nu_carregamento))]
    baskets = data.load_baskets()
    c1 = baskets.loc[(baskets["cd_corrida"] == corrida) & (baskets["nu_carregamento"] == 1)]
    meta = {
        "turno": None,
        "dia_semana": None,
        "feriado_nacional": 0,
        "duracao_montagem_min": np.nan,
        "cesto1": None,
        "oficial": None,
        "real": None,
        "parada_s": None,
        "inicio_utc": None,
    }
    if not case.empty:
        c = case.iloc[0]
        meta.update(
            {
                "oficial": float(c["probabilidade"]),
                "real": int(c["carga_alta"]),
                "parada_s": float(c["parada_s"]),
                "inicio_utc": c["inicio_utc"],
                "turno": int(pd.Timestamp(c["inicio_utc"]).tz_convert("America/Sao_Paulo").hour // 8),
                "dia_semana": int(pd.Timestamp(c["inicio_utc"]).tz_convert("America/Sao_Paulo").dayofweek),
            }
        )
    if not c1.empty:
        c = c1.iloc[0]
        meta["cesto1"] = {
            "peso_total": float(c["weight_t"]),
            "volume_estimado": float(c["volume_est_m3"]),
            "densidade_media_cesto": float(c["effective_density_t_m3"]),
            "prop_pesado": float(c["heavy_share"]),
            "prop_leve": float(c["light_share"]),
        }
    if meta["dia_semana"] is None and not row.empty:
        dt = row.iloc[0].get("heat_start_local")
        if pd.notna(dt):
            local = pd.Timestamp(dt).tz_convert("America/Sao_Paulo")
            meta["dia_semana"] = int(local.dayofweek)
            meta["turno"] = int(local.hour // 8)
    return meta


def cesto1_default() -> dict:
    table = data.load_features_table()
    if table is None:
        table = build_feature_table()
    c1 = table.loc[table["nu_carregamento"] == 1]
    return {
        "peso_total": float(c1["peso_total"].median()),
        "volume_estimado": float(c1["volume_estimado"].median()),
        "densidade_media_cesto": float(c1["densidade_media_cesto"].median()),
        "prop_pesado": float(c1["prop_pesado"].median()),
        "prop_leve": float(c1["prop_leve"].median()),
    }


def build_basket_features(
    layers_edit: pd.DataFrame,
    nu_carregamento: int,
    *,
    context: dict | None = None,
    cesto1_summary: dict | None = None,
    duracao_montagem_min: float | None = None,
) -> pd.DataFrame:
    """Constrói a linha de atributos de um cesto editado no simulador."""
    context = context or {}
    catalogo = material_catalog()
    df = layers_edit.copy()
    if "cd_corrida" not in df:
        df["cd_corrida"] = "SIMULADO"
    if "nu_carregamento" not in df:
        df["nu_carregamento"] = int(nu_carregamento)
    if "cd_baia" not in df:
        df["cd_baia"] = pd.NA
    if "consumed_at_utc" not in df:
        df["consumed_at_utc"] = pd.NaT
    df = _prepare_layers(df, catalogo)
    df = df.loc[df["weight_t"].notna()].copy()
    zeros = pd.Series(
        [int((df["weight_t"] == 0).sum())],
        index=pd.MultiIndex.from_tuples(
            [("SIMULADO", int(nu_carregamento))], names=["cd_corrida", "nu_carregamento"]
        ),
    )
    active = df.loc[df["weight_t"] > 0].copy()
    feat = aggregate_features(active, zeros)
    if duracao_montagem_min is not None:
        feat["duracao_montagem_min"] = float(duracao_montagem_min)
    feat = add_cesto1(feat, cesto1_summary if int(nu_carregamento) == 2 else None)
    feat["dia_semana"] = context.get("dia_semana", 0)
    feat["turno"] = context.get("turno", 1)
    feat["feriado_nacional"] = int(context.get("feriado_nacional", 0))
    feat["inicio_utc"] = pd.NaT
    feat["fim_utc"] = pd.NaT
    feat["cd_corrida"] = "SIMULADO"
    feat["nu_carregamento"] = int(nu_carregamento)

    for col in FEATURES:
        if col not in feat:
            feat[col] = np.nan
    return feat[FEATURES].copy()
