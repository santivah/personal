import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import numpy as np


###### Title
# Set page configuration
st.set_page_config(
    page_title="ANALISIS DE PAGOS PRÉSTAMO COLFUTURO",
    page_icon="🤓",  
    layout="wide",  # Wide layout for better use of screen space
    initial_sidebar_state="expanded",
)

###### Sidebar configurations
st.sidebar.header("⚙️ Set it up!")

# Sidebar for dark mode toggle
st.sidebar.header("Accessibility Features")
dark_mode = st.sidebar.checkbox("Enable Dark Mode 🌚", value=False)

# Update plotly template based on the dark mode toggle
plotly_template = "plotly_dark" if dark_mode else "plotly"

# Define Plotly theme based on the dark mode toggle
if dark_mode:
    plotly_template = "plotly_dark"
    st.markdown(
        """
        <style>
        body {
            background-color: #2B2B2B;
            color: white;
        }
        .sidebar-content {
            background-color: #333333;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    plotly_template = "plotly"
    st.markdown(
        """
        <style>
        body {
            background-color: white;
            color: black;
        }
        .sidebar-content {
            background-color: #f0f0f0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Sidebar values inputs

dinero_total = st.sidebar.number_input('Quantity given by Colfuturo [USD]', min_value=1, max_value=50000, step=1)
if dinero_total <= 0 or dinero_total > 50000:
    st.warning("Please enter a valid quantity given by Colfuturo")
    st.stop()

monto_beca = dinero_total / 2
monto_credito = dinero_total / 2

plazo_estudio_month = st.sidebar.number_input('Study period [months]', min_value=9, max_value=24, step=1)
if plazo_estudio_month <= 0 or plazo_estudio_month > 24:
    st.warning("Please enter a valid study period. According to Colfuturo, the study period must be between 9 and 24 months.")
    st.stop()

#plazo_estudio = plazo_estudio_month / 12 # Convert study period to years for calculations


# Sidebar input for loan years
st.sidebar.markdown("Loan Parameters")
plazo_amortizacion = st.sidebar.slider(
    "Desired loan payment period (years)", 
    min_value=1, 
    max_value=10, 
    value=5, 
    step=1
)

interes_estudio = st.sidebar.number_input('Interest rate for study period [%]', min_value=0.0, max_value=100.0, step=0.01)
if interes_estudio <= 0 or interes_estudio > 100:
    st.warning("Please enter a valid interest rate for the study period")
    st.stop()

interes_estudio = interes_estudio / 100

interes_amortizacion = st.sidebar.number_input('Interest rate for payment period [%]', min_value=0.0, max_value=100.0, step=0.01)
if interes_amortizacion <= 0 or interes_amortizacion > 100:
    st.warning("Please enter a valid interest rate for the payment period")
    st.stop()

interes_amortizacion = interes_amortizacion / 100

# Main screen
st.subheader("INTEREST RATE TOOL FOR COLFUTURO LOAN")

st.warning("By default the calculation takes into account a non-payment period of 1 year after graduation.")
plazo_gracia = 1 #años
#st.warning("Please wait while we calculate the results...")



# Datos de entrada
#monto_beca = 25000
#monto_credito = 25000
#interes_estudio = 0.07 #% anual
#interes_amortizacion = 0.09 #% anual
#plazo_estudio = 2 #años
#plazo_gracia = 1 #años
#plazo_amortizacion = 6 #años


# Cálculo de monto total a pagar después del periodo de gracia.
st.write("Loan base value: USD {:.2f}".format(monto_credito))

for i in range(plazo_estudio_month):
    #st.write("Initial value: USD {:.2f}".format(monto_credito))
    #print(f'Valor inicial crédito: USD {monto_credito:.2f}')
    monto_credito += monto_credito * (interes_estudio/12)
    #st.write("Monto crédito al finalizar el año {}: USD {:.2f}".format(i+1, monto_credito))
    #print(f'Monto crédito al finalizar el año {i+1}: USD {monto_credito:.2f}')

monto_credito = monto_credito * (1 + interes_amortizacion)
monto_total = monto_beca + monto_credito # Monto total a pagar
st.write("Total quantity after non-payment period: USD {:.2f}".format(monto_total))
#print(f"Monto total después del periodo de gracia: USD {monto_total: .2f}")
intereses_totales = monto_total - dinero_total
st.write("Total accumulated interest: USD {:.2f}".format(intereses_totales))
#print(f"Intereses acumulados después del periodo de gracia: USD {intereses_totales:.2f}")


# Cálculo de cuota mensual asumiendo pago de deuda del 100%
#def cuota_mensual_fija(monto, tasa_anual, plazo):
#    tasa_mensual = tasa_anual / 12
#    n_cuotas = plazo * 12
#    cuota = (monto * (tasa_mensual) * (1 + tasa_mensual)**n_cuotas) / ((1 + tasa_mensual)**n_cuotas - 1)
#    return cuota


def cuota_mensual_fija(monto, tasa_anual, plazo):
    tasa_mensual = tasa_anual / 12
    n_cuotas = plazo * 12
    
    if tasa_mensual == 0:  # Handle zero-interest case
        return monto / n_cuotas
    
    # Regular calculation for non-zero interest
    return (monto * tasa_mensual * (1 + tasa_mensual) ** n_cuotas) / ((1 + tasa_mensual) ** n_cuotas - 1)

cuota_mensual = cuota_mensual_fija(monto_total, interes_amortizacion, plazo_amortizacion)

st.subheader("Scenario 1: Payment of 100% of the money")
st.write(f"Fixed monthly fee in a period of {plazo_amortizacion} years: USD {cuota_mensual:.2f}")
#print(f'\nEscenario 1: Pago del 100% del dinero. \n Cuota fija mensual en un periodo de {plazo_amortizacion} años: USD {cuota_mensual:.2f}')
st.write("Total amount paid: USD {:.2f}".format(cuota_mensual * plazo_amortizacion * 12))


# Cálculo de cuota mensual asumiendo pago de deuda del 80%
st.subheader("Scenario 2: 80% of the debt waived")
monto_80 = (monto_beca + monto_credito) * 0.2 + intereses_totales
cuota_mensual_80 = cuota_mensual_fija(monto_80, interes_amortizacion, plazo_amortizacion)

st.write(f"Fixed monthly fee in a period of {plazo_amortizacion} years: USD {cuota_mensual_80:.2f}")
#print(f'\nEscenario 2: Pago del 80% del dinero. \n Cuota fija mensual en un periodo de {plazo_amortizacion} años: USD {cuota_mensual_80:.2f}')
st.write("Total amount paid: USD {:.2f}".format(cuota_mensual_80 * plazo_amortizacion * 12))


# Cálculo de cuota mensual asumiendo pago de deuda del 60%
st.subheader("Scenario 3: 60% of the debt waived")
monto_60 = (monto_beca + monto_credito) * 0.4 + intereses_totales
cuota_mensual_60 = cuota_mensual_fija(monto_60, interes_amortizacion, plazo_amortizacion)

st.write(f"Fixed monthly fee in a period of {plazo_amortizacion} years: USD {cuota_mensual_60:.2f}")
#print(f'\nEscenario 3: Pago del 60% del dinero. \n Cuota fija mensual en un periodo de {plazo_amortizacion} años: USD {cuota_mensual_60:.2f}')
st.write("Total amount paid: USD {:.2f}".format(cuota_mensual_60 * plazo_amortizacion * 12))

