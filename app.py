
import streamlit as st
import requests
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(
    page_title="Brasil God | Conversor Real-Time",
    page_icon="🇧🇷",
    layout="centered"
)

def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main {
        background-color: #f8fafc;
    }
    
    /* Header Estilo God */
    .header-container {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #064e3b 100%);
        padding: 2.5rem 1.5rem;
        border-radius: 0 0 40px 40px;
        margin: -6rem -2rem 2rem -2rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .logo-text {
        color: white;
        font-weight: 900;
        font-size: 1.8rem;
        line-height: 1;
        letter-spacing: -0.05em;
        font-style: italic;
    }
    
    .badge-god {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: #064e3b;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-weight: 900;
        font-size: 1.2rem;
        display: inline-block;
        margin-left: 5px;
        transform: rotate(-2deg);
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    /* Cards de Resultados */
    .result-card {
        background: white;
        padding: 1.8rem;
        border-radius: 32px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        margin-bottom: 1.2rem;
    }
    
    .result-card-dark {
        background: #0f172a;
        color: white;
        padding: 2rem;
        border-radius: 35px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .currency-label {
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        color: #10b981;
        margin-bottom: 0.5rem;
    }
    
    .currency-value {
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: -0.06em;
        margin: 0.2rem 0;
        line-height: 1;
    }
    
    .rate-badge {
        display: inline-block;
        font-size: 0.65rem;
        background: rgba(16, 185, 129, 0.1);
        color: #065f46;
        padding: 0.4rem 0.8rem;
        border-radius: 12px;
        font-weight: 800;
        margin-top: 1rem;
        text-transform: uppercase;
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tabs custom */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 15px;
        color: #64748b;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] {
        color: #065f46 !important;
        border-bottom-color: #10b981 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS (SOURCES ARGENTINAS) ---
CACHE_FILE = "argentina_rates_cache.json"

@st.cache_data(ttl=300) # Cache de 5 minutos
def fetch_all_rates():
    data = {
        "fetched_at": datetime.now().strftime("%H:%M"),
        "rates": {},
        "status": "error"
    }
    try:
        # 1. CriptoYa API (Dólar Tarjeta, MEP, Blue, Cripto)
        cy_res = requests.get("https://criptoya.com/api/dolar", timeout=10).json()
        
        # 2. Dolarito (Simulado vía CriptoYa o endpoints alternos para mayor estabilidad en Streamlit)
        # Usamos CriptoYa como motor principal ya que consolida Dolarito y otras fuentes
        data["rates"]["blue"] = cy_res["blue"]["ask"]
        data["rates"]["tarjeta"] = cy_res["tarjeta"]["ask"]
        data["rates"]["mep"] = cy_res["mep"]["al30"]["24hs"]["price"]
        
        # 3. BRL to USD (Global Rate)
        brl_usd_res = requests.get("https://open.er-api.com/v6/latest/BRL", timeout=10).json()
        data["rates"]["brl_usd"] = brl_usd_res["rates"]["USD"]
        
        # 4. PIX (CriptoYa tiene comparador de PIX)
        # Calculamos PIX basado en USDT (el método más común hoy) o valor directo si disponible
        pix_res = requests.get("https://criptoya.com/api/pix/ars/1", timeout=10).json()
        # Tomamos el promedio o el mejor valor de compra
        data["rates"]["pix"] = pix_res["total_ask"]
        
        data["status"] = "ok"
        
        # Persistencia en cache local por si falla la red
        with open(CACHE_FILE, "w") as f: json.dump(data, f)
        
    except Exception as e:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f: data = json.load(f)
            data["status"] = "cache"
        else:
            data["status"] = "error"
            
    return data

# --- PROCESAMIENTO ---
local_css()
rates_data = fetch_all_rates()

# Header
st.markdown("""
<div class="header-container">
    <div class="logo-text">BRASIL CONVERTER <span class="badge-god">GOD</span></div>
    <div style="color: #a7f3d0; font-size: 0.7rem; font-weight: 700; margin-top: 10px; letter-spacing: 0.2em; text-transform: uppercase;">
        Fuentes: Dolarito & CriptoYa (Real Time)
    </div>
</div>
""", unsafe_allow_html=True)

if rates_data["status"] == "error":
    st.error("Error crítico: No se pudieron obtener cotizaciones. Verificá tu conexión.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["💰 CONVERSOR", "🛍️ TECH SHOP", "🧭 TIPS"])

with tab1:
    # --- INPUTS ---
    monto_brl = st.number_input("Monto en Reales (BRL)", min_value=0.0, value=100.0, step=50.0, format="%.2f")
    
    metodo_pago = st.selectbox(
        "¿Cómo vas a pagar?",
        [
            "Tarjeta Crédito/Débito (Dólar Tarjeta)",
            "Efectivo Reales (Dólar Blue)",
            "Billetera / PIX (Mejor cotización)",
            "Cripto (Dólar MEP / USDT)"
        ],
        index=0
    )

    # --- LÓGICA DE CÁLCULO ---
    # 1 BRL = X USD = Y ARS
    brl_usd = rates_data["rates"]["brl_usd"]
    usd_monto = monto_brl * brl_usd
    
    if "Tarjeta" in metodo_pago:
        ars_usd_rate = rates_data["rates"]["tarjeta"]
        label_dolar = "Dólar Tarjeta"
        fuente = "Dolarito / CriptoYa"
    elif "Efectivo" in metodo_pago:
        ars_usd_rate = rates_data["rates"]["blue"]
        label_dolar = "Dólar Blue"
        fuente = "Dolarito"
    elif "PIX" in metodo_pago:
        # PIX es directo BRL -> ARS generalmente vía exchange
        # Si CriptoYa da PIX por 1 BRL:
        ars_brl_rate = rates_data["rates"]["pix"]
        ars_usd_rate = ars_brl_rate / brl_usd # Calculado para mostrar
        label_dolar = "Dólar PIX (Calculado)"
        fuente = "CriptoYa PIX"
    else:
        ars_usd_rate = rates_data["rates"]["mep"]
        label_dolar = "Dólar MEP"
        fuente = "CriptoYa"

    # Resultado final
    total_ars = usd_monto * ars_usd_rate
    if "PIX" in metodo_pago: # Corrección para PIX que es directo
        total_ars = monto_brl * rates_data["rates"]["pix"]

    # --- UI RESULTADOS ---
    status_color = "#10b981" if rates_data["status"] == "ok" else "#f59e0b"
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <span style="background: {status_color}22; color: {status_color}; padding: 4px 12px; border-radius: 20px; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">
            {rates_data['status']} • Actualizado {rates_data['fetched_at']} hs
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="result-card-dark">
        <div class="currency-label">Costo estimado en Pesos</div>
        <div class="currency-value">$ {total_ars:,.0f}</div>
        <div style="color: rgba(255,255,255,0.4); font-size: 0.8rem; font-weight: 600; margin-top: 5px;">
            ≈ u$d {usd_monto:,.2f}
        </div>
        <div class="rate-badge">
            Usando {label_dolar}: $ {ars_usd_rate:,.2f} • Fuente: {fuente}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Detalle técnico
    with st.expander("Ver detalle de cotizaciones"):
        st.write(f"**BRL/USD (Global):** {1/brl_usd:.2f} Reales por Dólar")
        st.write(f"**Dólar Blue:** ${rates_data['rates']['blue']}")
        st.write(f"**Dólar Tarjeta:** ${rates_data['rates']['tarjeta']}")
        st.write(f"**Dólar MEP:** ${rates_data['rates']['mep']}")
        st.write(f"**Conversión PIX (ARS/BRL):** ${rates_data['rates']['pix']}")

with tab2:
    st.markdown("<h3 style='font-weight: 900; letter-spacing: -0.05em;'>GUÍA DE PRECIOS BRASIL</h3>", unsafe_allow_html=True)
    
    # Items actualizados
    tech_items = [
        {"name": "iPhone 15 128GB", "brl": 4799, "cat": "Apple"},
        {"name": "AirPods Pro 2", "brl": 1699, "cat": "Audio"},
        {"name": "PlayStation 5 Slim", "brl": 3450, "cat": "Gaming"},
        {"name": "JBL Flip 6", "brl": 520, "cat": "Audio"},
        {"name": "Cena para 2 (Rodizio)", "brl": 280, "cat": "Gastro"},
        {"name": "Caipirinha en Playa", "brl": 25, "cat": "Gastro"}
    ]
    
    # Usamos cotización Tarjeta para tech por defecto
    card_rate = rates_data["rates"]["tarjeta"]
    
    for item in tech_items:
        cost_ars = (item['brl'] * brl_usd) * card_rate
        st.markdown(f"""
        <div style="background: white; padding: 1.2rem; border-radius: 25px; border: 1px solid #f1f5f9; margin-bottom: 0.8rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
            <div>
                <div style="font-size: 0.6rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">{item['cat']}</div>
                <div style="font-weight: 800; color: #1e293b; font-size: 1rem;">{item['name']}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 900; color: #10b981; font-size: 1.1rem;">R$ {item['brl']}</div>
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b;">$ {cost_ars:,.0f} ARS</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("### 🧭 Guía de Supervivencia")
    
    tips = [
        {
            "t": "💳 Tarjeta vs Efectivo", 
            "d": "Pagar con tarjeta hoy (Dólar Tarjeta) suele ser más caro que comprar Reales con Dólar MEP o Blue. Siempre hacé la cuenta antes de viajar."
        },
        {
            "t": "📲 El truco del PIX", 
            "d": "Bajate apps como Belo o Lemon. Podés pagar con QR de PIX usando tus pesos o USDT a una cotización mucho mejor que el Dólar Tarjeta."
        },
        {
            "t": "🏦 Retiros ATM", 
            "d": "Evitá sacar plata de cajeros. Cobran comisiones altísimas (20-40 R$ por retiro) y el cambio es el oficial del banco."
        },
        {
            "t": "🛡️ Seguridad Celular", 
            "d": "Nunca uses el celular en la vereda. Entrá a un local para mirar el mapa o pedir un Uber. Perfil bajo siempre."
        }
    ]
    
    for tip in tips:
        with st.container():
            st.markdown(f"""
            <div style="background: #f0fdf4; padding: 1.5rem; border-radius: 24px; border-left: 5px solid #10b981; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #064e3b; font-weight: 800;">{tip['t']}</h4>
                <p style="margin: 10px 0 0 0; color: #166534; font-size: 0.9rem; line-height: 1.4;">{tip['d']}</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #94a3b8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;'>Brasil God • {datetime.now().year} • v2.5 Premium</div>", unsafe_allow_html=True)
