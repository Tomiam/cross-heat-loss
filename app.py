import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import json

# --- 1. BRANDING & STYLE ---
st.set_page_config(page_title="Cross Group | Proposal Generator", layout="wide")

CROSS_BLUE = "#1C4E80"
CROSS_DARK = "#1A1A1A"
CROSS_RED = "#E31E24"
THEME_GREY = "#262730" 
LOGO_FILE = "logo-home.png"
CAPEX_FACTOR = 1750 

st.markdown(f"""
    <style>
    * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
    @media print {{
        [data-testid="stSidebar"], .stButton, header, [data-testid="stHeader"], [data-testid="stToolbar"] {{ 
            display: none !important; 
        }}
        .main .block-container {{ max-width: 100% !important; padding: 1rem !important; }}
        .page-break {{ page-break-before: always; }}
        .tc-text {{ font-size: 7.2pt !important; line-height: 1.1; color: #333; text-align: justify; }}
        .tc-column {{ column-count: 2; column-gap: 25px; }}
    }}
    section[data-testid="stSidebar"] {{ background-color: {CROSS_DARK}; color: white; }}
    [data-testid="stMetricValue"] {{ color: white !important; font-weight: 800; }}
    [data-testid="stMetricLabel"] {{ color: #94a3b8 !important; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; }}
    .stMetric {{ 
        background-color: {THEME_GREY}; 
        padding: 20px; 
        border: 1px solid #464855; 
        border-top: 5px solid {CROSS_RED}; 
        border-radius: 8px; 
    }}
    h1, h2, h3 {{ color: white; font-weight: 900; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR & DATA LOADING ---
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    else:
        st.markdown(f"<h2 style='color:{CROSS_BLUE}; text-align:center;'>CROSS GROUP</h2>", unsafe_allow_html=True)
    
    st.divider()

    with st.expander("💾 Project Data Control", expanded=True):
        uploaded_file = st.file_uploader("Load Project (.json)", type="json")
        save_data = json.load(uploaded_file) if uploaded_file else {}

    def get_val(key, default):
        return save_data.get(key, default)

    with st.expander("📄 Proposal Details", expanded=True):
        client_name = st.text_input("Client Name", value=get_val("client_name", ""))
        contact_person = st.text_input("Contact Person", value=get_val("contact_person", ""))
        cross_ref = st.text_input("Cross Reference", value=get_val("cross_ref", ""))
        show_budget = st.toggle("💰 Include Budgetary Capex", value=get_val("show_budget", True))
        report_ready = st.toggle("🚀 Generate Final Proposal", value=False)

    with st.expander("🔥 Heating System & Utilities", expanded=True):
        heat_source = st.selectbox("Heat Source", ["Gas", "Electric", "Heat Pump"], index=0)
        cop = st.number_input("Heat Pump COP", value=get_val("cop", 3.5)) if heat_source == "Heat Pump" else 1.0
        elec_price = st.number_input("Elec Price (£/kWh)", value=get_val("elec_price", 0.28))
        gas_price = st.number_input("Gas Price (£/kWh)", value=get_val("gas_price", 0.08))

    # --- RESTORED U-VALUE CALIBRATION ---
    with st.expander("🏗️ U-Value Calibration", expanded=True):
        u_wall_ext = st.number_input("External Walls", value=get_val("u_wall_ext", 0.25), format="%.2f")
        u_wall_int = st.number_input("Internal Walls", value=get_val("u_wall_int", 0.15), format="%.2f")
        u_floor = st.number_input("Floor", value=get_val("u_floor", 0.15), format="%.2f")
        u_roof = st.number_input("Roof", value=get_val("u_roof", 0.18), format="%.2f")
        u_door = st.number_input("Doors", value=get_val("u_door", 1.30), format="%.2f")

# --- 3. INPUT GATHERING ---
if not report_ready:
    st.title("Proposal Workbench")
    
    with st.expander("🏗️ Building & Room Data", expanded=True):
        row1_l, row1_r = st.columns(2)
        proj_name = row1_l.text_input("Project Reference", value=get_val("proj_name", ""))
        area_val = row1_r.number_input("Floor Area (m²)", value=get_val("area_val", 6000.0))

        st.subheader("Design Conditions")
        t1, t2, t3 = st.columns(3)
        target_temp = t1.number_input("Target Internal Temp (°C)", value=get_val("target_temp", 20))
        ext_temp = t2.number_input("Outdoor Design Temp (°C)", value=get_val("ext_temp", -5))
        delta_t_int = t3.number_input("Internal Wall ΔT (K)", value=get_val("delta_t_int", 21))
        delta_t_ext = target_temp - ext_temp

        st.subheader("Room Parameters")
        c1, c2, c3 = st.columns(3)
        height_val = c1.number_input("Height (m)", value=get_val("height_val", 13.0))
        ach_val = c2.number_input("ACH", value=get_val("ach_val", 0.5))
        door_area_val = c3.number_input("Doors Area (m²)", value=get_val("door_area_val", 260.0))

        st.subheader("Surface Exposures")
        r2c1, r2c2, r2c3 = st.columns(3)
        ext_wall_area_val = r2c1.number_input("External Wall Area (m²)", value=get_val("ext_wall_area_val", 1300.0))
        int_wall_length = r2c2.number_input("Internal Wall Length (m)", value=get_val("int_wall_length", 0.0))
        preheat_pct = r2c3.number_input("Preheat Allowance (%)", value=get_val("preheat_pct", 15.0))
    
    with st.expander("🌬️ System Design (Airflow & Season)", expanded=False):
        ac_col1, ac_col2 = st.columns(2)
        supply_delta = ac_col1.number_input("Supply Air ΔT (K)", value=get_val("supply_delta", 15.0))
        airflow_unit = ac_col2.radio("Airflow Unit", ["m³/h", "m³/s"], horizontal=True)
        st.divider()
        h_cols = st.columns(2)
        full_load_hrs = h_cols[0].number_input("Full Load Hrs/Day", value=get_val("full_load_hrs", 12.0))
        season_days = h_cols[1].number_input("Heating Season (Days)", value=get_val("season_days", 180))
        
    st.session_state.update({
        "proj_name": proj_name, "area_val": area_val, "height_val": height_val,
        "ach_val": ach_val, "door_area_val": door_area_val, "ext_wall_area_val": ext_wall_area_val, 
        "int_wall_length": int_wall_length, "target_temp": target_temp, "ext_temp": ext_temp, 
        "delta_t_int": delta_t_int, "preheat_pct": preheat_pct, "supply_delta": supply_delta,
        "airflow_unit": airflow_unit, "full_load_hrs": full_load_hrs, "season_days": season_days,
        "u_wall_ext": u_wall_ext, "u_wall_int": u_wall_int, "u_floor": u_floor, "u_roof": u_roof, "u_door": u_door
    })
else:
    # Recover state
    proj_name = st.session_state.get("proj_name", "")
    area_val = st.session_state.get("area_val", 6000.0)
    height_val = st.session_state.get("height_val", 13.0)
    ach_val = st.session_state.get("ach_val", 0.5)
    door_area_val = st.session_state.get("door_area_val", 260.0)
    ext_wall_area_val = st.session_state.get("ext_wall_area_val", 1300.0)
    int_wall_length = st.session_state.get("int_wall_length", 0.0)
    target_temp = st.session_state.get("target_temp", 20)
    ext_temp = st.session_state.get("ext_temp", -5)
    delta_t_int = st.session_state.get("delta_t_int", 21)
    delta_t_ext = target_temp - ext_temp
    preheat_pct = st.session_state.get("preheat_pct", 15.0)
    supply_delta = st.session_state.get("supply_delta", 15.0)
    airflow_unit = st.session_state.get("airflow_unit", "m³/h")
    full_load_hrs = st.session_state.get("full_load_hrs", 12.0)
    season_days = st.session_state.get("season_days", 180)

# --- 4. CALCULATIONS ---
vol = area_val * height_val
inf_loss = 0.33 * ach_val * vol * delta_t_ext
ext_wall_loss = ext_wall_area_val * u_wall_ext * delta_t_ext
int_wall_loss = int_wall_length * u_wall_int * delta_t_int 
floor_loss = area_val * u_floor * delta_t_ext
roof_loss = area_val * u_roof * delta_t_ext
door_loss = door_area_val * u_door * delta_t_ext

total_fabric_w = inf_loss + ext_wall_loss + int_wall_loss + floor_loss + roof_loss + door_loss
fabric_kw = total_fabric_w / 1000
preheat_kw = fabric_kw * (preheat_pct / 100)
final_peak_kw = fabric_kw + preheat_kw

# Derived Metrics
w_per_m2 = (final_peak_kw * 1000) / area_val if area_val > 0 else 0
req_airflow_h = (final_peak_kw * 1000) / (1.2 * 0.27 * supply_delta) if supply_delta > 0 else 0
final_airflow = req_airflow_h / 3600 if airflow_unit == "m³/s" else req_airflow_h

# Financials
efficiency = cop if heat_source == "Heat Pump" else 0.9 if heat_source == "Gas" else 1.0
fuel_rate = gas_price if heat_source == "Gas" else elec_price
annual_kwh = (final_peak_kw / efficiency) * full_load_hrs * season_days 
annual_spend = annual_kwh * fuel_rate
budget_capex = final_peak_kw * CAPEX_FACTOR

# --- 5. VIEWS ---
if not report_ready:
    st.divider()
    m_cols = st.columns(5 if show_budget else 4)
    m_cols[0].metric("Peak Design Load", f"{final_peak_kw:,.0f} kW")
    m_cols[1].metric("Heat Density", f"{w_per_m2:,.1f} W/m²")
    m_cols[2].metric("Heating Costs", f"£{annual_spend:,.0f}")
    m_cols[3].metric(f"Req. Airflow ({airflow_unit})", f"{final_airflow:,.1f}" if airflow_unit == "m³/s" else f"{final_airflow:,.0f}")
    if show_budget: m_cols[4].metric("Budgetary Capex", f"£{budget_capex:,.0f}")
    
    # Chart
    c_data = pd.DataFrame({
        'Category': ['Infiltration', 'Ext Walls', 'Int Walls', 'Floor', 'Roof', 'Doors', 'Preheat'],
        'kW': [inf_loss/1000, ext_wall_loss/1000, int_wall_loss/1000, floor_loss/1000, roof_loss/1000, door_loss/1000, preheat_kw]
    }).sort_values('kW', ascending=False)
    fig = go.Figure(data=[go.Bar(x=c_data['Category'], y=c_data['kW'], marker_color=CROSS_BLUE, text=c_data['kW'].apply(lambda x: f"{x:,.1f} kW"), textposition='outside')])
    fig.update_layout(height=400, margin=dict(t=30, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)

else:
    # PROPOSAL PDF
    c1, c2 = st.columns([1,1])
    with c1:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=220)
    with c2:
        st.markdown(f"<div style='text-align:right; color:{CROSS_BLUE}; font-weight:bold;'>REF: CROSS {cross_ref if cross_ref else '__________'}</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""<div style="text-align: center; border: 2px solid {CROSS_BLUE}; padding: 60px; border-radius: 10px; background-color:white;">
            <h1 style="font-size: 3.5rem; margin-bottom: 0; color:{CROSS_DARK};">PROPOSAL</h1>
            <p style="color:{CROSS_RED}; letter-spacing: 5px; font-weight: bold; font-size: 1.2rem;">ADVANCED TEMPERATURE CONTROL</p>
            <br><br>
            <h3 style="color:{CROSS_DARK};">CLIENT: {client_name if client_name else "___________________"}</h3>
            <h3 style="color:{CROSS_DARK};">PROJECT: {proj_name if proj_name else "___________________"}</h3>
            <p style="color:{CROSS_DARK};">Date: {pd.Timestamp.now().strftime('%d %B %Y')}</p>
        </div>""", unsafe_allow_html=True)
    
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    st.header("Thermal Performance & Financial Assessment")
    
    pcols = st.columns(3)
    pcols[0].metric("Peak Design Load", f"{final_peak_kw:,.0f} kW")
    pcols[1].metric("Est. Heating Costs", f"£{annual_spend:,.0f}")
    pcols[2].metric("Heat Density", f"{w_per_m2:,.1f} W/m²")

    st.write(f"Heating costs are estimated using the **Standard Season Formula**, based on using **{heat_source}** with an annual requirement of **{annual_kwh:,.0f} kWh**.")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    st.header("Terms and Conditions of Sale")
    st.markdown("""<div class="tc-text tc-column">... (Full 23 Clauses) ...</div>""", unsafe_allow_html=True)

    if st.button("⬅️ Back to Editor"): st.rerun()

# --- 6. EXPORT ---
current_params = { "proj_name": proj_name, "area_val": area_val, "height_val": height_val, "ach_val": ach_val, "door_area_val": door_area_val, "ext_wall_area_val": ext_wall_area_val, "int_wall_length": int_wall_length, "client_name": client_name, "contact_person": contact_person, "cross_ref": cross_ref, "target_temp": target_temp, "ext_temp": ext_temp, "delta_t_int": delta_t_int, "preheat_pct": preheat_pct, "supply_delta": supply_delta, "airflow_unit": airflow_unit, "show_budget": show_budget, "heat_source": heat_source, "elec_price": elec_price, "gas_price": gas_price, "cop": cop, "full_load_hrs": full_load_hrs, "season_days": season_days, "u_wall_ext": u_wall_ext, "u_wall_int": u_wall_int, "u_floor": u_floor, "u_roof": u_roof, "u_door": u_door }
st.sidebar.download_button("📥 Export Project Data", data=json.dumps(current_params), file_name=f"audit_{proj_name}.json", use_container_width=True)