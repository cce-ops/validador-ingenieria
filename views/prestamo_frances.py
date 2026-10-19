"""Simulador de Préstamo Francés y TAE.

Logica basada en el documento "Financiación y préstamos v3".

Formulas
--------
Tipo efectivo por periodo:
    Im = i_m / m        (i_m = TIN nominal anual; m = periodos de capitalizacion al año)

TAE (Tasa Anual Equivalente):
    TAE = (1 + Im)^m - 1 = (1 + i_m/m)^m - 1

Cuota periodica constante (prestamo frances):
    a = C0 * Im / (1 - (1 + Im)^-n)

Cuadro de amortizacion, para cada periodo r:
    Yr = R_{r-1} * Im          (cuota de intereses)
    Ar = a - Yr                (cuota de capital)
    Rr = R_{r-1} - Ar          (deuda pendiente despues del periodo r)
    R0 = C0
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def tipo_efectivo(tin, m):
    """Tipo de interes efectivo por periodo de capitalizacion."""
    return tin / m


def tae(tin, m):
    """Tasa Anual Equivalente a partir del TIN nominal y m."""
    return (1 + tin / m) ** m - 1


def cuota(c0, im, n):
    """Cuota periodica constante del prestamo frances."""
    return c0 * im / (1 - (1 + im) ** -n)


def tabla_amortizacion(c0, im, n, a):
    """Devuelve un DataFrame con el cuadro de amortizacion completo."""
    filas = []
    R = c0
    capital_amortizado_acum = 0.0
    intereses_acum = 0.0
    for r in range(0, int(n) + 1):
        if r == 0:
            filas.append(
                {
                    "Periodo r": r,
                    "Cuota a (€)": None,
                    "Intereses Yr (€)": None,
                    "Capital Ar (€)": None,
                    "Deuda pendiente Rr (€)": round(R, 2),
                    "Capital amortizado acumulado (€)": 0.0,
                    "Intereses acumulados (€)": 0.0,
                }
            )
            continue
        Y = R * im
        A = a - Y
        R = R - A
        intereses_acum += Y
        capital_amortizado_acum += A
        # Corrige posible residuo de redondeo en el ultimo periodo
        if r == int(n):
            R = 0.0
        filas.append(
            {
                "Periodo r": r,
                "Cuota a (€)": round(a, 2),
                "Intereses Yr (€)": round(Y, 2),
                "Capital Ar (€)": round(A, 2),
                "Deuda pendiente Rr (€)": round(max(R, 0.0), 2),
                "Capital amortizado acumulado (€)": round(capital_amortizado_acum, 2),
                "Intereses acumulados (€)": round(intereses_acum, 2),
            }
        )
    return pd.DataFrame(filas)


def render() -> None:
    """Dibuja el simulador de prestamo frances y TAE."""
    st.markdown(
        "Introduce las condiciones del préstamo y la app construye el cuadro de "
        "amortización mensual o trimestral, calcula la TAE y te permite "
        "certificar que tu ejercicio está bien resuelto."
    )

    with st.expander("ℹ️ Ayuda y formulas", expanded=False):
        st.markdown(
            """
**Tipos de interés**

- **TIN** (`i_m`): tipo de interés nominal anual que declara el banco, sin
  considerar la capitalización dentro del año.
- **Tipo efectivo por periodo** `Im = i_m / m` (1 % trimestral si TIN 4 % y m = 4).
- **TAE** = tipo de interés efectivo anual que tiene en cuenta la capitalización:

$$
TAE = (1 + \\frac{i_m}{m})^m - 1
$$

Permite comparar préstamos con distintos periodos de capitalización.

**Préstamo francés (cuotas constantes)**

$$
a = \\frac{C_0 \\cdot I_m}{1 - (1 + I_m)^{-n}}
$$

donde `n` es el número total de periodos (`años × m`). Equivale a
`=PAGO(Im; n; -C0)` en Excel.

**Cuadro de amortización (periodo r)**

$$
Y_r = R_{r-1} \\cdot I_m \\qquad
A_r = a - Y_r \\qquad
R_r = R_{r-1} - A_r \\qquad
a = Y_r + A_r
$$

- `a`: cuota constante (siempre igual).
- `Yr`: parte de la cuota que paga intereses.
- `Ar`: parte de la cuota que amortiza capital.
- `Rr`: deuda pendiente después del periodo r.

> Ejemplo del documento: C0 = 100.000 €, 5 años, TIN 6,5 % nominal, capitalización
> mensual (m = 12, n = 60).
> Im = 0,065/12 · a = 1.956,61 €/mes · Total pagado ≈ 117.397 € ·
> Intereses totales ≈ 17.397 €.
            """
        )

    st.markdown("---")
    st.subheader("⚙️ Condiciones del préstamo")

    col1, col2, col3 = st.columns(3)
    with col1:
        c0 = st.number_input(
            "Capital inicial C0 (€)",
            min_value=100.0,
            value=100000.0,
            step=1000.0,
            key="prestamo__c0",
        )
        tin = st.number_input(
            "TIN nominal anual (%)",
            min_value=0.0,
            max_value=100.0,
            value=6.5,
            step=0.05,
            key="prestamo__tin",
            help="Tipo de interés nominal anual declarado por el banco.",
        )
    with col2:
        m_opcion = st.selectbox(
            "Capitalización",
            options=[("Mensual (m = 12)", 12), ("Trimestral (m = 4)", 4), ("Anual (m = 1)", 1)],
            index=0,
            key="prestamo__m_opcion",
            format_func=lambda x: x[0],
        )
        m = m_opcion[1]
        anos = st.number_input(
            "Plazo (años)",
            min_value=0.5,
            max_value=50.0,
            value=5.0,
            step=0.5,
            key="prestamo__anos",
        )
    with col3:
        st.markdown(" ")  # alineado visual
        st.markdown(" ")
        calcular_btn = st.button("Calcular préstamo", key="prestamo__calcular", type="primary")

    n = anos * m
    im = tipo_efectivo(tin / 100, m)
    tae_val = tae(tin / 100, m)
    a_val = cuota(c0, im, n)
    total_pagado = a_val * n
    intereses_totales = total_pagado - c0

    # Calcular siempre (como la app original de viabilidad: recalcula en vivo)
    df = tabla_amortizacion(c0, im, n, a_val)

    st.markdown("---")
    st.subheader("📊 Resultados del préstamo")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Tipo efectivo por periodo Im", f"{im*100:.4f} %")
    r2.metric("TAE (Tasa Anual Equivalente)", f"{tae_val*100:.2f} %")
    r3.metric("Cuota periodica constante a", f"{a_val:,.2f} €")
    r4.metric("Numero de periodos n", f"{int(n)}")

    r5, r6 = st.columns(2)
    r5.metric("Total pagado (a × n)", f"{total_pagado:,.2f} €")
    r6.metric("Intereses totales", f"{intereses_totales:,.2f} €")

    st.markdown("#### Equivalencia TIN ↔ TAE")
    st.write(
        f"TIN {tin:g} % nominal con capitalización {'mensual' if m==12 else 'trimestral' if m==4 else 'anual'} "
        f"(m = {m}) → **TAE = {tae_val*100:.2f} %**. "
        f"Es el tipo efectivo anual real; úsalo para comparar préstamos."
    )

    # --- Cuadro de amortizacion ---
    st.markdown("---")
    st.subheader("📋 Cuadro de amortización")

    mostrar = st.slider(
        "Cuántos periodos mostrar de la tabla",
        min_value=5,
        max_value=len(df),
        value=min(20, len(df)),
        step=5,
        key="prestamo__mostrar",
    )

    df_show = df.head(mostrar).copy()
    st.dataframe(
        df_show.style.format(
            {
                "Cuota a (€)": "{:,.2f}",
                "Intereses Yr (€)": "{:,.2f}",
                "Capital Ar (€)": "{:,.2f}",
                "Deuda pendiente Rr (€)": "{:,.2f}",
                "Capital amortizado acumulado (€)": "{:,.2f}",
                "Intereses acumulados (€)": "{:,.2f}",
            },
            na_rep="-",
        ),
        width="stretch",
        hide_index=True,
    )

    if mostrar < len(df):
        st.caption(
            f"Mostrando los primeros {mostrar} de {len(df)-1} periodos de amortización. "
            f"En el periodo {int(n)} la deuda queda en 0,00 €."
        )

    # --- Grafica ---
    st.markdown("#### Evolución de la deuda y estructura de la cuota")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Periodo r"],
            y=df["Deuda pendiente Rr (€)"],
            mode="lines+markers",
            name="Deuda pendiente Rr",
            line=dict(color="#1f77b4", width=3),
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Periodo r"],
            y=df["Intereses Yr (€)"],
            name="Intereses Yr",
            marker_color="#d62728",
            opacity=0.7,
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Periodo r"],
            y=df["Capital Ar (€)"],
            name="Capital Ar",
            marker_color="#2ca02c",
            opacity=0.7,
        )
    )
    fig.update_layout(
        title="Amortización del préstamo francés",
        xaxis_title="Periodo r",
        yaxis_title="Euros (€)",
        barmode="overlay",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, width="stretch")

    # --- Autocertificacion del alumno ---
    st.markdown("---")
    st.subheader("✅ Certifica tu ejercicio")
    st.markdown(
        "Introduce la cuota y la TAE que tú has calculado y la app te dirá si "
        "coinciden (tolerancia ±0,01 € en la cuota, ±0,01 pp en la TAE)."
    )
    c1, c2 = st.columns(2)
    with c1:
        a_usuario = st.number_input(
            "Tu cuota a (€)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            key="prestamo__usuario_a",
        )
    with c2:
        tae_usuario = st.number_input(
            "Tu TAE (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.01,
            key="prestamo__usuario_tae",
        )

    errores = []
    if a_usuario != 0 and abs(a_usuario - a_val) > 0.01:
        errores.append(
            f"Cuota: esperada {a_val:,.2f} €, tú pusiste {a_usuario:,.2f} €"
        )
    if tae_usuario != 0 and abs(tae_usuario - tae_val * 100) > 0.01:
        errores.append(
            f"TAE: esperada {tae_val*100:.2f} %, tú pusiste {tae_usuario:.2f} %"
        )

    if (a_usuario != 0 or tae_usuario != 0) and not errores:
        st.success(
            "🎉 **Ejercicio correcto.** La cuota y la TAE coinciden con el "
            "cálculo de la app. Tu ejercicio está bien resuelto."
        )
    elif (a_usuario != 0 or tae_usuario != 0) and errores:
        st.error("❌ **Hay diferencias en tu ejercicio:**")
        for e in errores:
            st.write("• " + e)
    else:
        st.info("Introduce al menos un valor para certificarlo.")
