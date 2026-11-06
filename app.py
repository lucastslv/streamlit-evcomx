"""EVCOMX — app editorial sobre carga alta no forno elétrico a arco."""

from __future__ import annotations

import streamlit as st

from evcomx_app import config, ui
from evcomx_app.sections import business, diagnosis, errors, method, model, overview, simulator

st.set_page_config(
    page_title="Carga Alta · EVCOMX",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="auto",
)

ui.inject_css()

OPTIONS = list(config.SECTIONS.keys())
if "section" not in st.session_state or st.session_state.section not in OPTIONS:
    st.session_state.section = OPTIONS[0]
if "nav_widget" not in st.session_state or st.session_state.nav_widget not in OPTIONS:
    st.session_state.nav_widget = st.session_state.section


def _sync_nav() -> None:
    st.session_state.section = st.session_state.nav_widget


with st.sidebar:
    ui.render_html(
        """
        <div class="brand">
            <div class="brand-eyebrow">EVCOMX · BOOTCAMP</div>
            <div class="brand-title">Carga Alta</div>
            <div class="brand-sub">Dados, risco e decisão no pátio de metálicos.</div>
        </div>
        """
    )
    st.radio(
        "Navegação",
        OPTIONS,
        key="nav_widget",
        on_change=_sync_nav,
        label_visibility="collapsed",
    )
    ui.render_html(
        """
        <div class="sidebar-note">
            <strong>1.799 corridas</strong> · ago/2025 a ago/2026<br>
            43.405 camadas · 3.501 cestos com composição<br><br>
            Uma leitura observacional. O piloto no pátio é o próximo teste.
        </div>
        """
    )

RENDERERS = {
    "overview": overview.render,
    "diagnosis": diagnosis.render,
    "model": model.render,
    "errors": errors.render,
    "simulator": simulator.render,
    "business": business.render,
    "method": method.render,
}

RENDERERS[config.SECTIONS[st.session_state.section]]()
