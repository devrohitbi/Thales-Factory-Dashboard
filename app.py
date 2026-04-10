import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="Thales Operational Hub", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    div[data-testid="stMetric"] {
        background: white; border-radius: 10px; padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 5px solid #0052cc;
    }
    .main-title { color: #091e42; font-size: 32px; font-weight: bold; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- DATA ENGINE ---
@st.cache_data
def load_data():
    df = pd.read_csv("Thales_Group_Manufacturing_cleaned_data.csv")
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['Machine_Label'] = "Machine " + df['Machine_ID'].astype(str)
    return df

df = load_data()

# --- SIDEBAR (USER CAPABILITIES) ---
st.sidebar.markdown("### 🛠️ Control Panel")

# 1. Machine Selector (Sorted)
m_list = sorted(df['Machine_Label'].unique(), key=lambda x: int(x.split()[1]))
selected_units = st.sidebar.multiselect("Select Machines to Compare", m_list, default=m_list[:5])

# 2. Operation Mode Filter
modes = ["All Modes"] + list(df['Operation_Mode'].unique())
selected_mode = st.sidebar.selectbox("Filter by Operation Status", modes)

# 3. Date & Time Range Selector
st.sidebar.markdown("---")
st.sidebar.write("📅 *Timeframe Selection*")
start_dt = st.sidebar.date_input("Start Date", df['Date'].min())
end_dt = st.sidebar.date_input("End Date", df['Date'].max())

# 4. Metric Comparison Toggles
st.sidebar.markdown("---")
st.sidebar.write("📊 *Metric Display Settings*")
view_temp = st.sidebar.toggle("Temperature Analysis", value=True)
view_power = st.sidebar.toggle("Power Consumption", value=True)
view_speed = st.sidebar.toggle("Production Speed", value=False)

# --- FILTERING LOGIC ---
f_df = df[
    (df['Machine_Label'].isin(selected_units)) & 
    (df['Date'].dt.date >= start_dt) & 
    (df['Date'].dt.date <= end_dt)
]
if selected_mode != "All Modes":
    f_df = f_df[f_df['Operation_Mode'] == selected_mode]

# --- MAIN CONTENT ---
st.markdown("<h1 class='main-title'>🏭 Thales Smart Manufacturing Intelligence</h1>", unsafe_allow_html=True)

# TOP KPI SECTION
c1, c2, c3, c4 = st.columns(4)
c1.metric("Overall Health Index", f"{f_df['Predictive_Maintenance_Score'].mean():.1f}%")
c2.metric("Average Power Load", f"{f_df['Power_Consumption_kW'].mean():.2f} kW")
c3.metric("Daily Production Avg", f"{f_df['Production_Speed_units_per_hr'].mean():.0f} Units")
c4.metric("Quality Control Rate", f"{100 - f_df['Quality_Control_Defect_Rate_%'].mean():.2f}%")

st.markdown("---")

# --- DASHBOARD SECTION 1: HEATMAP (Comparison Simplified) ---
st.subheader("🌡️ Heatmap: Machine Performance Overview")
st.write("Colors (Red = Bad, Green = Good)")

# Creating a summary for Heatmap
pivot_df = f_df.groupby('Machine_Label')[['Predictive_Maintenance_Score', 'Temperature_C', 'Power_Consumption_kW']].mean()
fig_heat = px.imshow(pivot_df.T, text_auto=".1f", color_continuous_scale='RdYlGn', aspect="auto")
st.plotly_chart(fig_heat, use_container_width=True)

# --- DASHBOARD SECTION 2: COMPARISON BAR CHARTS ---
st.markdown("---")
st.subheader("📊 Operational Comparison (Bar Charts)")
left, right = st.columns(2)

with left:
    if view_temp:
        st.markdown("*Average Temperature per Unit*")
        avg_temp = f_df.groupby('Machine_Label')['Temperature_C'].mean().reset_index()
        fig_temp = px.bar(avg_temp, x='Machine_Label', y='Temperature_C', color='Temperature_C', color_continuous_scale='OrRd')
        st.plotly_chart(fig_temp, use_container_width=True)

with right:
    if view_power:
        st.markdown("*Power Consumption per Unit*")
        avg_pwr = f_df.groupby('Machine_Label')['Power_Consumption_kW'].mean().reset_index()
        fig_pwr = px.bar(avg_pwr, x='Machine_Label', y='Power_Consumption_kW', color='Power_Consumption_kW', color_continuous_scale='Blues')
        st.plotly_chart(fig_pwr, use_container_width=True)

# --- DASHBOARD SECTION 3: PRIORITY MAINTENANCE (NEAT & CLEAN) ---
st.markdown("---")
st.subheader("🚨 Priority Maintenance Action List")

# Identifying critical machines in a clean list
critical_df = f_df[f_df['Predictive_Maintenance_Score'] < 70].groupby('Machine_Label').agg({
    'Predictive_Maintenance_Score': 'mean',
    'Operation_Mode': lambda x: x.mode()[0]
}).reset_index()

if not critical_df.empty:
    st.error("The machines listed below are in critical condition and require maintenance.")
    # Professional Data Table
    st.table(critical_df.rename(columns={
        'Machine_Label': 'Machine Name',
        'Predictive_Maintenance_Score': 'Average Health Score',
        'Operation_Mode': 'Current Status'
    }).sort_values('Average Health Score'))
else:
    st.success("The Machines are in Good Condition.")

# Footer
st.sidebar.info("Operational Intelligence Dashboard v3.0")