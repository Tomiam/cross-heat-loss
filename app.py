import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import json
import math

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
        .tc-text {{ font-size: 6.8pt !important; line-height: 1.1; color: #333; text-align: justify; }}
        .tc-column {{ column-count: 2; column-gap: 20px; }}
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
    
    st.markdown(f"<p style='color: #94a3b8; font-size: 0.75rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; text-align: center; margin-top: -15px;'>Advanced Temperature Control</p>", unsafe_allow_html=True)
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
        elec_price = st.number_input("Elec Price (£/kWh)", value=get_val("elec_price", 0.28), format="%.2f")
        gas_price = st.number_input("Gas Price (£/kWh)", value=get_val("gas_price", 0.08), format="%.2f")

    with st.expander("🏗️ U-Value Calibration", expanded=False):
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
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        ext_wall_len = r2_c1.number_input("Ext. Wall Length (m)", value=get_val("ext_wall_len", 100.0))
        int_wall_len = r2_c2.number_input("Int. Wall Length (m)", value=get_val("int_wall_len", 0.0))
        preheat_pct = r2_c3.number_input("Preheat/Warm-up Allowance (%)", value=get_val("preheat_pct", 15.0))
    
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
        "ach_val": ach_val, "door_area_val": door_area_val, "ext_wall_len": ext_wall_len, 
        "int_wall_len": int_wall_len, "target_temp": target_temp, "ext_temp": ext_temp, 
        "delta_t_int": delta_t_int, "preheat_pct": preheat_pct, "supply_delta": supply_delta,
        "airflow_unit": airflow_unit, "full_load_hrs": full_load_hrs, "season_days": season_days
    })
else:
    # Value Recovery
    proj_name = st.session_state.get("proj_name", "")
    area_val = st.session_state.get("area_val", 6000.0)
    height_val = st.session_state.get("height_val", 13.0)
    ach_val = st.session_state.get("ach_val", 0.5)
    door_area_val = st.session_state.get("door_area_val", 260.0)
    ext_wall_len = st.session_state.get("ext_wall_len", 100.0)
    int_wall_len = st.session_state.get("int_wall_len", 0.0)
    target_temp = st.session_state.get("target_temp", 20)
    ext_temp = st.session_state.get("ext_temp", -5)
    delta_t_int = st.session_state.get("delta_t_int", 21)
    delta_t_ext = target_temp - ext_temp
    preheat_pct = st.session_state.get("preheat_pct", 15.0)
    supply_delta = st.session_state.get("supply_delta", 15.0)
    airflow_unit = st.session_state.get("airflow_unit", "m³/h")
    full_load_hrs = st.session_state.get("full_load_hrs", 12.0)
    season_days = st.session_state.get("season_days", 180)

# --- 4. GLOBAL CALCULATIONS ---
efficiency = cop if heat_source == "Heat Pump" else 0.9 if heat_source == "Gas" else 1.0
fuel_rate = gas_price if heat_source == "Gas" else elec_price

vol = area_val * height_val
inf_loss = 0.33 * ach_val * vol * delta_t_ext
ext_wall_loss = (ext_wall_len * height_val) * u_wall_ext * delta_t_ext
int_wall_loss = (int_wall_len * height_val) * u_wall_int * delta_t_int 
floor_loss = area_val * u_floor * delta_t_ext
roof_loss = area_val * u_roof * delta_t_ext
door_loss = door_area_val * u_door * delta_t_ext

total_fabric_w = inf_loss + ext_wall_loss + int_wall_loss + floor_loss + roof_loss + door_loss
fabric_kw = total_fabric_w / 1000
preheat_kw = fabric_kw * (preheat_pct / 100)
final_peak_kw = fabric_kw + preheat_kw

# Project Airflows
req_airflow_total_h = (final_peak_kw * 1000) / (1.2 * 0.27 * supply_delta) if supply_delta > 0 else 0
flow_m3s_total = req_airflow_total_h / 3600
final_airflow_display = flow_m3s_total if airflow_unit == "m³/s" else req_airflow_total_h

# Finance/Energy
annual_kwh = (final_peak_kw / efficiency) * full_load_hrs * season_days 
annual_spend = annual_kwh * fuel_rate
budget_capex = final_peak_kw * CAPEX_FACTOR
w_per_m2 = (final_peak_kw * 1000) / area_val if area_val > 0 else 0

# Chart
c_data = pd.DataFrame({
    'Category': ['Infiltration', 'Ext Walls', 'Int Walls', 'Floor', 'Roof', 'Doors', 'Preheat'],
    'kW': [inf_loss/1000, ext_wall_loss/1000, int_wall_loss/1000, floor_loss/1000, roof_loss/1000, door_loss/1000, preheat_kw]
}).sort_values('kW', ascending=False)

# --- 5. DUCT SIZING TOOL (WITH 3000MM RANGE & WARNINGS) ---
if not report_ready:
    with st.expander("📏 Internal Duct Sizing & Pressure Loss Tool", expanded=False):
        st.markdown("### Engineering Calculation (Non-Proposal)")
        ds_mode = st.radio("Duct Flow Source", ["Calculate from Project Heat Loss", "User Defined Manual Volume"], horizontal=True)
        
        if ds_mode == "Calculate from Project Heat Loss":
            num_ahus = st.number_input("Number of AHUs/Units", value=1, min_value=1)
            active_flow_h = req_airflow_total_h / num_ahus
        else:
            active_flow_h = st.number_input("Manual Airflow Volume (m³/h)", value=5000)
            
        active_flow_m3s = active_flow_h / 3600
        ds_col1, ds_col2 = st.columns(2)
        v_limit = ds_col1.number_input("Target Velocity Limit (m/s)", value=5.0, step=0.5)
        duct_type = ds_col2.radio("Duct Type", ["Circular", "Rectangular"], horizontal=True)
        
        req_area_m2 = active_flow_m3s / v_limit if v_limit > 0 else 0
        
        if duct_type == "Circular":
            req_diam_mm = math.sqrt((4 * req_area_m2) / math.pi) * 1000
            # EXTENDED RANGE 100-3000mm
            std_diams = [100, 150, 200, 250, 300, 315, 350, 400, 450, 500, 550, 600, 630, 710, 800, 850, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000]
            suggested_size = min([d for d in std_diams if d >= req_diam_mm], default=max(std_diams))
            actual_v = active_flow_m3s / (math.pi * (suggested_size/2000)**2)
            pa_per_m = (0.015 / (suggested_size/1000)) * (1.2 * (actual_v**2) / 2)
            
            dr1, dr2, dr3 = st.columns(3)
            dr1.metric("Suggested Std Size", f"{suggested_size} mm")
            
            # VELOCITY ALERT
            if actual_v > v_limit:
                dr2.error(f"⚠️ {actual_v:.1f} m/s")
                st.warning(f"Velocity exceeds {v_limit} m/s limit. Increase duct diameter.")
            else:
                dr2.metric("Actual Velocity", f"{actual_v:.1f} m/s")
            dr3.metric("Pressure Loss", f"{pa_per_m:.2f} Pa/m")
        else:
            fix_side = st.number_input("Known Side A (mm)", value=500)
            req_side_b = (req_area_m2 / (fix_side / 1000)) * 1000
            actual_v_rect = active_flow_m3s / ((fix_side/1000) * (req_side_b/1000))

            dr1, dr2, dr3 = st.columns(3)
            dr1.metric("Required Side B", f"{req_side_b:,.0f} mm")
            if actual_v_rect > v_limit:
                dr2.error(f"⚠️ {actual_v_rect:.1f} m/s")
            else:
                dr2.metric("Actual Velocity", f"{actual_v_rect:.1f} m/s")
            dr3.metric("Aspect Ratio", f"1:{max(fix_side,req_side_b)/min(fix_side,req_side_b):.1f}")

# --- 6. VIEWS ---
if not report_ready:
    st.divider()
    m_cols = st.columns(5 if show_budget else 4)
    m_cols[0].metric("Peak Design Load", f"{final_peak_kw:,.0f} kW")
    m_cols[1].metric("Heat Density", f"{w_per_m2:,.1f} W/m²")
    m_cols[2].metric("Heating Costs", f"£{annual_spend:,.0f}")
    m_cols[3].metric(f"Project Airflow ({airflow_unit})", f"{final_airflow_display:,.1f}" if airflow_unit == "m³/s" else f"{final_airflow_display:,.0f}")
    if show_budget: m_cols[4].metric("Budgetary Capex", f"£{budget_capex:,.0f}")
    
    fig = go.Figure(data=[go.Bar(x=c_data['Category'], y=c_data['kW'], marker_color=CROSS_BLUE, text=c_data['kW'].apply(lambda x: f"{x:,.1f} kW"), textposition='outside')])
    fig.update_layout(height=400, margin=dict(t=30, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)
else:
    # --- PROPOSAL VIEW ---
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
    st.write(f"Heating costs are estimated using the Standard Season Formula, based on using **{heat_source}**.")
    
    fig_rep = go.Figure(data=[go.Bar(x=c_data['Category'], y=c_data['kW'], marker_color=CROSS_BLUE, text=c_data['kW'].apply(lambda x: f"{x:,.1f} kW"), textposition='outside')])
    fig_rep.update_layout(height=400, margin=dict(t=30, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)', font=dict(color="black"))
    st.plotly_chart(fig_rep, use_container_width=True)

    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    # --- FULL 23 CLAUSES word-for-word from document ---
    st.header("Terms and Conditions of Sale")
    st.markdown("""
    <div class="tc-text tc-column">
    <p><strong>1. (a)</strong> It is hereby agreed that a contract shall be entered into between Cross Refrigeration (N.I.) Limited (hereinafter referred to as "the Company") and the person, Firm, Corporation, sole Undertaking, Association or Body, proposing to purchase from The Company (hereinafter referred to as "the Customer") any goods on foot of an order placed whether orally or in writing, by The Customer. <strong>(b)</strong> It is agreed that such contract as aforesaid shall be subject to the conditions hereinafter stipulated, and that such conditions supersede any earlier sets of conditions appearing in any of the Company's invoices, credit notes or any other documents whatsoever and shall override any terms and conditions and shall be binding upon the Customer unless otherwise stipulated herein and agreed to in writing by a duly authorised officer of the Company. <strong>(c)</strong> All guarantees, warranties and conditions, (including any conditions as to the quality or the fitness of the goods for any particular purpose, whether expressed or implied by statute, common law, or otherwise), are hereby excluded. <strong>(d)</strong> All goods supplied by the Company shall be in accordance with standards as specified by the Company and Customary trade standards subject to due allowance for processing any other recognised tolerances.</p>
    <p><strong>2.</strong> All orders for goods by the Customer through any agent or representative or sales representative of the Company shall be subject to the acceptance and approval of such order, or orders, by the Company and all deliveries of goods in respect of any such order or orders shall be subject to the approval and authorisation only by the Company, at its Head Office in Armagh, Northern Ireland.</p>
    <p><strong>3.</strong> It is hereby agreed that any price as quoted by the Company as comprised in the Contract is provisional only and shall be subject to market changes and changes in basic National Wage Agreement Rates, Freight Rates, Rates of Exchange, Costs of Materials, (including raw materials) or other relevant costs. Any goods supplied by the Company may be charged at the prices ruling as at the date of delivery to the Customer.</p>
    <p><strong>4.</strong> Unless otherwise expressly provided, it is agreed that all prices shall be exclusive of Value Added Tax or any other tax or taxes hereinafter imposed, whether statutory or otherwise, and it is further agreed that the Company shall be entitled to receive from the Customer any difference in price in respect of a variation in the value added tax rates.</p>
    <p><strong>5.</strong> Unless otherwise provided, it is agreed that all accounts shall be paid within 30 days of issue of the invoice. It is further agreed that all payments due shall be made on or before the due date as a condition precedent to further deliveries.</p>
    <p><strong>6.</strong> It is agreed that if preparation, manufacture or delivery of the goods is prevented or delayed in any way whatsoever by any Act of God or of any Government, War (whether declared or not) invasion or any other War like action, any strike, lockout or any Industrial Action or any civil disturbances, non-availability of raw materials, accident, mechanical failures, fire or any other event, or any action of a third party whatsoever, beyond the Company's reasonable control, then in any such circumstances the Company may upon reasonable notice, terminate, or amend this Contract or any obligation thereunder.</p>
    <p><strong>7.</strong> It is agreed that the goods shall be packed and secured in such a manner to reach the destination in good condition under normal conditions of transport and shall be delivered by the Company at or dispatched for delivery to the place or places in such a manner as specified in the order or subsequently agreed. Delivery to any such place or places shall be deemed to be affected by delivery at the nearest off-loading point or hard surface road adjoining such place of delivery.</p>
    <p><strong>8.</strong> The Company shall endeavour to meet delivery dates, but shall be under no liability of any kind if it fails to meet any such date or dates, whatever the cause of failure and whether such causes is under the Company's control or not. If so required by the Company the delivery date or dates may be extended for a reasonable period.</p>
    <p><strong>9. (a)</strong> If for any reason the Customer is unable to accept the delivery of the goods at the time when the goods are due and ready for delivery by the Company, then the Company, if its storage facilities permit, may agree to store the goods and safeguard them until their delivery and the Customer shall be liable to the Company for storage, insurance and other expenses. <strong>(b)</strong> The signature of any employee of the Customer acknowledging receipt of the goods shall be conclusive evidence of the receipt of such goods as specified in the relevant delivery docket or other documentation.</p>
    <p><strong>10. (a)</strong> Where goods are delivered by public carrier the liability of the Company shall cease immediately after such goods are delivered to the said carrier its servants or agents for the delivery to the Customer. <strong>(b)</strong> No claim for damages or shortages will be considered unless the Company and any carriers are advised in writing within seven days of the date of delivery and no claim for non-delivery shall be considered unless the Company and any carriers are notified within ten days of the date of dispatch.</p>
    <p><strong>11.</strong> It is agreed that the time of payment shall be of the essence of the contract and that all accounts shall be paid for in accordance with Clause 5 hereof. If the Customer should fail to make payment on the due date for goods ordered or delivered by the Company to the Customer under this or under any other contract, then the Company may, at its discretion, suspend further deliveries or effect such further deliveries and if any payment or part thereof shall remain in arrears for seven days after written demand shall have been made therefore, the Company may cancel this or any other contracts. The Company shall be entitled to charge interest at the rate of 2% per month on any overdue account.</p>
    <p><strong>12.</strong> In addition to any right to which the Company may be entitled under statute, common law or otherwise, the Company shall be entitled to retain possession of all goods in its possession or under its control for the unpaid price of any goods sold to the Customer by the Company under this or any other contract.</p>
    <p><strong>13.</strong> In addition to any other right of stoppage in transit to which the Company may be entitled under statute, common law or otherwise, the Company shall be entitled to retain and regain possession of all goods sold by the Company to the Customer which are in transit for the unpaid price of such goods or any goods sold to the Customer under this contract or any other contract.</p>
    <p><strong>14. (a)</strong> Where specifications are to be supplied by the Customer to the Company then it is agreed that the Customer shall supply such specifications to the Company in such reasonable time as will enable the Company to compete, manufacture and deliver. <strong>(b)</strong> Where any goods of a special nature are manufactured and delivered in accordance with the Customer's design, pattern, drawings, sample or materials then the Company's interest shall be confined to Manufacture in accordance with the Customer's requirements and under no circumstances shall the Company be liable or responsible to the Customer or any other person or persons whatsoever for any loss or damage howsoever caused. <strong>(c)</strong> In view of recurring improvements in design, we do not bind ourselves to supply equipment identical to the specification. <strong>(d)</strong> If materials are not available as specified, we reserve the right to substitute other materials if in our opinion such substituted materials are suitable.</p>
    <p><strong>15.</strong> In respect of new equipment the Company shall extend to the Customer the manufacturer's appropriate warranty (if any) and such warranty shall operate in place of all other warranties, conditions or liabilities expressed or implied by law, all of which are hereby expressly excluded. During the warranty period, the Company shall be entitled to inspect equipment at all reasonable times. Title to said machinery and materials shall remain in the possession of the Company until all sums due to the Company have been fully paid in cash.</p>
    <p><strong>16.</strong> If the Customer should make default in, or commit a breach of, this contract or of any other contract between the Customer and the Company or of any of the obligations of the Customer to the Company, howsoever arising, or if any distress, execution or other process be levied upon the Customers property or assets, the Company shall have the right forthwith to suspend all further deliveries to the Customer and to determine with or without notice any contract then subsisting between the Company and the Customer.</p>
    <p><strong>17.</strong> Notwithstanding any other provisions or agreement to payments in this contract, if, in the sole and absolute opinion of the Company, the financial position of the Customer warrants such action, then the Company may demand payment in cash or bankers draft, before delivery of all or any part or parts of the goods.</p>
    <p><strong>18.</strong> It is further agreed that in the event of any of these matters referred to in Clause 17 arising or occurring, then the Customer agrees to indemnify the Company against any loss, damage or expense incurred by the Company in connection with the contract.</p>
    <p><strong>19. (a)</strong> The ownership of all goods supplied by the Company to the Customer under this contract shall remain in the Company until such times as all Debts due to the Company from the Customer in respect of this or any other contract, have been paid by or on behalf of the Customer. <strong>(b)</strong> Until such time as all debts as aforesaid have been discharged in full, the Customer shall store the goods separately, hold the goods as bailee and trustee for the Company, keep separate books of account, and furnish particulars of any sub-purchasers. <strong>(c)</strong> The Company or its Authorised Agents may without notice re-take possession of any materials or machinery.</p>
    <p><strong>20.</strong> It is agreed that the risk in the goods shall pass to the Customer or any carrier or agent acting on his behalf and it is further agreed that the provisions hereof shall not entitle the Customer to return any goods or refuse or delay payment on the grounds that his property on such goods is not passed to the Customer.</p>
    <p><strong>21.</strong> It is agreed that this contract shall be deemed to have been made at the registered office of the Company and that all disputes, differences and questions shall be decided in accordance with the laws of Northern Ireland.</p>
    <p><strong>22.</strong> It is agreed that the Company does not warrant any particulars, specifications or otherwise as being accurate and the Company reserves the right to alter any such particulars or details where necessary. Any specifications, drawing or any other details whatsoever prepared by the Company for the purpose of a quotation or tender or otherwise shall remain the property of the Company, and shall be returned on request and shall not be used by the Customer for any purpose other than the purpose of the contract and the Customer shall not disclose them to a third party or parties and shall not copy, use, pass or in any other way dispose of such specifications and details without specific consent in writing of the Company.</p>
    <p><strong>23.</strong> A scheduled order (that is an order calling for specific quantity of goods for delivery spread over a period whether specified or not) shall constitute unqualified authority to the Company for the manufacture of that quantity and if the Customer shall fail to call on that quantity within the period specified in such order or orders then the Customer shall be liable to reimburse the Company for all loss or expenses incurred by it as a result of such failure. If the Schedule Order does not specify the date or dates on which the final delivery of the total quantity are to be made, then the Company shall be entitled to require the Customer to accept delivery of the specified quantity or quantities stated in such order or orders within a period not exceeding a maximum of twelve months from the date when such order was received.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⬅️ Back to Editor"): st.rerun()

# --- 7. EXPORT ---
p_data = { "proj_name": proj_name, "area_val": area_val, "height_val": height_val, "ach_val": ach_val, "door_area_val": door_area_val, "ext_wall_len": ext_wall_len, "int_wall_len": int_wall_len, "client_name": client_name, "contact_person": contact_person, "cross_ref": cross_ref, "target_temp": target_temp, "ext_temp": ext_temp, "delta_t_int": delta_t_int, "preheat_pct": preheat_pct, "supply_delta": supply_delta, "airflow_unit": airflow_unit, "show_budget": show_budget, "heat_source": heat_source, "elec_price": elec_price, "gas_price": gas_price, "cop": cop, "full_load_hrs": full_load_hrs, "season_days": season_days, "u_wall_ext": u_wall_ext, "u_wall_int": u_wall_int, "u_floor": u_floor, "u_roof": u_roof, "u_door": u_door }
st.sidebar.download_button("📥 Export Project Data", data=json.dumps(p_data), file_name=f"audit_{proj_name}.json", use_container_width=True)