import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io
import base64
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="APL Logistics Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS WITH ENHANCED STYLING
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #1f77b4, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA PROCESSING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def clean_data(df):
    """Clean and preprocess the raw logistics data"""
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    real_col = 'Days for shipping (real)'
    sched_col = 'Days for shipment (scheduled)'
    delivery_col = 'Delivery Status'
    late_risk_col = 'Late_delivery_risk'
    
    # Remove missing values in critical columns
    critical_cols = [delivery_col, real_col, sched_col, late_risk_col]
    df = df.dropna(subset=critical_cols)
    
    # Remove invalid delivery status values
    valid_statuses = ['Advance shipping', 'Late delivery', 'Shipping on time', 'Shipping canceled']
    df = df[df[delivery_col].isin(valid_statuses)]
    
    # Remove negative or zero shipping days
    df = df[(df[real_col] > 0) & (df[sched_col] > 0)]
    
    # Remove extreme shipping durations (> 60 days)
    df = df[(df[real_col] <= 60) & (df[sched_col] <= 60)]
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Standardize region and market names
    if 'Order Region' in df.columns:
        df['Order Region'] = df['Order Region'].str.title().str.strip()
    if 'Market' in df.columns:
        df['Market'] = df['Market'].str.title().str.strip()
    
    return df

def calculate_metrics(df):
    """Calculate delivery and financial metrics"""
    real_col = 'Days for shipping (real)'
    sched_col = 'Days for shipment (scheduled)'
    
    # 1. Delay gap calculation
    df['delay_gap'] = df[real_col] - df[sched_col]
    
    # 2. On-time delivery flag
    df['On_Time'] = (df['delay_gap'] <= 0).astype(int)
    
    # 3. Delivery classification
    conditions = [
        df['delay_gap'] < 0,
        df['delay_gap'] == 0,
        df['delay_gap'] > 0
    ]
    choices = ['Early', 'On Time', 'Late']
    df['delivery_classification'] = np.select(conditions, choices, default='Unknown')
    
    # 4. SLA status categorization
    sla_conditions = [
        df['delay_gap'] <= 0,
        (df['delay_gap'] > 0) & (df['delay_gap'] <= 2),
        (df['delay_gap'] > 2) & (df['delay_gap'] <= 5),
        df['delay_gap'] > 5
    ]
    sla_choices = ['SLA Met', 'Minor Breach', 'Critical Breach', 'Severe Breach']
    df['SLA_Status'] = np.select(sla_conditions, sla_choices, default='Unknown')
    
    # 5. Financial metrics
    if 'Sales' in df.columns and 'Order Profit Per Order' in df.columns:
        df['Profit_Margin_%'] = (df['Order Profit Per Order'] / df['Sales'] * 100).fillna(0)
    
    return df

def format_number(num):
    """Format large numbers with K, M suffixes"""
    if num >= 1_000_000:
        return f"${num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"${num/1_000:.1f}K"
    else:
        return f"${num:.0f}"

def create_download_link(df, filename, file_label):
    """Create a download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {file_label}</a>'
    return href

# ═══════════════════════════════════════════════════════════════════════════════
# FILE UPLOAD SECTION
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-header">📦 APL Logistics Dashboard</div>', unsafe_allow_html=True)

# Check if data is already loaded in session state
if 'df' not in st.session_state:
    st.markdown("""
    <div class="info-box">
        <h3>👋 Welcome to APL Logistics Dashboard!</h3>
        <p>Please upload your APL Logistics CSV file to get started.</p>
        <p><strong>Required columns:</strong> Days for shipping (real), Days for shipment (scheduled), 
        Delivery Status, Late_delivery_risk, Sales, Order Profit Per Order, Shipping Mode, Order Region, Market, Customer Segment</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("📂 Upload your CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            with st.spinner('🔄 Processing your data...'):
                # Read the CSV
                df_raw = pd.read_csv(uploaded_file, encoding='latin1')
                st.success(f"✅ Loaded {len(df_raw):,} rows × {len(df_raw.columns)} columns")
                
                # Clean and process data
                df_raw = clean_data(df_raw)
                df_raw = calculate_metrics(df_raw)
                
                # Store in session state
                st.session_state.df = df_raw
                st.success("✅ Data processed successfully!")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please make sure your CSV file has all the required columns.")
    
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# LOAD DATA FROM SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
df = st.session_state.df

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - FILTERS
# ═══════════════════════════════════════════════════════════════════════════════

st.sidebar.title("🎛️ Dashboard Controls")
st.sidebar.markdown("---")

# Add reset button
if st.sidebar.button("🔄 Upload New File"):
    del st.session_state.df
    st.rerun()

st.sidebar.subheader("🔍 Filters")

# Shipping mode filter
shipping_modes = ['All'] + sorted(df['Shipping Mode'].unique().tolist())
selected_shipping_mode = st.sidebar.selectbox("📦 Shipping Mode", shipping_modes, key='shipping_mode_filter')

# Region filter
regions = ['All'] + sorted(df['Order Region'].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("🌍 Region", regions, key='region_filter')

# Market filter
markets = ['All'] + sorted(df['Market'].dropna().unique().tolist())
selected_market = st.sidebar.selectbox("🌎 Market", markets, key='market_filter')

# Customer segment filter
segments = ['All'] + sorted(df['Customer Segment'].dropna().unique().tolist())
selected_segment = st.sidebar.selectbox("👥 Customer Segment", segments, key='segment_filter')

# SLA status filter
sla_statuses = ['All'] + sorted(df['SLA_Status'].unique().tolist())
selected_sla = st.sidebar.selectbox("⚠️ SLA Status", sla_statuses, key='sla_filter')

# Delay range selector
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Delay Range")
min_delay = int(df['delay_gap'].min())
max_delay = int(df['delay_gap'].max())
delay_range = st.sidebar.slider(
    "Delay Gap (days)",
    min_delay, max_delay, (min_delay, max_delay),
    key='delay_range_slider'
)

# APPLY FILTERS
filtered_df = df.copy()

if selected_shipping_mode != 'All':
    filtered_df = filtered_df[filtered_df['Shipping Mode'] == selected_shipping_mode]

if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Order Region'] == selected_region]

if selected_market != 'All':
    filtered_df = filtered_df[filtered_df['Market'] == selected_market]

if selected_segment != 'All':
    filtered_df = filtered_df[filtered_df['Customer Segment'] == selected_segment]

if selected_sla != 'All':
    filtered_df = filtered_df[filtered_df['SLA_Status'] == selected_sla]

filtered_df = filtered_df[
    (filtered_df['delay_gap'] >= delay_range[0]) &
    (filtered_df['delay_gap'] <= delay_range[1])
]

# Export section
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Export Data")
if st.sidebar.button("📊 Export Filtered Data"):
    st.sidebar.markdown(create_download_link(
        filtered_df,
        "apl_filtered_data.csv",
        "Filtered Dataset"
    ), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("### 🚀 Advanced Analytics with AI-Powered Insights")

# Show active filters
active_filters = []
if selected_shipping_mode != 'All': active_filters.append(f"📦 {selected_shipping_mode}")
if selected_region != 'All': active_filters.append(f"🌍 {selected_region}")
if selected_market != 'All': active_filters.append(f"🌎 {selected_market}")
if selected_segment != 'All': active_filters.append(f"👥 {selected_segment}")
if selected_sla != 'All': active_filters.append(f"⚠️ {selected_sla}")

if active_filters:
    st.markdown(f"**Active Filters:** {' | '.join(active_filters)}")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "💰 Financial Analysis",
    "🚚 Shipping Performance",
    "🔮 Predictive Insights",
    "📋 Detailed Reports"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("📊 Key Performance Indicators")
    
    # Calculate KPIs
    total_orders = len(filtered_df)
    total_revenue = filtered_df['Sales'].sum()
    total_profit = filtered_df['Order Profit Per Order'].sum()
    avg_profit_ratio = filtered_df['Order Item Profit Ratio'].mean() * 100
    on_time_rate = filtered_df['On_Time'].mean() * 100
    avg_delay = filtered_df['delay_gap'].mean()
    
    # Display KPIs in columns
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("📦 Total Orders", f"{total_orders:,}")
    
    with col2:
        st.metric("💰 Revenue", format_number(total_revenue))
    
    with col3:
        st.metric("💵 Profit", format_number(total_profit))
    
    with col4:
        st.metric("📈 Margin", f"{avg_profit_ratio:.1f}%")
    
    with col5:
        st.metric("✅ On-Time", f"{on_time_rate:.1f}%")
    
    with col6:
        st.metric("⏱️ Avg Delay", f"{avg_delay:.1f}d")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Delivery Performance")
        delivery_counts = filtered_df['delivery_classification'].value_counts()
        
        fig_delivery = go.Figure(data=[go.Pie(
            labels=delivery_counts.index,
            values=delivery_counts.values,
            hole=0.5,
            marker_colors=['#2ecc71', '#3498db', '#e74c3c'],
            textinfo='label+percent',
            textfont_size=14
        )])
        fig_delivery.update_layout(
            title="Delivery Classification Distribution",
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig_delivery, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ SLA Status")
        sla_counts = filtered_df['SLA_Status'].value_counts()
        
        colors_sla = {
            'SLA Met': '#2ecc71',
            'Minor Breach': '#f39c12',
            'Critical Breach': '#e67e22',
            'Severe Breach': '#e74c3c'
        }
        bar_colors = [colors_sla.get(x, '#95a5a6') for x in sla_counts.index]
        
        fig_sla = go.Figure(data=[go.Bar(
            x=sla_counts.index,
            y=sla_counts.values,
            marker_color=bar_colors,
            text=sla_counts.values,
            textposition='auto',
            textfont_size=14
        )])
        fig_sla.update_layout(
            title="SLA Status Distribution",
            xaxis_title="SLA Status",
            yaxis_title="Count",
            height=400
        )
        st.plotly_chart(fig_sla, use_container_width=True)
    
    st.markdown("---")
    
    # Regional heatmap
    st.subheader("🌍 Regional Performance Heatmap")
    region_metrics = filtered_df.groupby('Order Region').agg({
        'Sales': 'sum',
        'Order Profit Per Order': 'sum',
        'On_Time': 'mean',
        'delay_gap': 'mean'
    }).round(2)
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=region_metrics.values.T,
        x=region_metrics.index,
        y=['Revenue', 'Profit', 'On-Time Rate', 'Avg Delay'],
        colorscale='RdYlGn',
        text=region_metrics.values.T,
        texttemplate='%{text:.2f}',
        textfont={"size": 10}
    ))
    fig_heatmap.update_layout(
        title="Regional Performance Metrics",
        height=300
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: FINANCIAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("💰 Financial Impact Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("💹 Overall Profit Margin", f"{profit_margin:.2f}%")
    
    with col2:
        revenue_at_risk = filtered_df[filtered_df['Late_delivery_risk'] == 1]['Sales'].sum()
        st.metric("⚠️ Revenue at Risk", format_number(revenue_at_risk))
    
    with col3:
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        st.metric("💵 Avg Order Value", f"${avg_order_value:.2f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Revenue by SLA Status")
        sla_revenue = filtered_df.groupby('SLA_Status')['Sales'].sum().sort_values(ascending=False)
        
        fig_sla_rev = go.Figure(data=[go.Bar(
            x=sla_revenue.index,
            y=sla_revenue.values,
            marker_color=['#2ecc71', '#f39c12', '#e67e22', '#e74c3c'][:len(sla_revenue)],
            text=[format_number(v) for v in sla_revenue.values],
            textposition='auto'
        )])
        fig_sla_rev.update_layout(
            title="Total Revenue by SLA Status",
            xaxis_title="SLA Status",
            yaxis_title="Revenue ($)",
            height=400
        )
        st.plotly_chart(fig_sla_rev, use_container_width=True)
    
    with col2:
        st.subheader("💵 Profit by Delivery Type")
        class_profit = filtered_df.groupby('delivery_classification')['Order Profit Per Order'].sum()
        
        fig_class_profit = go.Figure(data=[go.Bar(
            x=class_profit.index,
            y=class_profit.values,
            marker_color=['#2ecc71', '#3498db', '#e74c3c'],
            text=[format_number(v) for v in class_profit.values],
            textposition='auto'
        )])
        fig_class_profit.update_layout(
            title="Total Profit by Delivery Classification",
            xaxis_title="Classification",
            yaxis_title="Profit ($)",
            height=400
        )
        st.plotly_chart(fig_class_profit, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: SHIPPING PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("🚚 Shipping Mode Performance Analysis")
    
    # Calculate shipping mode metrics
    mode_perf = filtered_df.groupby('Shipping Mode').agg(
        Total_Orders=('Sales', 'count'),
        Avg_Delay=('delay_gap', 'mean'),
        OnTime_Rate=('On_Time', 'mean'),
        Total_Revenue=('Sales', 'sum'),
        Total_Profit=('Order Profit Per Order', 'sum'),
    ).round(2)
    
    mode_perf['OnTime_Rate_Pct'] = (mode_perf['OnTime_Rate'] * 100).round(2)
    mode_perf['Efficiency_Score'] = (
        (mode_perf['OnTime_Rate_Pct'] * 0.6) -
        (mode_perf['Avg_Delay'] * 2)
    ).round(2)
    
    def assign_grade(score):
        if score >= 50: return '🏆 A'
        elif score >= 40: return '🥈 B'
        elif score >= 30: return '🥉 C'
        elif score >= 20: return '📉 D'
        else: return '❌ F'
    
    mode_perf['Grade'] = mode_perf['Efficiency_Score'].apply(assign_grade)
    mode_perf_sorted = mode_perf.sort_values('Efficiency_Score', ascending=False)
    
    # Display shipping mode rankings
    st.subheader("🏅 Shipping Mode Rankings")
    st.dataframe(
        mode_perf_sorted[['Grade', 'Efficiency_Score', 'OnTime_Rate_Pct', 'Avg_Delay', 'Total_Orders']],
        use_container_width=True
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Efficiency Score Comparison")
        fig_efficiency = go.Figure(data=[go.Bar(
            x=mode_perf_sorted.index,
            y=mode_perf_sorted['Efficiency_Score'],
            marker_color=mode_perf_sorted['Efficiency_Score'],
            marker_colorscale='RdYlGn',
            text=mode_perf_sorted['Efficiency_Score'],
            textposition='auto'
        )])
        fig_efficiency.update_layout(
            title="Shipping Mode Efficiency Scores",
            xaxis_title="Shipping Mode",
            yaxis_title="Efficiency Score",
            height=400
        )
        st.plotly_chart(fig_efficiency, use_container_width=True)
    
    with col2:
        st.subheader("💰 Revenue vs Profit Scatter")
        fig_scatter = go.Figure(data=[go.Scatter(
            x=mode_perf_sorted['Total_Revenue'],
            y=mode_perf_sorted['Total_Profit'],
            mode='markers+text',
            text=mode_perf_sorted.index,
            textposition='top center',
            marker=dict(
                size=mode_perf_sorted['Total_Orders']/100,
                color=mode_perf_sorted['Efficiency_Score'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Efficiency")
            )
        )])
        fig_scatter.update_layout(
            title="Revenue vs Profit (bubble size = orders)",
            xaxis_title="Total Revenue ($)",
            yaxis_title="Total Profit ($)",
            height=400
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: PREDICTIVE INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("🔮 Predictive Insights & Anomaly Detection")
    
    st.markdown("""
    <div class="info-box">
        <strong>📊 Statistical Analysis</strong><br>
        This section provides data-driven insights based on historical patterns.
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate percentiles for delay
    delay_percentiles = filtered_df['delay_gap'].quantile([0.25, 0.5, 0.75, 0.90, 0.95]).round(2)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Median Delay", f"{delay_percentiles[0.5]:.1f} days")
    
    with col2:
        st.metric("⚠️ 90th Percentile", f"{delay_percentiles[0.9]:.1f} days")
    
    with col3:
        st.metric("🔴 95th Percentile", f"{delay_percentiles[0.95]:.1f} days")
    
    st.markdown("---")
    
    # Delay distribution analysis
    st.subheader("📊 Delay Distribution Analysis")
    
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=filtered_df['delay_gap'],
        nbinsx=50,
        marker_color='#3498db',
        name='Delay Distribution'
    ))
    
    # Add percentile lines
    for percentile, color in [(0.5, 'green'), (0.9, 'orange'), (0.95, 'red')]:
        fig_hist.add_vline(
            x=delay_percentiles[percentile],
            line_dash="dash",
            line_color=color,
            annotation_text=f"{int(percentile*100)}th percentile"
        )
    
    fig_hist.update_layout(
        title="Delay Gap Distribution with Percentiles",
        xaxis_title="Delay Gap (days)",
        yaxis_title="Frequency",
        height=400
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: DETAILED REPORTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.header("📋 Detailed Reports & Data Tables")
    
    report_type = st.selectbox(
        "Select Report Type",
        ["Shipping Mode Analysis", "Regional Performance", "Market Analysis",
         "Customer Segment Analysis", "SLA Breach Details"]
    )
    
    if report_type == "Shipping Mode Analysis":
        st.subheader("🚚 Comprehensive Shipping Mode Report")
        
        mode_report = filtered_df.groupby('Shipping Mode').agg({
            'Sales': ['count', 'sum', 'mean'],
            'Order Profit Per Order': ['sum', 'mean'],
            'delay_gap': ['mean', 'std', 'min', 'max'],
            'On_Time': 'mean',
            'Late_delivery_risk': 'sum'
        }).round(2)
        
        mode_report.columns = ['_'.join(col).strip() for col in mode_report.columns.values]
        st.dataframe(mode_report, use_container_width=True)
        
        if st.button("📥 Download Shipping Mode Report"):
            st.markdown(create_download_link(
                mode_report.reset_index(),
                "shipping_mode_report.csv",
                "Shipping Mode Report"
            ), unsafe_allow_html=True)
    
    elif report_type == "Regional Performance":
        st.subheader("🌍 Regional Performance Report")
        
        region_report = filtered_df.groupby('Order Region').agg({
            'Sales': ['count', 'sum'],
            'Order Profit Per Order': 'sum',
            'delay_gap': 'mean',
            'On_Time': 'mean',
            'SLA_Status': lambda x: (x == 'SLA Met').mean()
        }).round(2)
        
        region_report.columns = ['Total_Orders', 'Total_Revenue', 'Total_Profit', 'Avg_Delay', 'OnTime_Rate', 'SLA_Met_Rate']
        region_report['OnTime_Rate'] = (region_report['OnTime_Rate'] * 100).round(2)
        region_report['SLA_Met_Rate'] = (region_report['SLA_Met_Rate'] * 100).round(2)
        region_report = region_report.sort_values('Total_Revenue', ascending=False)
        
        st.dataframe(region_report, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #7f8c8d;">
    <p><strong>APL Logistics Dashboard</strong> | Powered by Advanced Analytics</p>
    <p>📊 Real-time insights • 💰 Financial optimization • 🚚 Performance monitoring • 🔮 Predictive analytics</p>
</div>
""", unsafe_allow_html=True)
