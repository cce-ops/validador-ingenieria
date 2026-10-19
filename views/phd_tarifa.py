"""Calculadora de Precio Hora Directa (PHD) y Tarifa Final sin IVA.

Logica basada en el documento "Costes de ingeniería y Punto de Equilibrio v4".

Formulas
--------
PHD = (S + SS + OCD) / H

donde:
 - S: salario bruto anual del tecnico.
 - SS: aportacion patronal a la Seguridad Social = S * %_patronal (defecto 31,57%).
 - OCD: otros costes directos anualizados (formacion, EPI, licencias, material...).
 - H: horas trabajadas al año (tipicamente 1600-1800).

PHT = (1 + delta) * alfa * PHD

donde:
 - alfa: coeficiente de horas indirectas = horas totales / horas productivas
         (tipicamente 1.2 - 1.5).
 - delta: coeficiente de costes indirectos = costes indirectos / costes directos
          (tipicamente 0.5 - 1.5; en ingeniería ~1.4).

Tarifa Final sin IVA = PHT * [1 + m * (1 + tIS)]

donde:
 - m: margen de beneficio sobre el PHT (tipico ingeniería ~9%).
 - tIS: tipo impositivo del Impuesto de Sociedades (25% general, 24% PYME,
        21% microempresa primeros 50.000 €, 15% empresa nueva creacion).

Tarifa con IVA = Tarifa sin IVA * (1 + IVA)   (IVA general servicios 21%).
"""

from __future__ import annotations

import streamlit as st


def calcular(S, ss_pct, ocd, h, alfa, delta, m, tis, iva):
    """Devuelve un diccionario con todos los intermediates y resultados.

    Los redondeos se hacen sobre los importes con dos decimales (c\u00e9ntimos),
    tal y como se muestra en el ejemplo resuelto del documento de referencia,
    as\u00ed el resultado coincide c\u00e9ntimo a c\u00e9ntimo con el c\u00e1lculo del alumno.
    """
    ss = round(S * ss_pct / 100, 2)
    phd = round((S + ss + ocd) / h, 2)
    pht = round((1 + delta) * alfa * phd, 2)
    beneficio = round(m / 100 * pht, 2)
    is_ = round(beneficio * tis / 100, 2)
    tarifa_sin_iva = round(pht + beneficio + is_, 2)
    # Equivalente: pht * (1 + (m/100) * (1 + tis/100))
    tarifa_con_iva = round(tarifa_sin_iva * (1 + iva / 100), 2)
    return {
        "ss": ss,
        "coste_directo_total": S + ss + ocd,
        "phd": phd,
        "pht": pht,
        "beneficio": beneficio,
        "is": is_,
        "tarifa_sin_iva": tarifa_sin_iva,
        "tarifa_con_iva": tarifa_con_iva,
    }


def render() -> None:
    """Dibuja la calculadora de PHD y Tarifa Final."""
    st.markdown(
        "Rellena los datos de tu ejercicio y compara el resultado de la app con "
        "el tuyo. Si coinciden (dentro de una tolerancia del 0,01 €), tu "
        "ejercicio esta **bien resuelto**."
    )

    with st.expander("ℹ️ Ayuda y formulas", expanded=False):
        st.markdown(
            """
**1. Precio Hora Directa (PHD)**

$$
PHD = \\frac{S + SS + OCD}{H}
$$

- **S**: Salario bruto anual del técnico.
- **SS**: Aportación patronal a la Seguridad Social (defecto 31,57 % para
  actividades de oficina/consultoría de ingeniería).
- **OCD**: Otros costes directos anualizados (formación, EPI, licencias,
  material técnico…).
- **H**: Horas trabajadas al año (típicamente 1600–1800).

**2. Precio Hora Total (PHT)**

$$
PHT = (1 + \\delta) \\cdot \\alpha \\cdot PHD
$$

- **α**: Coeficiente de horas indirectas = horas totales / horas productivas
  (típico 1,2 – 1,5).
- **δ**: Coeficiente de costes indirectos = costes indirectos / costes directos
  (típico 0,5 – 1,5; en ingeniería ~1,4).

**3. Tarifa Final al cliente (sin IVA)**

$$
TF = PHT \\cdot [1 + m(1 + t_{IS})]
$$

- **m**: Margen de beneficio sobre el PHT (típico ingeniería ~9 %).
- **tIS**: Tipo impositivo del Impuesto de Sociedades (25 % general, 24 %
  PYME, 21 % microempresa primeros 50.000 €, 15 % empresa nueva creación).

La **tarifa con IVA** se obtiene multiplicando la tarifa sin IVA por
(1 + IVA) — IVA general servicios de ingeniería 21 %. El IVA no es un coste
para la empresa, se repercute al cliente en la factura.

> Ejemplo del documento: S = 30.000 €, H = 1700 h, OCD = 1200 €, SS = 31,57 %,
> α = 1,25, δ = 1,4, m = 9 %, tIS = 24 % (PYME).
> PHD = 23,92 €/h · PHT = 71,76 €/h · Tarifa sin IVA = 79,77 €/h ·
> Tarifa con IVA 21 % = 96,52 €/h.
            """
        )

    st.markdown("---")
    st.subheader("⚙️ Datos de entrada")

    col1, col2, col3 = st.columns(3)
    with col1:
        S = st.number_input(
            "Salario bruto anual S (€)",
            min_value=0.0,
            value=30000.0,
            step=500.0,
            key="phd__S",
            help="Salario bruto anual del técnico, antes de descontar IRPF y cotizaciones.",
        )
        ss_pct = st.number_input(
            "Seguridad Social patronal (%)",
            min_value=0.0,
            max_value=100.0,
            value=31.57,
            step=0.01,
            key="phd__ss",
            help="Aportación de la empresa. 31,57 % es el valor típico para oficina/consultoría de ingeniería (2025).",
        )
        ocd = st.number_input(
            "Otros costes directos anualizados OCD (€)",
            min_value=0.0,
            value=1200.0,
            step=100.0,
            key="phd__ocd",
            help="Formación, EPI, licencias profesionales, material técnico específico…",
        )
    with col2:
        h = st.number_input(
            "Horas trabajadas anuales H",
            min_value=1,
            max_value=3000,
            value=1700,
            step=50,
            key="phd__H",
            help="Típicamente entre 1600 y 1800 horas al año (excluyendo vacaciones y festivos).",
        )
        alfa = st.number_input(
            "Coeficiente de horas indirectas α",
            min_value=1.0,
            max_value=3.0,
            value=1.25,
            step=0.05,
            key="phd__alfa",
            help="Horas totales / horas productivas. Típico 1,2 – 1,5.",
        )
        delta = st.number_input(
            "Coeficiente de costes indirectos δ",
            min_value=0.0,
            max_value=5.0,
            value=1.4,
            step=0.05,
            key="phd__delta",
            help="Costes indirectos / costes directos del personal técnico. Típico 0,5 – 1,5 (ingeniería ~1,4).",
        )
    with col3:
        m = st.number_input(
            "Margen de beneficio m sobre el PHT (%)",
            min_value=0.0,
            max_value=100.0,
            value=9.0,
            step=0.5,
            key="phd__m",
            help="Beneficio empresarial deseado sobre el precio hora total. Típico ingeniería ~9 %.",
        )
        tis = st.number_input(
            "Tipo Impuesto de Sociedades tIS (%)",
            min_value=0.0,
            max_value=50.0,
            value=24.0,
            step=1.0,
            key="phd__tis",
            help="25 % general · 24 % PYME · 21 % microempresa (primeros 50.000 €) · 15 % empresa nueva creación.",
        )
        iva = st.number_input(
            "IVA (%) (solo referencia, tarifa con IVA)",
            min_value=0.0,
            max_value=50.0,
            value=21.0,
            step=1.0,
            key="phd__iva",
            help="IVA general servicios de ingeniería 21 %. Se repercute al cliente, no es coste de empresa.",
        )

    res = calcular(S, ss_pct, ocd, h, alfa, delta, m, tis, iva)

    st.markdown("---")
    st.subheader("📊 Resultados")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Aportación patronal SS", f"{res['ss']:,.2f} €")
    m2.metric("PHD (Precio Hora Directa)", f"{res['phd']:,.2f} €/h")
    m3.metric("PHT (Precio Hora Total)", f"{res['pht']:,.2f} €/h")
    m4.metric("Tarifa Final SIN IVA", f"{res['tarifa_sin_iva']:,.2f} €/h")

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("Beneficio empresarial B = m·PHT", f"{res['beneficio']:,.2f} €/h")
    m6.metric("Impuesto de Sociedades IS", f"{res['is']:,.2f} €/h")
    m7.metric("Tarifa Final CON IVA (21 %)", f"{res['tarifa_con_iva']:,.2f} €/h")
    m8.metric("Coste directo total (S+SS+OCD)", f"{res['coste_directo_total']:,.2f} €/año")

    st.markdown("#### Desglose del cálculo")
    st.write(
        f"**PHD** = ({S:,.2f} + {res['ss']:,.2f} + {ocd:,.2f}) / {h:,} "
        f"= **{res['phd']:,.2f} €/h**"
    )
    st.write(
        f"**PHT** = (1 + {delta}) × {alfa} × {res['phd']:,.2f} "
        f"= **{res['pht']:,.2f} €/h**"
    )
    st.write(
        f"**Tarifa sin IVA** = {res['pht']:,.2f} × [1 + {m/100:.2f}(1 + {tis/100:.2f})] "
        f"= {res['pht']:,.2f} + {res['beneficio']:,.2f} + {res['is']:,.2f} "
        f"= **{res['tarifa_sin_iva']:,.2f} €/h**"
    )
    st.write(
        f"**Tarifa con IVA** = {res['tarifa_sin_iva']:,.2f} × (1 + {iva/100:.2f}) "
        f"= **{res['tarifa_con_iva']:,.2f} €/h**"
    )

    # --- Autocertificacion del alumno ---
    st.markdown("---")
    st.subheader("✅ Certifica tu ejercicio")
    st.markdown(
        "Introduce los valores que tú has obtenido en tu ejercicio y la app te "
        "dirá si coinciden con el cálculo correcto (tolerancia ±0,01 €)."
    )
    c1, c2 = st.columns(2)
    with c1:
        phd_usuario = st.number_input(
            "Tu PHD (€/h)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            key="phd__usuario_phd",
        )
        pht_usuario = st.number_input(
            "Tu PHT (€/h)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            key="phd__usuario_pht",
        )
    with c2:
        tf_usuario = st.number_input(
            "Tu Tarifa Final sin IVA (€/h)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            key="phd__usuario_tf",
        )
        tfiva_usuario = st.number_input(
            "Tu Tarifa Final con IVA (€/h)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            key="phd__usuario_tfiva",
        )

    TOL = 0.01
    errores = []
    if phd_usuario != 0 and abs(phd_usuario - res["phd"]) > TOL:
        errores.append(f"PHD: esperada {res['phd']:,.2f} €/h, tú pusiste {phd_usuario:,.2f} €/h")
    if pht_usuario != 0 and abs(pht_usuario - res["pht"]) > TOL:
        errores.append(f"PHT: esperado {res['pht']:,.2f} €/h, tú pusiste {pht_usuario:,.2f} €/h")
    if tf_usuario != 0 and abs(tf_usuario - res["tarifa_sin_iva"]) > TOL:
        errores.append(
            f"Tarifa sin IVA: esperada {res['tarifa_sin_iva']:,.2f} €/h, "
            f"tú pusiste {tf_usuario:,.2f} €/h"
        )
    if tfiva_usuario != 0 and abs(tfiva_usuario - res["tarifa_con_iva"]) > TOL:
        errores.append(
            f"Tarifa con IVA: esperada {res['tarifa_con_iva']:,.2f} €/h, "
            f"tú pusiste {tfiva_usuario:,.2f} €/h"
        )

    any_input = any(
        v != 0 for v in (phd_usuario, pht_usuario, tf_usuario, tfiva_usuario)
    )
    if any_input and not errores:
        st.success(
            "🎉 **Ejercicio correcto.** Todos los valores que introdujiste "
            "coinciden con el cálculo de la app. Tu ejercicio está bien resuelto."
        )
    elif any_input and errores:
        st.error("❌ **Hay diferencias en tu ejercicio:**")
        for e in errores:
            st.write("• " + e)
    elif not any_input:
        st.info("Introduce al menos un valor para certificarlo.")
