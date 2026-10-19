"""Punto de Equilibrio (Break-Even Point).

Logica basada en el documento "Costes de ingeniería y Punto de Equilibrio v4".

Formulas
--------
Margen unitario:
    Mu = precio de venta unitario p - coste variable unitario cv

Punto de equilibrio (beneficio = 0):
    PE = CF / Mu

Punto de equilibrio con beneficio objetivo Bobjetivo:
    PE_objetivo = (CF + Bobjetivo) / Mu

donde CF son los costes fijos totales anuales.
"""

from __future__ import annotations

import streamlit as st


def render() -> None:
    """Dibuja la calculadora de punto de equilibrio."""
    st.markdown(
        "El punto de equilibrio es el número mínimo de unidades (o proyectos) que "
        "deben venderse al año para que los ingresos totales igualen los costes "
        "totales, es decir, beneficio cero. Introduce los datos de tu ejercicio "
        "y certifica el resultado."
    )

    with st.expander("ℹ️ Ayuda y formulas", expanded=False):
        st.markdown(
            """
**Punto de equilibrio clásico**

$$
PE = \\frac{CF}{M_m}
$$

donde:
 - **CF**: Costes fijos totales anuales (alquiler, personal administrativo fijo,
   seguros…).
 - **Mm**: Margen medio unitario = precio de venta unitario − coste variable
   unitario.

Si se venden varios productos con márgenes distintos, `Mm` es una media
ponderada según la proporción de ventas de cada uno.

**Punto de equilibrio con beneficio objetivo**

$$
PE_{con\\ beneficio} = \\frac{CF + B_{objetivo}}{M_m}
$$

> Ejemplo del documento: CF = 120.000 €/año, precio proyecto 5.000 €,
> coste variable 2.000 €/proyecto.
> Margen unitario = 3.000 € · PE = 120.000 / 3.000 = **40 proyectos/año**.
> Con beneficio objetivo de 60.000 €: PE = (120.000 + 60.000) / 3.000 =
> **60 proyectos/año**.
            """
        )

    st.markdown("---")
    st.subheader("⚙️ Datos de entrada")

    col1, col2, col3 = st.columns(3)
    with col1:
        cf = st.number_input(
            "Costes fijos totales anuales CF (€)",
            min_value=0.0,
            value=120000.0,
            step=1000.0,
            key="pe__cf",
        )
    with col2:
        p = st.number_input(
            "Precio de venta unitario p (€/unidad o proyecto)",
            min_value=0.0,
            value=5000.0,
            step=100.0,
            key="pe__p",
        )
    with col3:
        cv = st.number_input(
            "Coste variable unitario cv (€/unidad o proyecto)",
            min_value=0.0,
            value=2000.0,
            step=100.0,
            key="pe__cv",
        )

    bo = st.number_input(
        "Beneficio objetivo anual B (€) — deja 0 para el punto de equilibrio clásico",
        min_value=0.0,
        value=60000.0,
        step=1000.0,
        key="pe__bo",
        help="Si pones 0, se calcula el punto de equilibrio clásico (beneficio = 0).",
    )

    mu = p - cv
    pe = cf / mu if mu > 0 else None
    pe_objetivo = (cf + bo) / mu if mu > 0 else None

    st.markdown("---")
    st.subheader("📊 Resultados")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Margen unitario Mu = p − cv", f"{mu:,.2f} €")
    if pe is not None:
        r2.metric("Punto de equilibrio PE", f"{pe:,.2f} unidades/año")
        r3.metric("Ingresos en punto de equilibrio", f"{pe * p:,.2f} €")
        r4.metric("Costes variables en PE", f"{pe * cv:,.2f} €")
    else:
        r2.metric("Punto de equilibrio PE", "No alcanzable")
        r3.metric("Ingresos en punto de equilibrio", "—")
        r4.metric("Costes variables en PE", "—")

    if pe_objetivo is not None:
        st.markdown("#### Con beneficio objetivo")
        o1, o2 = st.columns(2)
        o1.metric(
            f"PE con beneficio objetivo {bo:,.0f} €",
            f"{pe_objetivo:,.2f} unidades/año",
        )
        o2.metric(
            "Ingresos necesarios en PE objetivo",
            f"{pe_objetivo * p:,.2f} €",
        )

    if mu <= 0:
        st.warning(
            "El coste variable unitario es mayor o igual al precio de venta, por lo que el "
            "margen es nulo o negativo: nunca se cubre el punto de equilibrio."
        )

    # --- Autocertificacion del alumno ---
    st.markdown("---")
    st.subheader("✅ Certifica tu ejercicio")
    st.markdown(
        "Introduce el punto de equilibrio que tú has calculado y la app te dirá "
        "si coincide (tolerancia ±0,01 unidades)."
    )
    pe_usuario = st.number_input(
        "Tu punto de equilibrio PE (unidades/año)",
        min_value=0.0,
        value=0.0,
        step=0.01,
        key="pe__usuario",
    )

    if pe_usuario != 0 and pe is not None:
        if abs(pe_usuario - pe) <= 0.01:
            st.success(
                f"🎉 **Ejercicio correcto.** El punto de equilibrio es "
                f"{pe:,.2f} unidades/año, coincidiendo con tu valor."
            )
        else:
            st.error(
                f"❌ Diferencia: el punto de equilibrio correcto es "
                f"{pe:,.2f} unidades/año, y tú pusiste {pe_usuario:,.2f}."
            )
    elif pe_usuario != 0 and pe is None:
        st.error(
            "❌ No se puede alcanzar el punto de equilibrio (margen unitario "
            "nulo o negativo)."
        )
    else:
        st.info("Introduce un valor para certificarlo.")
