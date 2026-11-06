"""Gráficos Plotly com leitura editorial: título fora, grade discreta, anotação direta."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import config


def _base(fig: go.Figure, height: int = 340, showlegend: bool = False) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=48, r=18, t=12, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Helvetica, Arial, sans-serif", size=12, color=config.INK),
        hoverlabel=dict(bgcolor=config.CARD, font=dict(color=config.INK, size=12)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(size=11, color=config.MUTED),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=showlegend,
        bargap=0.28,
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=config.RULE,
        tickfont=dict(size=11, color=config.MUTED),
        title_font=dict(size=11, color=config.MUTED),
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=config.RULE,
        gridwidth=0.6,
        zeroline=False,
        tickfont=dict(size=11, color=config.MUTED),
        title_font=dict(size=11, color=config.MUTED),
        automargin=True,
    )
    return fig


MESES = {1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun",
         7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez"}


def _pct(value: float | None, digits: int = 0) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "—"
    return f"{value:.{digits}%}".replace(".", ",")


def _month_labels(values) -> list[str]:
    labels = []
    for value in values:
        text = str(value)
        try:
            year, month = text.split("-")[:2]
            labels.append(f"{MESES[int(month)]}/{year[2:]}")
        except (ValueError, KeyError):
            labels.append(text)
    return labels


def monthly_rate(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["month"],
            y=d["ci_high"],
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["month"],
            y=d["ci_low"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(182,69,47,0.12)",
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["month"],
            y=d["rate"],
            mode="lines+markers",
            line=dict(color=config.RED, width=2.4),
            marker=dict(size=6, color=config.RED, line=dict(color=config.CARD, width=1)),
            name="taxa mensal",
            customdata=np.stack([d["n"], d["events"], d["ci_low"], d["ci_high"]], axis=-1),
            hovertemplate=(
                "<b>%{x}</b><br>taxa: %{y:.1%}<br>"
                "eventos: %{customdata[1]} de %{customdata[0]}<br>"
                "IC 95%: %{customdata[2]:.1%}–%{customdata[3]:.1%}<extra></extra>"
            ),
        )
    )
    fig.add_hline(
        y=0.30,
        line=dict(color=config.GRAY, width=1, dash="dot"),
        annotation_text="média da amostra: 30%",
        annotation_position="top left",
        annotation_font=dict(size=10, color=config.MUTED),
    )
    labels = _month_labels(d["month"])
    fig.update_yaxes(range=[0, 0.52], tickformat=".0%", title="corridas com carga alta")
    fig.update_xaxes(
        type="category",
        tickmode="array",
        tickvals=d["month"][::2],
        ticktext=labels[::2],
        tickangle=-35,
    )
    return _base(fig, height=330)


def monthly_downtime(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    d["horas"] = d["downtime_minutes"] / 60.0
    fig = go.Figure(
        go.Bar(
            x=d["month"],
            y=d["horas"],
            marker_color=config.GRAY,
            marker_line_width=0,
            text=[f"{v:.1f}" if v >= 8 else "" for v in d["horas"]],
            textposition="outside",
            textfont=dict(size=9, color=config.MUTED),
            hovertemplate="<b>%{x}</b><br>%{y:.1f} h de parada<extra></extra>",
        )
    )
    labels = _month_labels(d["month"])
    fig.update_yaxes(title="horas de forno parado", rangemode="tozero")
    fig.update_xaxes(
        type="category",
        tickmode="array",
        tickvals=d["month"][::2],
        ticktext=labels[::2],
        tickangle=-35,
    )
    return _base(fig, height=330)


def bar_pair(
    df: pd.DataFrame,
    value_col: str,
    *,
    label: str,
    y_title: str,
    percent: bool = False,
    height: int = 250,
    color: str = config.BLUE,
) -> go.Figure:
    d = df.copy()
    d["rotulo"] = d["nu_carregamento"].map({1: "Cesto 1", 2: "Cesto 2"})
    values = d[value_col]
    text = [_pct(v, 1) if percent else f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in values]
    fig = go.Figure(
        go.Bar(
            x=d["rotulo"],
            y=values,
            marker_color=[color, config.AMBER][: len(d)],
            marker_line_width=0,
            text=text,
            textposition="outside",
            textfont=dict(size=11, color=config.INK),
            hovertemplate="<b>%{x}</b><br>" + label + ": %{y}<extra></extra>",
        )
    )
    fig.update_yaxes(
        title=y_title,
        rangemode="tozero",
        tickformat=".0%" if percent else None,
    )
    fig.update_xaxes(title=None)
    return _base(fig, height=height)


def heavy_by_event(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    d["rotulo"] = d["nu_carregamento"].map({1: "Cesto 1", 2: "Cesto 2"})
    groups = ["sem carga alta", "com carga alta"]
    colors = {"sem carga alta": config.GRAY, "com carga alta": config.RED}
    fig = go.Figure()
    for group in groups:
        sub = d.loc[d["grupo"] == group]
        fig.add_trace(
            go.Bar(
                x=sub["rotulo"],
                y=sub["mediana"],
                name=group,
                marker_color=colors[group],
                marker_line_width=0,
                text=[f"{v:.1%}".replace(".", ",") for v in sub["mediana"]],
                textposition="outside",
                textfont=dict(size=10, color=config.INK),
                customdata=np.stack([sub["n"], sub["media"]], axis=-1),
                hovertemplate=(
                    "<b>%{x} · " + group + "</b><br>mediana: %{y:.1%}<br>"
                    "média: %{customdata[1]:.1%}<br>n = %{customdata[0]}<extra></extra>"
                ),
            )
        )
    fig.update_yaxes(title="participação de material pesado", range=[0, 0.45], tickformat=".0%")
    fig.update_layout(barmode="group")
    return _base(fig, height=330, showlegend=True)


def volume_by_event(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    d["rotulo"] = d["nu_carregamento"].map({1: "Cesto 1", 2: "Cesto 2"})
    groups = ["sem carga alta", "com carga alta"]
    colors = {"sem carga alta": config.GRAY, "com carga alta": config.RED}
    fig = go.Figure()
    for group in groups:
        sub = d.loc[d["grupo"] == group]
        fig.add_trace(
            go.Bar(
                x=sub["rotulo"],
                y=sub["mediana"],
                name=group,
                marker_color=colors[group],
                marker_line_width=0,
                text=[f"{v:,.0f}".replace(",", ".") for v in sub["mediana"]],
                textposition="outside",
                textfont=dict(size=10, color=config.INK),
                customdata=sub["n"],
                hovertemplate="<b>%{x} · " + group + "</b><br>%{y:.1f} m³<br>n = %{customdata}<extra></extra>",
            )
        )
    fig.update_yaxes(title="volume estimado mediano (m³)", rangemode="tozero")
    fig.update_layout(barmode="group")
    return _base(fig, height=330, showlegend=True)


FEATURE_LABELS = {
    "weight_t": "Massa",
    "volume_est_m3": "Volume estimado",
    "effective_density_t_m3": "Densidade efetiva",
    "layer_count": "Camadas ativas",
    "material_count": "Materiais distintos",
    "light_share": "Proporção de leve",
    "heavy_share": "Proporção de pesado",
    "mixed_share": "Proporção de misto",
    "bottom_light_share": "Leve na base",
    "top_light_share": "Leve no topo",
    "middle_light_share_total": "Leve no meio",
    "energy_weighted_kwh_t": "Energia específica",
    "yield_weighted_fraction": "Rendimento metálico",
}


def association_bars(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    d["feature_label"] = d["feature"].map(FEATURE_LABELS).fillna(d["feature"])
    order = [
        "volume_est_m3",
        "weight_t",
        "effective_density_t_m3",
        "layer_count",
        "material_count",
        "light_share",
        "heavy_share",
        "mixed_share",
        "bottom_light_share",
        "top_light_share",
        "middle_light_share_total",
        "energy_weighted_kwh_t",
        "yield_weighted_fraction",
    ]
    d["ordem"] = d["feature"].map({f: i for i, f in enumerate(order)})
    d = d.sort_values("ordem", ascending=True)
    labels = [FEATURE_LABELS.get(f, f) for f in order]
    colors = {1: config.BLUE, 2: config.RED}
    fig = go.Figure()

    # Haste cinza entre os dois cestos, como um dumbbell plot.
    pivot = d.pivot_table(index="feature", columns="charge", values="point_biserial_r")
    for feature in order:
        if feature not in pivot.index:
            continue
        row = pivot.loc[feature]
        if 1 in row.index and 2 in row.index and pd.notna(row.get(1)) and pd.notna(row.get(2)):
            fig.add_trace(
                go.Scatter(
                    x=[row[1], row[2]],
                    y=[FEATURE_LABELS.get(feature, feature)] * 2,
                    mode="lines",
                    line=dict(color=config.GRAY_SOFT, width=2),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
    for charge in (1, 2):
        sub = d.loc[d["charge"] == charge]
        fig.add_trace(
            go.Scatter(
                x=sub["point_biserial_r"],
                y=sub["feature_label"],
                mode="markers",
                name=f"Cesto {charge}",
                marker=dict(size=9, color=colors[charge], line=dict(color=config.CARD, width=1)),
                hovertemplate="<b>%{y}</b><br>Cesto " + str(charge) + "<br>r = %{x:+.3f}<extra></extra>",
            )
        )
    fig.add_vline(x=0, line=dict(color=config.INK, width=1))
    values = d["point_biserial_r"].dropna()
    xmin = min(-0.10, float(values.min()) * 1.28) if not values.empty else -0.3
    xmax = max(0.10, float(values.max()) * 1.28) if not values.empty else 0.2
    fig.update_xaxes(title="correlação ponto-bisserial com carga alta", range=[xmin, xmax])
    fig.update_yaxes(
        title=None,
        categoryorder="array",
        categoryarray=list(reversed(labels)),
    )
    fig = _base(fig, height=470, showlegend=True)
    fig.update_layout(margin=dict(r=30))
    return fig


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def missing_c2(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    d["ci"] = d.apply(lambda r: _wilson(int(r["eventos"]), int(r["n"])), axis=1)
    d["ci_low"] = d["ci"].apply(lambda x: x[0])
    d["ci_high"] = d["ci"].apply(lambda x: x[1])
    colors = [config.RED if "sem" in g else config.BLUE for g in d["grupo"]]
    fig = go.Figure(
        go.Bar(
            x=d["grupo"],
            y=d["taxa"],
            marker_color=colors,
            marker_line_width=0,
            error_y=dict(
                type="data",
                symmetric=False,
                array=d["ci_high"] - d["taxa"],
                arrayminus=d["taxa"] - d["ci_low"],
                color=config.INK,
                thickness=1.2,
                width=4,
            ),
            text=[f"{v:.1%}" for v in d["taxa"]],
            textposition="outside",
            textfont=dict(size=12, color=config.INK),
            customdata=np.stack([d["n"], d["eventos"]], axis=-1),
            hovertemplate=(
                "<b>%{x}</b><br>taxa: %{y:.1%}<br>"
                "eventos: %{customdata[1]} de %{customdata[0]}<extra></extra>"
            ),
        )
    )
    fig.update_yaxes(title="corridas com carga alta", range=[0, 0.68], tickformat=".0%")
    fig.update_xaxes(title=None)
    return _base(fig, height=320)


def holiday_bars(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    d["ci"] = d.apply(lambda r: _wilson(int(r["eventos"]), int(r["n"])), axis=1)
    d["ci_low"] = d["ci"].apply(lambda x: x[0])
    d["ci_high"] = d["ci"].apply(lambda x: x[1])
    colors = [config.AMBER if "calendário" in g else config.GRAY for g in d["grupo"]]
    fig = go.Figure(
        go.Bar(
            x=d["grupo"],
            y=d["taxa"],
            marker_color=colors,
            marker_line_width=0,
            error_y=dict(
                type="data",
                symmetric=False,
                array=d["ci_high"] - d["taxa"],
                arrayminus=d["taxa"] - d["ci_low"],
                color=config.INK,
                thickness=1.2,
                width=4,
            ),
            text=[f"{v:.1%}" for v in d["taxa"]],
            textposition="outside",
            textfont=dict(size=12, color=config.INK),
            customdata=np.stack([d["n"], d["eventos"]], axis=-1),
            hovertemplate=(
                "<b>%{x}</b><br>taxa: %{y:.1%}<br>"
                "eventos: %{customdata[1]} de %{customdata[0]}<extra></extra>"
            ),
        )
    )
    fig.update_yaxes(title="corridas com carga alta", range=[0, 0.62], tickformat=".0%")
    return _base(fig, height=310)


def downtime_hist(resp: pd.DataFrame) -> go.Figure:
    d = resp.loc[resp["is_carga_alta"] == 1, "qt_segundos_parada_carga_alta"] / 60.0
    bins = [0, 1, 3, 6, 10, 21]
    counts, edges = np.histogram(d, bins=bins)
    centers = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
    labels = [f"{edges[i]:.0f}–{edges[i+1]:.0f}" for i in range(len(edges) - 1)]
    fig = go.Figure(
        go.Bar(
            x=centers,
            y=counts,
            width=[(edges[i + 1] - edges[i]) * 0.82 for i in range(len(edges) - 1)],
            marker_color=config.RED,
            marker_line_width=0,
            customdata=labels,
            hovertemplate="<b>%{customdata} min</b><br>%{y} corridas<extra></extra>",
        )
    )
    fig.add_vline(
        x=3.0,
        line=dict(color=config.INK, width=1, dash="dot"),
        annotation_text="mediana: 3,0 min",
        annotation_position="top right",
        annotation_font=dict(size=10, color=config.INK),
    )
    fig.update_xaxes(
        title="minutos de parada por corrida afetada",
        tickvals=centers,
        ticktext=labels,
        tickangle=-30,
    )
    fig.update_yaxes(title="corridas", rangemode="tozero")
    return _base(fig, height=310)


def pr_curve(df: pd.DataFrame, ap: float, threshold: float = 0.45) -> go.Figure:
    d = df.loc[df["recall"] > 0].sort_values("recall")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["recall"],
            y=d["precision"],
            mode="lines",
            line=dict(color=config.RED, width=2.6),
            name="ensemble",
            hovertemplate="recall %{x:.2f}<br>precisão %{y:.2f}<extra></extra>",
        )
    )
    fig.add_hline(
        y=0.1619,
        line=dict(color=config.GRAY, width=1, dash="dot"),
        annotation_text="prevalência: 16,2%",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color=config.MUTED),
    )
    # Ponto operacional no limiar escolhido.
    if not d.empty:
        idx = (d["threshold"] - threshold).abs().idxmin()
        op = d.loc[idx]
        if pd.notna(op["threshold"]):
            fig.add_trace(
                go.Scatter(
                    x=[op["recall"]],
                    y=[op["precision"]],
                    mode="markers",
                    marker=dict(size=11, color=config.INK, line=dict(color=config.CARD, width=2)),
                    showlegend=False,
                    hovertemplate=(
                        f"limiar {op['threshold']:.2f}".replace(".", ",") + "<br>"
                        f"recall {op['recall']:.1%}<br>precisão {op['precision']:.1%}<extra></extra>"
                    ),
                )
            )
    fig.update_xaxes(title="recall (eventos capturados)", range=[0, 1], tickformat=".0%")
    fig.update_yaxes(title="precisão", range=[0, 1], tickformat=".0%")
    fig.add_annotation(
        x=0.02,
        y=0.06,
        xref="paper",
        yref="paper",
        text=f"PR-AUC = {ap:.3f}".replace(".", ","),
        showarrow=False,
        font=dict(size=12, color=config.INK, family="Source Serif 4, Georgia, serif"),
        bgcolor=config.CARD,
        bordercolor=config.RULE,
        borderwidth=1,
    )
    return _base(fig, height=370)


def threshold_curves(df: pd.DataFrame, current: float) -> go.Figure:
    d = df.copy()
    fig = go.Figure()
    specs = [
        ("recall", "recall", config.RED),
        ("precision", "precisão", config.BLUE),
        ("f2", "F2", config.AMBER),
    ]
    for col, label, color in specs:
        fig.add_trace(
            go.Scatter(
                x=d["threshold"],
                y=d[col],
                mode="lines",
                line=dict(color=color, width=2.2),
                name=label,
                hovertemplate=f"{label}: %{{y:.2f}}<extra></extra>",
            )
        )
    fig.add_vline(
        x=current,
        line=dict(color=config.INK, width=1.4, dash="dash"),
        annotation_text=f"limiar {current:.2f}".replace(".", ","),
        annotation_position="top",
        annotation_font=dict(size=10, color=config.INK),
    )
    fig.update_xaxes(title="limiar de alerta", range=[0.10, 0.70])
    fig.update_yaxes(title="métrica", range=[0, 1], tickformat=".0%")
    return _base(fig, height=350, showlegend=True)


def probability_hist(cases: pd.DataFrame, threshold: float) -> go.Figure:
    fig = go.Figure()
    for label, mask, color in [
        ("sem carga alta", cases["carga_alta"] == 0, config.GRAY),
        ("com carga alta", cases["carga_alta"] == 1, config.RED),
    ]:
        fig.add_trace(
            go.Histogram(
                x=cases.loc[mask, "probabilidade"],
                nbinsx=20,
                name=label,
                marker_color=color,
                opacity=0.62,
                hovertemplate="risco %{x:.0%}<br>%{y} cestos<extra>" + label + "</extra>",
            )
        )
    fig.add_vline(
        x=threshold,
        line=dict(color=config.INK, width=1.5, dash="dash"),
        annotation_text=f"limiar {threshold:.2f}".replace(".", ","),
        annotation_position="top right",
        annotation_font=dict(size=10, color=config.INK),
    )
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(title="probabilidade estimada de carga alta", range=[0, 1], tickformat=".0%")
    fig.update_yaxes(title="cestos", rangemode="tozero")
    return _base(fig, height=350, showlegend=True)


def calibration(df: pd.DataFrame, brier: float) -> go.Figure:
    d = df.copy()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            line=dict(color=config.GRAY, width=1, dash="dot"),
            name="calibração perfeita",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["prob_media"],
            y=d["taxa_observada"],
            mode="markers+lines",
            line=dict(color=config.BLUE, width=1.5),
            marker=dict(
                size=np.clip(d["n"] * 0.55, 8, 22),
                color=config.BLUE,
                line=dict(color=config.CARD, width=1),
            ),
            name="ensemble",
            customdata=d["n"],
            hovertemplate=(
                "risco médio: %{x:.1%}<br>taxa observada: %{y:.1%}<br>n = %{customdata}<extra></extra>"
            ),
        )
    )
    fig.update_xaxes(title="probabilidade média prevista", range=[0, 1], tickformat=".0%")
    fig.update_yaxes(title="fração real de carga alta", range=[0, 0.7], tickformat=".0%")
    fig.add_annotation(
        x=0.02,
        y=0.92,
        xref="paper",
        yref="paper",
        text=f"Brier = {brier:.3f}".replace(".", ","),
        showarrow=False,
        font=dict(size=11, color=config.INK),
        bgcolor=config.CARD,
        bordercolor=config.RULE,
        borderwidth=1,
    )
    return _base(fig, height=340, showlegend=True)


def outcome_bars(df: pd.DataFrame, metric: str, label: str, *, percent: bool = False, height: int = 250) -> go.Figure:
    d = df.copy()
    order = ["VN", "FP", "FN", "VP"]
    d["ordem"] = d["resultado"].map({k: i for i, k in enumerate(order)})
    d = d.sort_values("ordem")
    colors = {"VN": config.GRAY, "FP": config.AMBER, "FN": config.RED, "VP": config.BLUE}
    text = [_pct(v, 1) if percent else f"{v:.1f}".replace(".", ",") for v in d[metric]]
    fig = go.Figure(
        go.Bar(
            y=d["resultado"],
            x=d[metric],
            orientation="h",
            marker_color=[colors.get(r, config.GRAY) for r in d["resultado"]],
            marker_line_width=0,
            text=text,
            textposition="outside",
            textfont=dict(size=10, color=config.INK),
            cliponaxis=False,
            customdata=np.stack([d["n"], d["resultado_label"]], axis=-1),
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>" + label + ": %{x}<br>n = %{customdata[0]}<extra></extra>"
            ),
        )
    )
    max_value = float(d[metric].max()) if not d.empty else 1.0
    fig.update_xaxes(
        title=label,
        tickformat=".0%" if percent else None,
        range=[0, max_value * 1.28 if max_value > 0 else 1],
    )
    fig.update_yaxes(title=None)
    fig = _base(fig, height=height)
    fig.update_layout(margin=dict(r=42))
    return fig


def business_bars(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=d["cenario"],
            y=d["modelo"],
            name="ensemble",
            marker_color=config.RED,
            marker_line_width=0,
            text=[f"R$ {v:+.1f} mi".replace(".", ",") for v in d["modelo"]],
            textposition="outside",
            textfont=dict(size=11, color=config.INK),
            hovertemplate="<b>%{x}</b><br>ensemble: R$ %{y:+.2f} mi<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=d["cenario"],
            y=d["regra_volume"],
            name="regra por volume",
            marker_color=config.GRAY,
            marker_line_width=0,
            text=[f"R$ {v:+.1f} mi".replace(".", ",") for v in d["regra_volume"]],
            textposition="outside",
            textfont=dict(size=10, color=config.MUTED),
            hovertemplate="<b>%{x}</b><br>regra por volume: R$ %{y:+.2f} mi<extra></extra>",
        )
    )
    fig.add_hline(y=0, line=dict(color=config.INK, width=1))
    fig.update_yaxes(title="R$ milhões", zeroline=False)
    fig.update_layout(barmode="group")
    return _base(fig, height=370, showlegend=True)


def band_stacked(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    order = ["verde", "amarelo", "vermelho"]
    colors = {"verde": config.GREEN, "amarelo": config.AMBER, "vermelho": config.RED}
    total = d["n"].sum()
    fig = go.Figure()
    left = 0
    for band in order:
        row = d.loc[d["banda"] == band]
        if row.empty:
            continue
        n = int(row["n"].iloc[0])
        rate = float(row["taxa"].iloc[0])
        fig.add_trace(
            go.Bar(
                y=["holdout"],
                x=[n],
                orientation="h",
                name=band,
                marker_color=colors[band],
                marker_line_width=0,
                text=[f"{n} cestos · {rate:.1%} com evento"],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(size=11, color="white"),
                hovertemplate=f"<b>{band}</b><br>{n} cestos<br>taxa de evento: {rate:.1%}<extra></extra>",
            )
        )
        left += n
    fig.update_layout(barmode="stack")
    fig.update_xaxes(visible=False, range=[0, total])
    fig.update_yaxes(visible=False)
    return _base(fig, height=150, showlegend=True)


def contribution_bars(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    colors = [config.RED if v > 0 else config.BLUE for v in d["contrib"]]
    fig = go.Figure(
        go.Bar(
            y=d["label"],
            x=d["contrib"],
            orientation="h",
            marker_color=colors,
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>contribuição: %{x:+.2f}<extra></extra>",
        )
    )
    fig.add_vline(x=0, line=dict(color=config.INK, width=1))
    fig.update_xaxes(title="contribuição no log-odds (vermelho = aumenta risco)")
    fig.update_yaxes(title=None)
    return _base(fig, height=max(260, 36 * len(d)))


def family_bars(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    colors = [config.RED if v > 0 else config.BLUE for v in d["contrib"]]
    fig = go.Figure(
        go.Bar(
            y=d["family"],
            x=d["contrib"],
            orientation="h",
            marker_color=colors,
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>soma: %{x:+.2f}<extra></extra>",
        )
    )
    fig.add_vline(x=0, line=dict(color=config.INK, width=1))
    fig.update_xaxes(title="soma das contribuições por família")
    fig.update_yaxes(title=None)
    return _base(fig, height=250)
