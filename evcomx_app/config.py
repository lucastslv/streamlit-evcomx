"""Caminhos, constantes e paleta editorial do app."""

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

# Paleta semântica, inspirada na leitura editorial do NYT:
# papel quente, tinta, vermelho para evento/risco, azul para contexto,
# verde para operação segura e âmbar para atenção.
PAPER = "#F6F2E9"
CARD = "#FFFCF5"
INK = "#1C1B18"
MUTED = "#6E685D"
RULE = "#DCD4C4"
LIGHT = "#E9E2D4"
RED = "#B6452F"
RED_SOFT = "#E8C4B8"
BLUE = "#2E657C"
BLUE_SOFT = "#C9DCE3"
GREEN = "#2E7356"
GREEN_SOFT = "#CDE0D6"
AMBER = "#B98319"
AMBER_SOFT = "#EAD7AC"
GRAY = "#989184"
GRAY_SOFT = "#DAD5CA"

COLORS = {
    "paper": PAPER,
    "card": CARD,
    "ink": INK,
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
