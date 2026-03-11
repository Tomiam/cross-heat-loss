import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. BRANDING & STYLE ---
st.set_page_config(page_title="Cross Group | Heat Loss Calculator", layout="wide")

CROSS_BLUE = "#1C4E80"
CROSS_DARK = "#1A1A1A"
CROSS_RED = "#E31E24"
LOGO_FILE = "logo-home.png"
CAPEX_FACTOR = 1750  # Your requested £1750 per kW

st.markdown(f"""
    <style>
    * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
    @media print {{
        [data-testid="stSidebar"], .stButton, header, [data-testid="stHeader"], [data-testid="stToolbar"] {{ 
            display: none !important; 
        }}
        .main .block-container {{ max-width: 100% !important; padding: 1rem !important; }}
    }}
    section[data-testid="stSidebar"] {{ background-color: {CROSS_DARK}; color: white; }}
    [data-testid="stMetricValue"] {{ color: {CROSS_BLUE} !important; font-weight: 800; }}
    [data-testid="stMetricLabel"] {{ color: {CROSS_DARK} !important; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }}
    .stMetric {{ 
        background-color: #f1f5f9; 
        padding: 20px; 
        border: 1px solid #e2e8f0; 
        border-top: 5px solid {CROSS_RED}; 
        border-radius: 8px; 
    }}
    h1 {{ color: {CROSS_DARK}; border-bottom: 3px solid {CROSS_BLUE}; padding-bottom: 10px; text-transform: uppercase; font-weight: 900; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR CONFIGURATION ---
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    else:
        st.markdown(f"<h2 style='color:{CROSS_BLUE};'>CROSS GROUP</h2>", unsafe_allow_html=True)
    
    st.markdown(f"<p style='color: #94a3b8; font-size: 0.75rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-top: -10px;'>Advanced Temperature Control</p>", unsafe_allow_html=True)
    st.divider()
    
    # Financial Toggle
    st.subheader("Reporting Options")
    show_budget = st.toggle("💰 Include Budgetary Capex", value=False)
    report_ready = st.toggle("🚀 Prepare Report for PDF")
    
    st.divider()
    st.subheader("Design Conditions")
    target_temp = st.number_input("Target Internal Temp (°C)", value=20)
    ext_temp = st.number_input("Design External Temp (°C)", value=-5)
    delta_t = target_temp - ext_temp
    
    st.divider()
    st.subheader("U-Values")
    u_wall = st.number_input("Walls", value=0.25, format="%.2f")
    u_floor = st.number_input("Floor", value=0.15, format="%.2f")
    u_roof = st.number_input("Roof", value=0.18, format="%.2f")
    u_window = st.number_input("Windows", value=1.31, format="%.2f")
    u_door = st.number_input("Doors", value=1.30, format="%.2f")

# --- 3. MAIN CONTENT ---
if report_ready:
    st.markdown("<style>section[data-testid='stSidebar'] {display: none !important;}</style>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 1])
    with col_l:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, width=200)
        else:
            st.markdown(f"<h2 style='color:{CROSS_BLUE};'>CROSS GROUP</h2>", unsafe_allow_html=True)
    with col_r:
        st.markdown(f"<div style='text-align:right;'><strong>Audit Date:</strong> {pd.Timestamp.now().strftime('%d/%m/%Y')}<br><strong>Ref:</strong> Asset Performance Audit</div>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Editor"):
        st.rerun()

st.title("Heat Loss & Financial Impact Audit")

c1, c2 = st.columns(2)
with c1:
    proj = st.text_input("Project Reference", "Arena Main Hall")
    area = st.number_input("Floor Area (m²)", value=6000)
    height = st.number_input("Ceiling Height (m)", value=13)
with c2:
    ach = st.number_input("Infiltration (ACH)", value=0.5)
    wall_len = st.number_input("Ext. Wall Length (m)", value=100)
    door_area = st.number_input("Door Area (m²)", value=260)

# Calculations
vol = area * height
v_loss = 0.33 * ach * vol * delta_t
w_loss = (wall_len * height) * u_wall * delta_t
f_loss = area * u_floor * delta_t
r_loss = area * u_roof * delta_t
d_loss = door_area * u_door * delta_t

total_kw = (v_loss + w_loss + f_loss + r_loss + d_loss) / 1000
peak_kw = total_kw * 1.15
seasonal_cost = total_kw * 12 * 0.12 * 180
budget_capex = peak_kw * CAPEX_FACTOR

# Output Metrics
st.divider()
st.subheader("Executive Metrics")

# Layout adjustment based on toggle
if show_budget:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Peak Design Load", f"{peak_kw:,.1f} kW")
    m2.metric("Seasonal Spend", f"£{seasonal_cost:,.0f}")
    m3.metric("Building Volume", f"{vol:,} m³")
    m4.metric("Budgetary Capex", f"£{budget_capex:,.0f}")
else:
    m1, m2, m3 = st.columns(3)
    m1.metric("Peak Design Load", f"{peak_kw:,.1f} kW")
    m2.metric("Seasonal Spend", f"£{seasonal_cost:,.0f}")
    m3.metric("Building Volume", f"{vol:,} m³")

# Chart
st.subheader("Heat Loss Breakdown")
fig = go.Figure(data=[go.Bar(
    x=['Ventilation', 'Walls', 'Floor', 'Roof', 'Doors'],
    y=[v_loss, w_loss, f_loss, r_loss, d_loss],
    marker_color=CROSS_BLUE
)])
fig.update_layout(height=400, margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

st.divider()
footer_text = f"Proprietary Audit Tool | © Cross Group | Project: {proj} | Design ΔT: {delta_t}K"
if show_budget:
    footer_text += f" | Budget factor: £{CAPEX_FACTOR}/kW"
st.caption(footer_text)