"""Validador Financiero y de Costes de Ingeniería.

Punto de entrada de la aplicación. Su responsabilidad es deliberadamente
pequena:

1. Configurar la pagina UNA vez (Streamlit solo admite una
   set_page_config por app).
2. Repartir las herramientas en tres pestañas de primer nivel.

Cada herramienta conserva su propia logica y su interfaz; todo es calculo
local puro (sin llamadas a red ni API Key), para que el alumnado pueda
usarla libremente y certificar que sus ejercicios estan bien resueltos.

Ejecucion
---------
    streamlit run app.py

La app queda en http://localhost:8501
"""

from __future__ import annotations

import streamlit as st

from views import phd_tarifa, prestamo_frances, punto_equilibrio

# Unica llamada a set_page_config de toda la aplicacion.
st.set_page_config(
    page_title="Validador Financiero y de Costes de Ingeniería",
    page_icon="💶",
    layout="wide",
)

st.title("💶 Validador Financiero y de Costes de Ingeniería")
st.caption(
    "Comprueba la viabilidad económica, el cálculo de tarifas técnicas y la "
    "estructura de préstamos. Herramienta de autocertificación para el "
    "alumnado: introduce tus datos y compara con el resultado de la app para "
    "certificar que tus ejercicios están bien resueltos."
)

# Pestanas de primer nivel, perezosas: solo se ejecuta la que esta visible.
tab_phd, tab_prestamo, tab_pe = st.tabs(
    ["💶 PHD y Tarifa Final", "🏦 Préstamo Francés y TAE", "⚖️ Punto de Equilibrio"],
    on_change="rerun",
    key="nav_principal",
)

if tab_phd.open:
    with tab_phd:
        phd_tarifa.render()

if tab_prestamo.open:
    with tab_prestamo:
        prestamo_frances.render()

if tab_pe.open:
    with tab_pe:
        punto_equilibrio.render()
