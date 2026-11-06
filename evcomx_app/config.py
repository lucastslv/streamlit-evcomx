"""Caminhos, constantes e paleta da identidade visual EVCOMX."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Projetos de origem
DADOS_BOOTCAMP = ROOT / "dados-bootcamp"
PROJETO_BOOTCAMP = ROOT / "projeto-bootcamp"

RAW_DADOS = DADOS_BOOTCAMP / "data" / "raw"
PROCESSED = DADOS_BOOTCAMP / "data" / "processed"
EXTERNAL = DADOS_BOOTCAMP / "data" / "external"

RAW_PROJETO = PROJETO_BOOTCAMP / "data" / "raw"
REPORTS = PROJETO_BOOTCAMP / "relatorios_complementares"
MODELS = PROJETO_BOOTCAMP / "models"

APP_DATA = ROOT / "data" / "app"
APP_MODELS = ROOT / "models"
APP_MODEL_PATH = APP_MODELS / "app_simulator.joblib"
ASSETS = ROOT / "evcomx_app" / "assets"

# Identidade visual EVCOMX, extraída do tema da apresentação final:
# carvão (#2F363E), laranja (#FF4000), cinzas neutros e branco.
PAPER = "#FFFFFF"
CARD = "#F0F0F0"
INK = "#2F363E"
DARK = "#182028"
MUTED = "#6B7076"
RULE = "#D9D9D9"
LIGHT = "#E6E6E6"
RED = "#FF4000"
RED_SOFT = "#FFD8CC"
BLUE = "#2F5D73"
BLUE_SOFT = "#DCE6EA"
GREEN = "#2E7D5B"
GREEN_SOFT = "#D8E8E0"
AMBER = "#C58A00"
AMBER_SOFT = "#F4E3B8"
GRAY = "#8A9096"
GRAY_SOFT = "#E4E5E6"

COLORS = {
    "paper": PAPER,
    "card": CARD,
    "ink": INK,
    "dark": DARK,
    "muted": MUTED,
    "rule": RULE,
    "light": LIGHT,
    "red": RED,
    "red_soft": RED_SOFT,
    "blue": BLUE,
    "blue_soft": BLUE_SOFT,
    "green": GREEN,
    "green_soft": GREEN_SOFT,
    "amber": AMBER,
    "amber_soft": AMBER_SOFT,
    "gray": GRAY,
    "gray_soft": GRAY_SOFT,
}

# Navegação do app (a ordem é a narrativa)
SECTIONS = {
    "Visão geral": "overview",
    "Diagnóstico": "diagnosis",
    "Modelo": "model",
    "Erros & casos": "errors",
    "Simulador": "simulator",
    "Negócio & piloto": "business",
    "Dados & método": "method",
}

SECTION_LABELS = {v: k for k, v in SECTIONS.items()}
