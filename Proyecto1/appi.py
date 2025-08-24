import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image

# --- Estilo global con gradiente de fondo ---
st.markdown(
    """
    <style>
    /* Gradiente de fondo sutil */
    .stApp {
        background: linear-gradient(180deg, #000000, #111111);
        color: white;
    }

    /* Título grande en blanco */
    .title {
        color: white;
        font-size: 40px;
        font-weight: bold;
        text-align: center;
    }

    /* Labels de inputs */
    .stNumberInput label, .stTextInput label {
        color: white;
        font-size: 18px;
        font-weight: bold;
    }

    /* Tarjetas de resultados */
    .result-card {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.7);
    }

    .result-name {
        color: #FFD700;
        font-weight: bold;
    }
    .result-value {
        color: #00FF00;
    }

    /* Botones con gradiente y hover */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(90deg, #333333, #555555);
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background: linear-gradient(90deg, #555555, #777777);
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.6);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Logo ---
try:
    logo = Image.open("logo.png")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(logo, width=300)
except:
    st.write("No se encontró logo.png")

# --- Título ---
st.markdown('<h1 class="title">Calculadora de Comisiones - Asesores Súper Nómina</h1>', unsafe_allow_html=True)

# --- Datos de comisiones ---
comisiones = {'GA': 400, 'GB': 200, 'GM': 30, 'TDC': 150, 'PO': 300, 'CO': 500, 'E': 36}

# --- Entradas ---
PE = st.number_input("Entregas", min_value=0, step=1)
PGB = st.number_input("Seguros gama baja", min_value=0, step=1)
PGM = st.number_input("Microseguros", min_value=0, step=1)
PTDC = st.number_input("TDC aceptadas", min_value=0, step=1)
PPO = st.number_input("Portabilidades", min_value=0, step=1)
PGA = st.number_input("Seguros auto", min_value=0, step=1)
PCO = st.number_input("Consumos", min_value=0, step=1)
NPS = st.number_input("NPS de la zona", min_value=0, step=1)
RX = st.number_input("Número de rechazos", min_value=0, step=1)

# --- Función de cálculo ---
def calcular(cantidad, umbral, valor):
    return cantidad * valor if cantidad >= umbral else 0

# --- Botón de cálculo ---
if st.button("Calcular comisiones y generar PDF"):
    CE   = calcular(PE,   200, comisiones['E'])
    CGB  = calcular(PGB,   16, comisiones['GB'])
    CGM  = calcular(PGM,   22, comisiones['GM'])
    CTDC = calcular(PTDC,   4, comisiones['TDC'])
    CPO  = calcular(PPO,    3, comisiones['PO'])
    CGA  = calcular(PGA,    1, comisiones['GA'])
    CCO  = calcular(PCO,    2, comisiones['CO'])

    CT = CGB + CGM + CTDC + CPO + CGA + CCO + CE  

    if NPS < 80 and RX >= 1:  
        CR = CGB + CGM + CTDC + CPO + CGA + CCO + (CE * 0.75)  
    elif NPS < 80:  
        CR = CGB + CGM + CTDC + CPO + CGA + CCO + (CE * 0.85)  
    elif RX >= 1:  
        CR = CGB + CGM + CTDC + CPO + CGA + CCO + (CE * 0.90)  
    else:  
        CR = CT  

    resultados = {  
        'Entregas': CE,  
        'Seguros Gama Baja': CGB,  
        'Microseguros GM': CGM,  
        'TDC Aceptadas': CTDC,  
        'Portabilidades': CPO,  
        'Seguros Auto': CGA,  
        'Consumos': CCO,  
        'Comisión Total': CT,  
        'Descuentos NPS/Rechazos': -(CT - CR),  
        'Comisión Real': CR  
    }  

    # --- Mostrar resultados en tarjetas ---  
    for nombre, valor in resultados.items():  
        color_valor = "#00FF00" if valor >= 0 else "#FF0000"  
        st.markdown(  
            f"""  
            <div class="result-card">  
                <span class="result-name">{nombre}:</span>   
                <span class="result-value" style="color:{color_valor}">${valor:.2f}</span>  
            </div>  
            """,  
            unsafe_allow_html=True  
        )  

    # --- Generar PDF en memoria ---  
    buffer = BytesIO()  
    c = canvas.Canvas(buffer, pagesize=letter)  
    width, height = letter  

    c.setFont("Helvetica-Bold", 16)  
    c.drawString(50, height - 50, "Desglose de Comisiones")  

    c.setFont("Helvetica", 12)  
    y = height - 100  
    for nombre, valor in resultados.items():  
        c.drawString(50, y, f"{nombre}: ${valor:.2f}")  
        y -= 25  

    c.showPage()  
    c.save()  
    buffer.seek(0)  

    # --- Botón de descarga PDF ---
    st.download_button(  
        label="Descargar PDF",  
        data=buffer,  
        file_name="comisiones.pdf",  
        mime="application/pdf"  
    )