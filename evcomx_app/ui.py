"""Componentes visuais e CSS da identidade EVCOMX."""

from __future__ import annotations

import base64
import html
import re
import textwrap
from functools import lru_cache
from typing import Iterable

import streamlit as st

from . import config


CSS = f"""
<style>
:root {{
    --paper: {config.PAPER};
    --card: {config.CARD};
    --ink: {config.INK};
    --dark: {config.DARK};
    --muted: {config.MUTED};
    --rule: {config.RULE};
    --red: {config.RED};
    --red-soft: {config.RED_SOFT};
    --blue: {config.BLUE};
    --green: {config.GREEN};
    --amber: {config.AMBER};
}}

html, body, [class*="css"] {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    color: var(--ink);
}}

.stApp {{
    background: var(--paper);
}}

header[data-testid="stHeader"] {{
    background: transparent;
}}

#MainMenu, footer {{ visibility: hidden; }}

[data-testid="stAppDeployButton"], [data-testid="stToolbar"] {{
    display: none;
}}

.block-container {{
    max-width: 1180px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
}}

h1, h2, h3, h4 {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    color: var(--ink);
    letter-spacing: -0.015em;
}}

p, li, .stMarkdown {{
    font-size: 1rem;
    line-height: 1.65;
}}

a {{
    color: var(--blue);
    text-decoration-thickness: 1px;
    text-underline-offset: 2px;
}}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {{
    background: #EFE9DC;
    border-right: 1px solid var(--rule);
}}

[data-testid="stSidebar"] .block-container {{
    padding-top: 1.4rem;
}}

.brand {{
    padding: 0.35rem 0.2rem 1.25rem 0.2rem;
    border-bottom: 1px solid var(--rule);
    margin-bottom: 1rem;
}}

.brand-eyebrow {{
    font-size: 0.66rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 700;
    margin-bottom: 0.45rem;
}}

.brand-title {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: 1.9rem;
    line-height: 1.0;
    font-weight: 700;
    letter-spacing: -0.03em;
}}

.brand-sub {{
    font-size: 0.82rem;
    line-height: 1.45;
    color: var(--muted);
    margin-top: 0.55rem;
}}

[data-testid="stSidebar"] [role="radiogroup"] {{
    gap: 0.1rem;
}}

[data-testid="stSidebar"] [role="radiogroup"] label {{
    padding: 0.5rem 0.55rem;
    border-radius: 6px;
    transition: background 120ms ease;
}}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
    background: rgba(28, 27, 24, 0.05);
}}

[data-testid="stSidebar"] [role="radiogroup"] label p {{
    font-size: 0.9rem;
    font-weight: 500;
}}

.sidebar-note {{
    font-size: 0.72rem;
    line-height: 1.5;
    color: var(--muted);
    border-top: 1px solid var(--rule);
    padding-top: 0.8rem;
    margin-top: 1rem;
}}

/* ---------- editorial blocks ---------- */
.hero {{
    border-top: 5px solid var(--ink);
    padding-top: 1.1rem;
    margin-bottom: 2rem;
}}

.eyebrow {{
    font-size: 0.7rem;
    letter-spacing: 0.19em;
    text-transform: uppercase;
    color: var(--red);
    font-weight: 700;
    margin-bottom: 0.8rem;
}}

.hero-title {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: clamp(2.4rem, 5.2vw, 4.6rem);
    line-height: 0.98;
    letter-spacing: -0.045em;
    font-weight: 700;
    max-width: 950px;
    margin: 0 0 1rem 0;
}}

.hero-deck {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: clamp(1.05rem, 1.8vw, 1.35rem);
    line-height: 1.5;
    color: #3E3A32;
    max-width: 800px;
    margin-bottom: 1rem;
}}

.hero-meta {{
    font-size: 0.76rem;
    color: var(--muted);
    letter-spacing: 0.02em;
}}

.section {{
    margin-top: 2.4rem;
    margin-bottom: 1.1rem;
}}

.section-head {{
    display: flex;
    gap: 0.85rem;
    align-items: baseline;
    border-top: 1px solid var(--rule);
    padding-top: 1.1rem;
}}

.section-num {{
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--red);
    white-space: nowrap;
}}

.section-title {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: clamp(1.45rem, 2.6vw, 2.05rem);
    line-height: 1.12;
    font-weight: 700;
    letter-spacing: -0.025em;
    margin: 0;
}}

.section-deck {{
    font-size: 0.95rem;
    color: var(--muted);
    line-height: 1.55;
    max-width: 820px;
    margin: 0.45rem 0 1.15rem 1.85rem;
}}

.chart-title {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: 1.03rem;
    font-weight: 700;
    line-height: 1.25;
    margin: 0.2rem 0 0.1rem 0;
}}

.chart-deck {{
    font-size: 0.78rem;
    color: var(--muted);
    line-height: 1.45;
    margin-bottom: 0.4rem;
}}

.source {{
    font-size: 0.69rem;
    color: var(--muted);
    line-height: 1.5;
    margin-top: 0.25rem;
}}

.source code {{
    font-size: 0.68rem;
    background: transparent;
}}

/* ---------- KPI cards ---------- */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.8rem;
    margin: 0.75rem 0 1.3rem 0;
}}

.kpi {{
    background: var(--card);
    border: 1px solid var(--rule);
    border-top: 3px solid var(--ink);
    padding: 0.95rem 1rem 0.9rem 1rem;
    min-height: 118px;
}}

.kpi.red {{ border-top-color: var(--red); }}
.kpi.blue {{ border-top-color: var(--blue); }}
.kpi.green {{ border-top-color: var(--green); }}
.kpi.amber {{ border-top-color: var(--amber); }}

.kpi-value {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: clamp(1.65rem, 3vw, 2.35rem);
    line-height: 1.0;
    font-weight: 700;
    letter-spacing: -0.035em;
    margin-bottom: 0.35rem;
}}

.kpi-label {{
    font-size: 0.78rem;
    font-weight: 600;
    line-height: 1.3;
    color: var(--ink);
}}

.kpi-note {{
    font-size: 0.7rem;
    line-height: 1.35;
    color: var(--muted);
    margin-top: 0.3rem;
}}

/* ---------- callouts ---------- */
.callout {{
    background: var(--card);
    border: 1px solid var(--rule);
    border-left: 4px solid var(--blue);
    padding: 0.9rem 1rem;
    margin: 0.85rem 0;
    font-size: 0.9rem;
    line-height: 1.55;
}}

.callout.red {{ border-left-color: var(--red); }}
.callout.amber {{ border-left-color: var(--amber); }}
.callout.green {{ border-left-color: var(--green); }}

.callout-title {{
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--muted);
    margin-bottom: 0.2rem;
}}

.callout p {{ margin: 0; }}

/* ---------- pills and tags ---------- */
.pill {{
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    line-height: 1.2;
}}

.pill.red {{ background: {config.RED_SOFT}; color: #6F1F12; }}
.pill.amber {{ background: {config.AMBER_SOFT}; color: #5B3C00; }}
.pill.green {{ background: {config.GREEN_SOFT}; color: #16462F; }}
.pill.blue {{ background: {config.BLUE_SOFT}; color: #123C4C; }}
.pill.gray {{ background: {config.GRAY_SOFT}; color: #3E3A32; }}

/* ---------- risk scale ---------- */
.risk-wrap {{
    background: var(--card);
    border: 1px solid var(--rule);
    padding: 1.1rem 1.15rem 1rem 1.15rem;
    margin: 0.6rem 0 1rem 0;
}}

.risk-top {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 1rem;
    margin-bottom: 0.65rem;
}}

.risk-number {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: 2.7rem;
    line-height: 0.95;
    font-weight: 700;
    letter-spacing: -0.04em;
}}

.risk-label {{
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 700;
}}

.risk-track {{
    position: relative;
    height: 16px;
    display: flex;
    border-radius: 2px;
    overflow: hidden;
    margin: 0.4rem 0 0.55rem 0;
}}

.risk-seg {{ height: 100%; }}

.risk-marker {{
    position: absolute;
    top: -8px;
    width: 3px;
    height: 32px;
    background: var(--ink);
    transform: translateX(-1.5px);
}}

.risk-ticks {{
    display: flex;
    justify-content: space-between;
    font-size: 0.66rem;
    color: var(--muted);
    margin-top: 0.15rem;
}}

.risk-caption {{
    font-size: 0.72rem;
    color: var(--muted);
    line-height: 1.45;
    margin-top: 0.55rem;
}}

/* ---------- semáforo / band cards ---------- */
.band-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
    margin: 0.8rem 0 1rem 0;
}}

.band-card {{
    border: 1px solid var(--rule);
    background: var(--card);
    padding: 1rem;
    border-top: 5px solid var(--gray);
}}

.band-card.green {{ border-top-color: var(--green); }}
.band-card.amber {{ border-top-color: var(--amber); }}
.band-card.red {{ border-top-color: var(--red); }}

.band-name {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 0.15rem;
}}

.band-range {{
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    margin-bottom: 0.5rem;
}}

.band-card p {{
    font-size: 0.82rem;
    line-height: 1.5;
    margin: 0;
}}

/* ---------- confusion matrix ---------- */
.confusion {{
    display: grid;
    grid-template-columns: 120px 1fr 1fr;
    gap: 4px;
    max-width: 560px;
    margin: 0.4rem 0 0.8rem 0;
}}

.confusion-cell {{
    padding: 0.8rem 0.6rem;
    text-align: center;
    background: var(--card);
    border: 1px solid var(--rule);
    min-height: 82px;
}}

.confusion-head {{
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.confusion-num {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1.1;
}}

.confusion-sub {{
    font-size: 0.66rem;
    color: var(--muted);
    line-height: 1.3;
}}

.confusion-cell.tn {{ background: #F1EEE6; }}
.confusion-cell.tp {{ background: #F4DDD5; }}
.confusion-cell.fp {{ background: #FBF1E1; }}
.confusion-cell.fn {{ background: #F7E9E4; }}

/* ---------- case detail ---------- */
.case-card {{
    background: var(--card);
    border: 1px solid var(--rule);
    padding: 1.1rem;
    margin: 0.5rem 0 1rem 0;
}}

.case-title {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}}

.case-sub {{
    font-size: 0.76rem;
    color: var(--muted);
    margin-bottom: 0.75rem;
}}

.case-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.55rem;
    margin-top: 0.6rem;
}}

.case-stat {{
    border-top: 1px solid var(--rule);
    padding-top: 0.45rem;
}}

.case-stat-label {{
    font-size: 0.66rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    font-weight: 700;
}}

.case-stat-value {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
}}

/* ---------- navigation cards ---------- */
.nav-card {{
    background: var(--card);
    border: 1px solid var(--rule);
    padding: 1rem;
    height: 100%;
    min-height: 150px;
}}

.nav-card .nav-kicker {{
    font-size: 0.66rem;
    color: var(--red);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 700;
    margin-bottom: 0.35rem;
}}

.nav-card .nav-title {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 0.3rem;
}}

.nav-card .nav-text {{
    font-size: 0.8rem;
    color: var(--muted);
    line-height: 1.5;
}}

/* ---------- streamlit widgets ---------- */
.stButton > button {{
    background: var(--ink);
    color: var(--paper);
    border: 1px solid var(--ink);
    border-radius: 4px;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.45rem 0.8rem;
}}

.stButton > button:hover {{
    background: var(--red);
    border-color: var(--red);
    color: white;
}}

.stDownloadButton > button {{
    background: transparent;
    color: var(--ink);
    border: 1px solid var(--rule);
    border-radius: 4px;
    font-size: 0.78rem;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 1.2rem;
    border-bottom: 1px solid var(--rule);
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent;
    padding-left: 0;
    padding-right: 0;
    font-size: 0.85rem;
    font-weight: 600;
}}

.stTabs [aria-selected="true"] {{
    color: var(--red);
    border-bottom-color: var(--red);
}}

div[data-testid="stDataFrame"] {{
    border: 1px solid var(--rule);
}}

div[data-testid="stExpander"] {{
    border: 1px solid var(--rule);
    background: rgba(255, 252, 245, 0.45);
}}

div[data-testid="stExpander"] summary {{
    font-size: 0.85rem;
    font-weight: 600;
}}

.stSlider [data-baseweb="slider"] {{
    padding-top: 0.2rem;
}}

.stSelectbox label, .stNumberInput label, .stSlider label, .stRadio label {{
    font-size: 0.78rem !important;
    color: var(--muted) !important;
    font-weight: 600 !important;
}}

.stAlert {{
    border-radius: 4px;
}}

/* ---------- responsive ---------- */
@media (max-width: 760px) {{
    .block-container {{
        padding-left: 1rem;
        padding-right: 1rem;
    }}
    .band-grid {{
        grid-template-columns: 1fr;
    }}
    .confusion {{
        grid-template-columns: 78px 1fr 1fr;
    }}
    .hero-title {{
        font-size: 2.5rem;
    }}
}}

/* ---------- EVCOMX brand layer ---------- */
html, body, [class*="css"], .stMarkdown, p, li, button, input, select, textarea {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
}}

h1, h2, h3, h4, .hero-title, .section-title, .chart-title,
.kpi-value, .risk-number, .band-name, .case-title, .case-stat-value,
.nav-card .nav-title, .confusion-num, .brand-title,
.hero-deck, .hero-meta, .section-deck, .chart-deck, .source,
.callout, .callout-title, .kpi-label, .kpi-note, .nav-card .nav-text,
.case-sub, .case-stat-label, .band-card p, .risk-label, .risk-caption,
.risk-ticks, .brand-sub, .brand-eyebrow, .sidebar-note, .eyebrow,
.section-num, .pill, .confusion-head, .confusion-sub {{
    font-family: Arial, 'Liberation Sans', 'Helvetica Neue', Helvetica, sans-serif;
}}

.stApp {{
    background: var(--paper);
}}

a {{ color: var(--red); }}

/* sidebar: capa escura da apresentação */
[data-testid="stSidebar"] {{
    background: var(--ink);
    border-right: none;
}}

[data-testid="stSidebar"] .brand {{
    border-bottom: 1px solid #4A5158;
    padding-bottom: 1.1rem;
}}

.sidebar-logo {{
    width: 142px;
    height: auto;
    display: block;
    margin-bottom: 0.9rem;
}}

.brand-eyebrow {{
    color: var(--red);
    letter-spacing: 0.18em;
}}

.brand-title {{
    color: #FFFFFF;
    font-size: 1.75rem;
    letter-spacing: -0.02em;
}}

.brand-sub {{
    color: #C4C4C4;
}}

[data-testid="stSidebar"] [role="radiogroup"] label p {{
    color: #E8E8E8;
}}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
    background: rgba(255, 255, 255, 0.08);
}}

[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] p,
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{
    color: #FFFFFF;
    font-weight: 700;
}}

[data-testid="stSidebar"] .sidebar-note {{
    color: #C4C4C4;
    border-top: 1px solid #4A5158;
}}

/* hero: capa EVCOMX no Overview, faixa branca nas demais páginas */
.hero {{
    border-top: 6px solid var(--red);
    padding-top: 0.9rem;
    margin-bottom: 2.2rem;
}}

.hero-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.2rem;
}}

.hero-brand {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.35rem;
}}

.hero-logo {{
    width: 108px;
    height: auto;
    display: block;
}}

.hero-tagline {{
    font-size: 0.56rem;
    letter-spacing: 0.18em;
    color: #FFFFFF;
    font-weight: 400;
    white-space: nowrap;
}}

.eyebrow {{
    color: var(--red);
    letter-spacing: 0.17em;
    margin-bottom: 0;
}}

.hero-title {{
    font-size: clamp(2rem, 4.2vw, 3.45rem);
    line-height: 1.02;
    letter-spacing: -0.02em;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--ink);
    margin: 0 0 0.9rem 0;
}}

.hero-deck {{
    font-size: clamp(1rem, 1.6vw, 1.16rem);
    line-height: 1.55;
    color: var(--muted);
}}

.hero-meta {{
    color: var(--muted);
}}

.hero.cover {{
    background: var(--ink);
    border-top: none;
    padding: 1.25rem 1.5rem 2.1rem 1.5rem;
    position: relative;
    overflow: hidden;
}}

.hero.cover::before {{
    content: "";
    position: absolute;
    width: 58%;
    height: 260%;
    top: -92%;
    right: -10%;
    background: var(--red);
    transform: rotate(24deg);
}}

.hero.cover::after {{
    content: "";
    position: absolute;
    width: 36%;
    height: 190%;
    bottom: -112%;
    left: -12%;
    background: var(--red);
    transform: rotate(24deg);
    opacity: 0.92;
}}

.hero.cover > * {{
    position: relative;
    z-index: 1;
}}

.hero.cover .hero-title,
.hero.cover .hero-deck,
.hero.cover .hero-meta {{
    color: #FFFFFF;
}}

.hero.cover .hero-title {{
    max-width: 840px;
}}

.hero.cover .hero-deck {{
    color: #FFFFFF;
    max-width: 720px;
}}

.hero.cover .hero-meta {{
    color: #FFFFFF;
    opacity: 0.85;
}}

.hero.cover .eyebrow {{
    color: #FFFFFF;
}}

.hero.cover .hero-logo {{
    width: 132px;
}}

/* seções e títulos */
.section-head {{
    border-top: 1px solid var(--rule);
}}

.section-num {{
    color: var(--red);
    font-size: 0.72rem;
}}

.section-title {{
    font-size: clamp(1.22rem, 2.1vw, 1.72rem);
    line-height: 1.1;
    letter-spacing: -0.01em;
    text-transform: uppercase;
    color: var(--ink);
}}

.section-deck, .chart-deck, .source {{
    color: var(--muted);
}}

.chart-title {{
    font-size: 1rem;
    letter-spacing: -0.01em;
    color: var(--ink);
}}

/* cards: cinza claro com régua laranja, como nos slides */
.kpi, .risk-wrap, .band-card, .case-card, .nav-card {{
    background: var(--card);
    border: none;
    border-top: 4px solid var(--red);
    border-radius: 0;
}}

.kpi.red, .kpi.blue, .kpi.green, .kpi.amber {{
    border-top-color: var(--red);
}}

.kpi-value {{
    color: var(--red);
    font-size: clamp(1.8rem, 3.1vw, 2.45rem);
    letter-spacing: -0.02em;
}}

.kpi-label {{
    font-size: 0.8rem;
    font-weight: 700;
}}

.kpi-note {{
    color: var(--muted);
}}

.nav-card .nav-kicker,
.case-stat-label,
.band-range {{
    color: var(--red);
}}

.nav-card .nav-title,
.case-title,
.band-name {{
    color: var(--ink);
}}

.band-card.green {{ border-top-color: var(--green); }}
.band-card.amber {{ border-top-color: var(--amber); }}
.band-card.red {{ border-top-color: var(--red); }}

.band-card p, .nav-card .nav-text, .case-sub {{
    color: var(--muted);
}}

/* callouts: barras escuras para decisões, cinza para leitura */
.callout {{
    background: var(--card);
    border: none;
    border-left: 6px solid var(--ink);
    border-radius: 0;
}}

.callout.red {{
    background: var(--ink);
    color: #FFFFFF;
    border-left-color: var(--red);
}}

.callout.red .callout-title {{
    color: var(--red);
}}

.callout.amber {{ border-left-color: var(--amber); }}
.callout.green {{ border-left-color: var(--green); }}
.callout.blue {{ border-left-color: var(--ink); }}

.callout-title {{
    color: var(--muted);
    letter-spacing: 0.12em;
}}

/* matriz e demais componentes */
.confusion-cell {{
    background: var(--card);
    border: none;
    border-top: 3px solid var(--rule);
}}

.confusion-cell.tn {{ background: #E6E6E6; border-top-color: var(--gray); }}
.confusion-cell.tp {{ background: var(--red-soft, #FFD8CC); border-top-color: var(--red); }}
.confusion-cell.fp {{ background: #F4E3B8; border-top-color: var(--amber); }}
.confusion-cell.fn {{ background: #F0F0F0; border-top-color: var(--ink); }}

.confusion-num {{
    font-size: 1.55rem;
}}

.risk-marker {{ background: var(--ink); }}

.risk-number, .case-stat-value {{
    color: var(--red);
}}

/* widgets */
.stButton > button {{
    background: var(--ink);
    border-color: var(--ink);
    color: #FFFFFF;
    border-radius: 0;
    font-family: Arial, 'Liberation Sans', sans-serif;
    font-weight: 700;
}}

.stButton > button:hover {{
    background: var(--red);
    border-color: var(--red);
}}

.stDownloadButton > button {{
    border-radius: 0;
    border-color: var(--rule);
    color: var(--ink);
}}

div[data-testid="stExpander"] {{
    background: #F7F7F7;
    border: 1px solid var(--rule);
    border-radius: 0;
}}

div[data-testid="stDataFrame"] {{
    border: 1px solid var(--rule);
}}

.stTabs [aria-selected="true"] {{
    color: var(--red);
    border-bottom-color: var(--red);
}}

.stSelectbox label, .stNumberInput label, .stSlider label, .stRadio label {{
    color: var(--muted) !important;
}}

/* responsivo */
@media (max-width: 760px) {{
    .hero.cover {{
        padding: 1rem 1rem 1.6rem 1rem;
    }}
    .hero-title {{
        font-size: 2.15rem;
    }}
    .hero-logo {{
        width: 88px;
    }}
    .hero.cover .hero-logo {{
        width: 100px;
    }}
}}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def _clean_markup(markup: str) -> str:
    """Remove indentação que o Markdown interpretaria como bloco de código."""
    markup = textwrap.dedent(markup).strip()
    return re.sub(r">\s+<", "><", markup)


def render_html(markup: str) -> None:
    st.markdown(_clean_markup(markup), unsafe_allow_html=True)


def esc(value: object) -> str:
    return html.escape(str(value))


@lru_cache(maxsize=4)
def logo_data_uri(variant: str = "dark") -> str:
    path = config.ASSETS / f"evcomx_logo_{variant}.png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def hero(
    eyebrow: str,
    title: str,
    deck: str,
    meta: str | None = None,
    *,
    variant: str = "light",
) -> None:
    meta_html = f'<div class="hero-meta">{esc(meta)}</div>' if meta else ""
    logo = logo_data_uri("white" if variant == "cover" else "dark")
    variant_class = " cover" if variant == "cover" else ""
    tagline = (
        '<div class="hero-tagline">VIVEMOS GRANDES INDÚSTRIAS</div>'
        if variant == "cover"
        else ""
    )
    render_html(
        f"""
        <div class="hero{variant_class}">
            <div class="hero-top">
                <div class="eyebrow">{esc(eyebrow)}</div>
                <div class="hero-brand">
                    <img class="hero-logo" src="{logo}" alt="EVCOMX">
                    {tagline}
                </div>
            </div>
            <div class="hero-title">{esc(title)}</div>
            <div class="hero-deck">{esc(deck)}</div>
            {meta_html}
        </div>
        """
    )


def section(number: str, title: str, deck: str | None = None) -> None:
    deck_html = f'<div class="section-deck">{esc(deck)}</div>' if deck else ""
    render_html(
        f"""
        <div class="section">
            <div class="section-head">
                <div class="section-num">{esc(number)}</div>
                <h2 class="section-title">{esc(title)}</h2>
            </div>
            {deck_html}
        </div>
        """
    )


def chart_header(title: str, deck: str | None = None) -> None:
    deck_html = f'<div class="chart-deck">{esc(deck)}</div>' if deck else ""
    render_html(f'<div class="chart-title">{esc(title)}</div>{deck_html}')


def source(text: str) -> None:
    render_html(f'<div class="source">{text}</div>')


def callout(text: str, kind: str = "blue", title: str | None = None) -> None:
    title_html = f'<div class="callout-title">{esc(title)}</div>' if title else ""
    color_class = "" if kind == "blue" else kind
    render_html(f'<div class="callout {color_class}">{title_html}<p>{text}</p></div>')


def kpi_row(items: Iterable[dict]) -> None:
    cards = []
    for item in items:
        tone = item.get("tone", "")
        cards.append(
            f"""
            <div class="kpi {tone}">
                <div class="kpi-value">{esc(item["value"])}</div>
                <div class="kpi-label">{esc(item["label"])}</div>
                <div class="kpi-note">{esc(item.get("note", ""))}</div>
            </div>
            """
        )
    render_html('<div class="kpi-grid">' + "".join(cards) + "</div>")


def pill(text: str, kind: str = "gray") -> str:
    return f'<span class="pill {kind}">{esc(text)}</span>'


def risk_scale(
    probability: float,
    *,
    low_cut: float = 0.50,
    high_cut: float = 0.75,
    label: str = "Risco estimado",
    caption: str | None = None,
    value_text: str | None = None,
) -> None:
    """Escala horizontal com marcador. Aqui as faixas são percentis, não 30/45."""
    p = max(0.0, min(1.0, float(probability)))
    value = value_text or f"{p:.0%}"
    caption_html = f'<div class="risk-caption">{caption}</div>' if caption else ""
    render_html(
        f"""
        <div class="risk-wrap">
            <div class="risk-top">
                <div>
                    <div class="risk-label">{esc(label)}</div>
                    <div class="risk-number">{esc(value)}</div>
                </div>
            </div>
            <div class="risk-track">
                <div class="risk-seg" style="width:{low_cut*100:.1f}%;background:{config.GREEN_SOFT};"></div>
                <div class="risk-seg" style="width:{(high_cut-low_cut)*100:.1f}%;background:{config.AMBER_SOFT};"></div>
                <div class="risk-seg" style="width:{(1-high_cut)*100:.1f}%;background:{config.RED_SOFT};"></div>
                <div class="risk-marker" style="left:{p*100:.1f}%;"></div>
            </div>
            <div class="risk-ticks">
                <span>baixo</span><span>atenção</span><span>alto</span>
            </div>
            {caption_html}
        </div>
        """
    )


def semaforo_cards() -> None:
    render_html(
        f"""
        <div class="band-grid">
            <div class="band-card green">
                <div class="band-name">Verde</div>
                <div class="band-range">risco &lt; 30%</div>
                <p><strong>Liberar o cestão.</strong> Cesto denso e bem compactado; segue direto para o forno.</p>
            </div>
            <div class="band-card amber">
                <div class="band-name">Amarelo</div>
                <div class="band-range">30% a 45%</div>
                <p><strong>Atenção no despejo.</strong> Composição limítrofe; orientar centralização e velocidade controlada.</p>
            </div>
            <div class="band-card red">
                <div class="band-name">Vermelho</div>
                <div class="band-range">risco ≥ 45%</div>
                <p><strong>Agir no pátio.</strong> Compactar o topo ou adicionar 2–3 t de material pesado antes do forno.</p>
            </div>
        </div>
        """
    )


def confusion_matrix(tn: int, fp: int, fn: int, vp: int) -> None:
    render_html(
        f"""
        <div class="confusion">
            <div class="confusion-head"></div>
            <div class="confusion-head">Previsto normal</div>
            <div class="confusion-head">Previsto carga alta</div>

            <div class="confusion-head" style="justify-content:flex-start;">Real normal</div>
            <div class="confusion-cell tn">
                <div class="confusion-num">{tn}</div>
                <div class="confusion-sub">verdadeiro negativo</div>
            </div>
            <div class="confusion-cell fp">
                <div class="confusion-num">{fp}</div>
                <div class="confusion-sub">falso positivo</div>
            </div>

            <div class="confusion-head" style="justify-content:flex-start;">Real carga alta</div>
            <div class="confusion-cell fn">
                <div class="confusion-num">{fn}</div>
                <div class="confusion-sub">falso negativo</div>
            </div>
            <div class="confusion-cell tp">
                <div class="confusion-num">{vp}</div>
                <div class="confusion-sub">verdadeiro positivo</div>
            </div>
        </div>
        """
    )


def case_card(
    title: str,
    subtitle: str,
    stats: Iterable[tuple[str, str]],
    *,
    pill_html: str | None = None,
) -> None:
    stats_html = "".join(
        f'<div class="case-stat"><div class="case-stat-label">{esc(k)}</div>'
        f'<div class="case-stat-value">{esc(v)}</div></div>'
        for k, v in stats
    )
    pill_html = pill_html or ""
    render_html(
        f"""
        <div class="case-card">
            <div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;">
                <div>
                    <div class="case-title">{esc(title)}</div>
                    <div class="case-sub">{esc(subtitle)}</div>
                </div>
                <div>{pill_html}</div>
            </div>
            <div class="case-grid">{stats_html}</div>
        </div>
        """
    )
