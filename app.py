import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pumping Iron Dashboard", layout="wide")

# --- CUSTOM CSS FOR GLASSMORPHISM ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        color: white;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: rgba(0, 200, 255, 0.3);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA PERSISTENCE ---
DATA_FILE = "data.csv"
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Date", "Exercise", "Sets", "Reps", "Weight", "Volume", "Type"])
    df.to_csv(DATA_FILE, index=False)

def load_data():
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# --- SIDEBAR: GAINZ ENTRY ---
st.sidebar.header("🏋️ Log Your Set")
with st.sidebar.form("entry_form", clear_on_submit=True):
    date = st.date_input("Date", datetime.now())
    exercise = st.text_input("Exercise Name (e.g., Lat Pulldown)")
    set_type = st.selectbox("Set Type", ["Regular", "Superset", "Drop Set", "Giant Set", "Low Rest Set"])
    cols = st.columns(3)
    sets = cols[0].number_input("Sets", min_value=1, value=3)
    reps = cols[1].number_input("Reps", min_value=1, value=12)
    weight = cols[2].number_input("Weight (kg)", min_value=0.0, value=20.0)
    
    submit = st.form_submit_button("Record Gains")

if submit:
    volume = sets * reps * weight
    new_data = pd.DataFrame([[date.strftime("%d-%b-%y"), exercise, sets, reps, weight, volume, set_type]], 
                            columns=["Date", "Exercise", "Sets", "Reps", "Weight", "Volume", "Type"])
    new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
    st.sidebar.success(f"Added {volume}kg of volume!")

# --- MAIN DASHBOARD ---
st.title("🔥 Pumping Iron: Volume Analytics")
df = load_data()

if not df.empty:
    # --- METRICS ---
    m_col1, m_col2, m_col3 = st.columns(3)
    total_vol = df['Volume'].sum()
    daily_vol = df[df['Date'].dt.date == datetime.now().date()]['Volume'].sum()
    
    m_col1.metric("Total Lifetime Volume", f"{total_vol:,} kg")
    m_col2.metric("Today's Volume", f"{daily_vol:,} kg")
    m_col3.metric("Favorite Lift", df['Exercise'].mode()[0] if not df['Exercise'].empty else "N/A")

    # --- GLASS STYLE VOLUME TREND ---
    st.subheader("📈 Volume Progression")
    trend_df = df.groupby('Date')['Volume'].sum().reset_index()
    fig = px.area(trend_df, x='Date', y='Volume', template="plotly_dark")
    fig.update_traces(line_color='#00d2ff', fillcolor='rgba(0, 210, 255, 0.2)')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- EXCEL STYLE TABLE WITH COLOR CODING ---
    st.subheader("📋 Training Log")
    
    # Mapping colors to types for visual flair
    color_map = {
        "Superset": "background-color: #FFA500; color: black;",
        "Giant Set": "background-color: #FF69B4; color: black;",
        "Low Rest Set": "background-color: #FFDAB9; color: black;",
        "Regular": "background-color: #ADD8E6; color: black;",
        "Drop Set": "background-color: #90EE90; color: black;"
    }
    
    def style_rows(row):
        return [color_map.get(row['Type'], '')] * len(row)

    styled_df = df.sort_values(by='Date', ascending=False).head(20).style.apply(style_rows, axis=1)
    st.write(styled_df)

else:
    st.info("No data yet. Start lifting and logging!")
