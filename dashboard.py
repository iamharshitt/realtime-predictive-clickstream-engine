import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import time

# Set up clean, professional page configurations
st.set_page_config(
    page_title="Real-Time E-Commerce Engine",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Live Enterprise Clickstream & ML Inference Command Center")
st.markdown("This dashboard updates live every 2 seconds by pulling real-time streaming data from our processed SQL database store.")

# Create an empty container that we will continuously clear and redraw
DB_URI = "postgresql://postgres.tzqnmqmfhnwppzgujrjn:Khushank@2008@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
placeholder = st.empty()

def fetch_live_data():
    """Establishes a connection to the DB and extracts all records into a Pandas DataFrame."""
    conn = sqlite3.connect('analytics.db')
    query = "SELECT * FROM processed_clicks"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- THE LIVE REFRESH LOOP ---
while True:
    try:
        df = fetch_live_data()
        
        # Avoid crashing if the database is initialized but empty
        if len(df) == 0:
            with placeholder.container():
                st.warning("Waiting for data stream pipeline to write first records...")
            time.sleep(2)
            continue
            
        # --- CALCULATE REAL-TIME BUSINESS KPI METRICS ---
        total_events = len(df)
        total_revenue = df[df['action'] == 'purchase']['price'].sum()
        avg_ml_score = df['risk_score'].mean()
        high_risk_alerts = len(df[df['risk_score'] > 0.5])
        
        with placeholder.container():
            # 1. Top Level Executive KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📦 Monitored Events (Total Logs)", f"{total_events:,}")
            col2.metric("💰 Live Monitored Revenue", f"${total_revenue:,.2f}")
            col3.metric("🧠 Mean ML Intent Score", f"{avg_ml_score:.2f}")
            col4.metric("🚨 High Intent/Risk Alerts", f"{high_risk_alerts}", delta_color="inverse")
            
            st.markdown("---")
            
            # 2. Advanced Interactive Charts Row
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("📈 Revenue Growth & Purchase Influx Trends")
                purchase_df = df[df['action'] == 'purchase'].copy()
                if not purchase_df.empty:
                    # Line graph showing revenue progression over timeline
                    purchase_df['timestamp'] = pd.to_datetime(purchase_df['timestamp'])
                    purchase_df = purchase_df.sort_values('timestamp')
                    purchase_df['cumulative_revenue'] = purchase_df['price'].cumsum()
                    
                    fig_line = px.line(
                        purchase_df, x='timestamp', y='cumulative_revenue',
                        labels={'cumulative_revenue': 'Total Revenue ($)', 'timestamp': 'Time'},
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.info("Waiting for a 'purchase' event to populate line trend chart...")
                    
            with chart_col2:
                st.subheader("📱 Traffic Influx Distribution by Device Type")
                device_counts = df['device'].value_counts().reset_index()
                device_counts.columns = ['Device', 'Count']
                fig_pie = px.pie(
                    device_counts, values='Count', names='Device',
                    hole=0.4, template="plotly_dark",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
            st.markdown("---")
            
            # 3. Live Log Feed & High Threat Monitoring Panel
            log_col1, log_col2 = st.columns([2, 1])
            
            with log_col1:
                st.subheader("📥 Live Pipeline Data Stream (Latest 10 Logs)")
                st.dataframe(df.tail(10)[['user_id', 'timestamp', 'product', 'price', 'action', 'device', 'risk_score']].iloc[::-1], use_container_width=True)
                
            with log_col2:
                st.subheader("🚨 Critical ML Exception Board (>0.5)")
                high_risk_df = df[df['risk_score'] > 0.5].tail(5).iloc[::-1]
                if not high_risk_df.empty:
                    for idx, row in high_risk_df.iterrows():
                        st.error(f"⚠️ **User:** {row['user_id']} | **Score:** {row['risk_score']} \n\n Action: *{row['action']}* on *{row['product']}* (${row['price']})")
                else:
                    st.success("System Stable: No critical anomalies or high risk activity flags detected.")
                    
        # Pause for 2 seconds before flushing database memory and redrawing UI components
        time.sleep(2)
        
    except Exception as e:
        # Prevent database lock or collision crashes from disrupting the view loop
        time.sleep(1)