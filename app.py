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
        .tc-column {{ column-count: 2; column-gap: 25px; }}
    }}
    section[data-testid="stSidebar"] {{ background-color: {CROSS_DARK}; color: white; }}
    [data-testid="stMetricValue"] {{ color: {CROSS_BLUE} !important; font-weight: 800; }}
    .stMetric {{ background-color: #f1f5f9; border-top: 5px solid {CROSS_RED}; border-radius: 8px; }}
    h1, h2, h3 {{ color: {CROSS_DARK}; font-weight: 900; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR & DATA LOADING ---
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    else:
        st.markdown(f"<h2 style='color:{CROSS_BLUE}; text-align:center;'>CROSS GROUP</h2>", unsafe_allow_html=True)
    
    st.markdown(f"<p style='color: #94a3b8; font-size: 0.75rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; text-align: center;'>Advanced Temperature Control</p>", unsafe_allow_html=True)
    st.divider()

    with st.expander("💾 Project Data Control", expanded=True):
        uploaded_file = st.file_uploader("Load Project (.json)", type="json")
        save_data = json.load(uploaded_file) if uploaded_file else {}

    def get_val(key, default):
        return save_data.get(key, default)

    # PROPOSAL SETTINGS
    with st.expander("📄 Proposal Details", expanded=True):
        client_name = st.text_input("Client Name", value=get_val("client_name", ""))
        contact_person = st.text_input("Contact Person", value=get_val("contact_person", ""))
        cross_ref = st.text_input("Cross Reference", value=get_val("cross_ref", ""))
        report_ready = st.toggle("🚀 Generate Final Proposal", value=False)

    # HEATING & UTILITIES
    with st.expander("🔥 Heating System & Utilities", expanded=False):
        heat_source = st.selectbox("Heat Source", ["Gas", "Electric", "Heat Pump"], index=0)
        cop = st.number_input("Heat Pump COP", value=get_val("cop", 3.5)) if heat_source == "Heat Pump" else 1.0
        elec_price = st.number_input("Elec Price (£/kWh)", value=get_val("elec_price", 0.28))
        gas_price = st.number_input("Gas Price (£/kWh)", value=get_val("gas_price", 0.08))

    # U-VALUES
    with st.expander("🏗️ U-Value Calibration", expanded=False):
        u_wall_ext = st.number_input("External Walls", value=get_val("u_wall_ext", 0.25))
        u_wall_int = st.number_input("Internal Walls", value=get_val("u_wall_int", 1.50))
        u_floor = st.number_input("Floor", value=get_val("u_floor", 0.15))
        u_roof = st.number_input("Roof", value=get_val("u_roof", 0.18))
        u_window = st.number_input("Windows", value=get_val("u_window", 1.31))
        u_door = st.number_input("Doors", value=get_val("u_door", 1.30))

# --- 3. THE WORKBENCH INPUTS (Now outside the IF to keep data alive) ---
if not report_ready:
    st.title("Proposal Workbench")
    
    r1c1, r1c2 = st.columns(2)
    proj_name = r1c1.text_input("Project Reference", value=get_val("proj_name", ""))
    area_val = r1c2.number_input("Floor Area (m²)", value=get_val("area_val", 0.0))

    st.subheader("Room Parameters")
    c1, c2, c3, c4 = st.columns(4)
    height_val = c1.number_input("Height (m)", value=get_val("height_val", 0.0))
    ach_val = c2.number_input("ACH", value=get_val("ach_val", 0.5))
    win_area_val = c3.number_input("Windows (m²)", value=get_val("win_area_val", 0.0))
    door_area_val = c4.number_input("Doors (m²)", value=get_val("door_area_val", 0.0))

    st.subheader("Surface Exposures")
    r2c1, r2c2 = st.columns(2)
    ext_wall_area_val = r2c1.number_input("External Wall Area (m²)", value=get_val("ext_wall_area_val", 0.0))
    int_wall_area_val = r2c2.number_input("Internal Wall Area (m²)", value=get_val("int_wall_area_val", 0.0))
    
    # Store these in session state so they persist when we toggle the report
    st.session_state.update({
        "proj_name": proj_name, "area_val": area_val, "height_val": height_val,
        "ach_val": ach_val, "win_area_val": win_area_val, "door_area_val": door_area_val,
        "ext_wall_area_val": ext_wall_area_val, "int_wall_area_val": int_wall_area_val
    })

# If report is ready, we fetch from the session state we just updated
else:
    proj_name = st.session_state.get("proj_name", "")
    area_val = st.session_state.get("area_val", 0.0)
    height_val = st.session_state.get("height_val", 0.0)
    ach_val = st.session_state.get("ach_val", 0.5)
    win_area_val = st.session_state.get("win_area_val", 0.0)
    door_area_val = st.session_state.get("door_area_val", 0.0)
    ext_wall_area_val = st.session_state.get("ext_wall_area_val", 0.0)
    int_wall_area_val = st.session_state.get("int_wall_area_val", 0.0)

# --- 4. GLOBAL CALCULATIONS ---
delta_t_ext = 25 
vol = area_val * height_val
inf_loss = 0.33 * ach_val * vol * delta_t_ext
ext_wall_loss = ext_wall_area_val * u_wall_ext * delta_t_ext
int_wall_loss = int_wall_area_val * u_wall_int * 5 
floor_loss = area_val * u_floor * delta_t_ext
roof_loss = area_val * u_roof * delta_t_ext
door_loss = door_area_val * u_door * delta_t_ext
win_loss = win_area_val * u_window * delta_t_ext

total_kw = (inf_loss + ext_wall_loss + int_wall_loss + floor_loss + roof_loss + door_loss + win_loss) / 1000
peak_kw = total_kw * 1.15
budget_capex = peak_kw * CAPEX_FACTOR

# Chart
df_chart = pd.DataFrame({
    'Category': ['Infiltration', 'Ext Walls', 'Int Walls', 'Floor', 'Roof', 'Doors', 'Windows'],
    'Loss (W)': [inf_loss, ext_wall_loss, int_wall_loss, floor_loss, roof_loss, door_loss, win_loss]
}).sort_values(by='Loss (W)', ascending=False)
fig = go.Figure(data=[go.Bar(x=df_chart['Category'], y=df_chart['Loss (W)'], marker_color=CROSS_BLUE)])
fig.update_layout(height=350, margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor='rgba(0,0,0,0)')

# --- 5. FINAL VIEWS ---
if not report_ready:
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Peak Load", f"{peak_kw:,.1f} kW")
    m2.metric("Building Vol", f"{vol:,.0f} m³")
    m3.metric("Budget Capex", f"£{budget_capex:,.0f}")
    st.plotly_chart(fig, use_container_width=True)

else:
    # PROPOSAL HEADER
    c1, c2 = st.columns([1,1])
    with c1:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=220)
    with c2:
        st.markdown(f"<div style='text-align:right; color:{CROSS_BLUE}; font-weight:bold;'>REF: CROSS {cross_ref if cross_ref else '__________'}</div>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; border: 2px solid {CROSS_BLUE}; padding: 60px; border-radius: 10px;">
            <h1 style="font-size: 3.5rem; margin-bottom: 0;">PROPOSAL</h1>
            <p style="color:{CROSS_RED}; letter-spacing: 5px; font-weight: bold; font-size: 1.2rem;">ADVANCED TEMPERATURE CONTROL</p>
            <br><br>
            <h3>CLIENT: {client_name if client_name else "___________________"}</h3>
            <h3>PROJECT: {proj_name if proj_name else "___________________"}</h3>
            <p>Date: {pd.Timestamp.now().strftime('%d %B %Y')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)

    # PAGE 2
    st.header("Budget Quotation Overview")
    st.write(f"**Attention:** {contact_person if contact_person else 'Sir / Madam'},")
    st.write(f"**Client:** {client_name}")
    st.write(f"**Ref:** {proj_name}")
    st.write("Dear Sir,")
    st.write("Further to your recent enquiry, please find enclosed our Budget Costs and outlined specification in respect of the above project.")
    
    st.subheader("Thermal Performance Assessment")
    p1, p2, p3 = st.columns(3)
    p1.metric("Peak Design Load", f"{peak_kw:,.1f} kW")
    p2.metric("Building Volume", f"{vol:,.0f} m³")
    p3.metric("Projected Capex", f"£{budget_capex:,.0f}")

    st.subheader("Heat Loss Breakdown")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)

    # PAGE 3: FULL TERMS & CONDITIONS (ALL 23 CLAUSES)
    st.header("Terms and Conditions of Sale")
    st.markdown("""
    <div class="tc-text tc-column">
    <p><strong>1. (a)</strong> It is hereby agreed that a contract shall be entered into between Cross Refrigeration (N.I.) Limited (hereinafter referred to as "the Company") and the person, Firm, Corporation, sole Undertaking, Association or Body, proposing to purchase from The Company (hereinafter referred to as "the Customer") any goods on foot of an order placed whether orally or in writing, by The Customer. <strong>(b)</strong> It is agreed that such contract shall be subject to the conditions hereinafter stipulated, supersede any earlier sets of conditions, and shall override any terms and conditions binding upon the Customer unless otherwise agreed in writing. <strong>(c)</strong> All guarantees, warranties and conditions, whether expressed or implied by statute, common law, or otherwise, are hereby excluded. <strong>(d)</strong> All goods supplied shall be in accordance with standards specified by the Company and Customary trade standards.</p>
    <p><strong>2.</strong> All orders through any agent or representative of the Company shall be subject to acceptance and approval by the Company at its Head Office in Armagh, Northern Ireland.</p>
    <p><strong>3.</strong> Any price quoted is provisional only and shall be subject to market changes, National Wage Agreement Rates, Freight Rates, Rates of Exchange, Costs of Materials, or other relevant costs. Goods may be charged at prices ruling at the date of delivery.</p>
    <p><strong>4.</strong> Unless expressly provided, prices shall be exclusive of Value Added Tax. The Company is entitled to receive any difference in price due to variation in V.A.T. rates.</p>
    <p><strong>5.</strong> Unless otherwise provided, all accounts shall be paid within 30 days of issue of the invoice. Payment is a condition precedent to further deliveries.</p>
    <p><strong>6.</strong> If delivery is prevented or delayed by Act of God, Government, War, strike, lockout, civil disturbances, or other events beyond the Company's control, the Company may terminate or amend the Contract without liability.</p>
    <p><strong>7.</strong> Goods shall be packed to reach the destination in good condition under normal transport and delivered to the nearest off-loading point.</p>
    <p><strong>8.</strong> The Company shall endeavour to meet delivery dates but shall be under no liability for failure to meet such dates.</p>
    <p><strong>9. (a)</strong> If the Customer cannot accept delivery, the Company may store goods at the Customer's expense. <strong>(b)</strong> Signature of any employee acknowledging receipt is conclusive evidence of receipt.</p>
    <p><strong>10. (a)</strong> Liability ceases immediately after goods are delivered to a public carrier. <strong>(b)</strong> Shortage or damage claims must be made in writing within seven days of delivery.</p>
    <p><strong>11.</strong> Time of payment is of the essence. Interest charged at 2% per month on overdue accounts.</p>
    <p><strong>12.</strong> The Company is entitled to retain possession of all goods for the unpaid price of any goods sold under this or any other contract.</p>
    <p><strong>13.</strong> Stoppage in transit rights allow the Company to regain possession of goods for the unpaid price.</p>
    <p><strong>14. (a)</strong> Specifications must be supplied by the Customer. <strong>(b)</strong> For special goods made to Customer design, the Company is not liable for faults in design. <strong>(c)</strong> Equipment may vary from specification due to improvements. <strong>(d)</strong> Substituted materials may be used.</p>
    <p><strong>15.</strong> The Company extends the manufacturer's appropriate warranty. Warranty does not include labour, refrigerant, or taxes. Accidental damage voids warranty.</p>
    <p><strong>16.</strong> If the Customer defaults or enters bankruptcy/liquidation, the Company may suspend deliveries and determine the contract.</p>
    <p><strong>17.</strong> If the Customer's financial position warrants it, the Company may demand cash payment before delivery.</p>
    <p><strong>18.</strong> In the event of Clause 17 arising, the Customer shall indemnify the Company against all loss and expenses.</p>
    <p><strong>19. (a)</strong> Ownership remains with the Company until all debts are paid in full. <strong>(b)</strong> Customer must store goods separately. <strong>(c)</strong> Company may re-take possession without notice.</p>
    <p><strong>20.</strong> Risk passes upon delivery. Provisions do not entitle Customer to delay payment.</p>
    <p><strong>21.</strong> Contract deemed made at the registered office; disputes decided under the laws of Northern Ireland.</p>
    <p><strong>22.</strong> Specifications and drawings remain Company property, must be returned on request, and cannot be disclosed to third parties.</p>
    <p><strong>23.</strong> Scheduled orders constitute authority for manufacture. Failure to call on quantity results in liability for all Company loss and expenses.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⬅️ Back to Editor"): st.rerun()

# --- 6. EXPORT ---
current_params = {
    "proj_name": proj_name, "area_val": area_val, "height_val": height_val, "ach_val": ach_val,
    "win_area_val": win_area_val, "door_area_val": door_area_val,
    "ext_wall_area_val": ext_wall_area_val, "int_wall_area_val": int_wall_area_val,
    "client_name": client_name, "contact_person": contact_person, "cross_ref": cross_ref
}
json_string = json.dumps(current_params)
with st.sidebar:
    st.divider()
    st.download_button(label="📥 Export Project Data", data=json_string, file_name=f"audit_{proj_name}.json", mime="application/json", use_container_width=True)