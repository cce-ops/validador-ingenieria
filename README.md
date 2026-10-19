# 💶 Validador Financiero y de Costes de Ingeniería

App web (Streamlit) para que el alumnado **autocertifique** que sus ejercicios de
viabilidad económica, cálculo de tarifas técnicas y estructura de préstamos están
bien resueltos.

Incluye tres herramientas, con las fórmulas de los documentos de referencia
("Costes de ingeniería y Punto de Equilibrio v4" y "Financiación y préstamos v3"):

https://validador-ingenieria.streamlit.app/

| Pestaña | Qué hace |
| :--- | :--- |
| 💶 **PHD y Tarifa Final** | Precio Hora Directa, Precio Hora Total y Tarifa Final al cliente (sin/con IVA), con coeficientes α y δ. |
| 🏦 **Préstamo Francés y TAE** | Cuota constante, cuadro de amortización mensual/trimestral ($a, Y_r, A_r, R_r$) y equivalencia TIN ↔ TAE. |
| ⚖️ **Punto de Equilibrio** | Punto de equilibrio clásico y con beneficio objetivo. |

Cada pestaña tiene una sección **✅ Certifica tu ejercicio**: introduces tus
resultados y la app te avisa si coinciden con el cálculo correcto.

## 🚀 Puesta en marcha local

```bash
git clone <este-repositorio>
cd <repositorio>

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

La app queda en `http://localhost:8501`.

## 📂 Estructura

```text
.
├── app.py                    # punto de entrada: pagina y pestañas
├── requirements.txt
├── README.md
└── views/
    ├── __init__.py
    ├── phd_tarifa.py         # PHD, PHT y Tarifa Final (sin/con IVA)
    ├── prestamo_frances.py   # Prestamo frances, cuadro de amortizacion y TAE
    └── punto_equilibrio.py   # Punto de equilibrio y beneficio objetivo
```

## 🧮 Fórmulas implementadas

**Costes de ingeniería**

- $PHD = (S + SS + OCD) / H$
- $PHT = (1 + \\delta) \\cdot \\alpha \\cdot PHD$
- $Tarifa\ sin\ IVA = PHT \\cdot [1 + m(1 + t_{IS})]$
- $Tarifa\ con\ IVA = Tarifa\ sin\ IVA \\cdot (1 + IVA)$

**Préstamo francés y TAE**

- Tipo efectivo por periodo: $I_m = i_m / m$
- $TAE = (1 + i_m/m)^m - 1$
- Cuota constante: $a = C_0 \\cdot I_m / (1 - (1 + I_m)^{-n})$
- Amortización periodo $r$: $Y_r = R_{r-1} \\cdot I_m$; $A_r = a - Y_r$; $R_r = R_{r-1} - A_r$

**Punto de equilibrio**

- $PE = CF / (p - c_v)$
- $PE\ con\ beneficio = (CF + B_{objetivo}) / (p - c_v)$

## 📄 Notas

El IVA (21 % general para servicios de ingeniería) no es un coste para la
empresa: se repercute al cliente en la factura. El Impuesto de Sociedades (25 %
general, 24 % PYME, 21 % microempresa primeros 50.000 €, 15 % empresa nueva
creación) sí grava el beneficio.

Calculo local puro: no requiere API Key ni conexion a internet una vez
instaladas las dependencias.
