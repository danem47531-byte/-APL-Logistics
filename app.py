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
import requests
import zipfile
import os
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
# AUTO-LOAD DATA FROM GITHUB
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_data_from_github():
    """Download and extract CSV from GitHub repository"""
    # REPLACE THIS URL with your actual GitHub raw file URL
    # Example: "https://github.com/USERNAME/REPO/raw/main/APL_Logistics.zip"
    GITHUB_ZIP_URL = "https://github.com/danem47531-byte/-APL-Logistics/raw/main/APL_Logistics.zip"
    
    try:
        # Download the zip file
        response = requests.get(GITHUB_ZIP_URL, timeout=30)
        response.raise_for_status()
        
        # Extract CSV from zip
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            # Get the first CSV file in the zip
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            if not csv_files:
                raise ValueError("No CSV file found in the zip archive")
            
            # Read the CSV
            with zip_ref.open(csv_files[0]) as csv_file:
                df = pd.read_csv(csv_file, encoding='latin1')
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading data from GitHub: {str(e)}")
        st.info("""
        **📝 Setup Instructions:**
        1. Replace `YOUR-USERNAME` and `YOUR-REPO-NAME` in the code with your actual GitHub details
        2. Make sure APL_Logistics.zip is in the main branch of your repository
        3. The URL should look like: `https://github.com/username/repo/raw/main/APL_Logistics.zip`
        """)
        st.stop()

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
# LOAD DATA AUTOMATICALLY
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-header">📦 APL Logistics Dashboard</div>', unsafe_allow_html=True)

# Check if data is already loaded in session state
if 'df' not in st.session_state:
    with st.spinner('🔄 Loading data from GitHub...'):
        try:
            # Load data from GitHub
            df_raw = load_data_from_github()
            st.success(f"✅ Loaded {len(df_raw):,} rows × {len(df_raw.columns)} columns from GitHub")
            
            # Clean and process data
            df_raw = clean_data(df_raw)
            df_raw = calculate_metrics(df_raw)
            
            # Store in session state
            st.session_state.df = df_raw
            st.success("✅ Data processed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# LOAD DATA FROM SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
df = st.session_state.df

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR FILTERS
# ═══════════════════════════════════════════════════════════════════════════════
st.sidebar.header("🔍 Filter Dashboard")

# Shipping Mode Filter
shipping_modes = ['All'] + sorted(df['Shipping Mode'].unique().tolist())
selected_shipping = st.sidebar.multiselect(
    "🚚 Shipping Mode",
    options=shipping_modes,
    default=['All']
)

# Region Filter
regions = ['All'] + sorted(df['Order Region'].unique().tolist())
selected_region = st.sidebar.multiselect(
    "🌍 Region",
    options=regions,
    default=['All']
)

# Market Filter
markets = ['All'] + sorted(df['Market'].unique().tolist())
selected_market = st.sidebar.multiselect(
    "🌎 Market",
    options=markets,
    default=['All']
)

# Customer Segment Filter
segments = ['All'] + sorted(df['Customer Segment'].unique().tolist())
selected_segment = st.sidebar.multiselect(
    "👥 Customer Segment",
    options=segments,
    default=['All']
)

# Delivery Status Filter
delivery_statuses = ['All'] + sorted(df['Delivery Status'].unique().tolist())
selected_delivery = st.sidebar.multiselect(
    "📦 Delivery Status",
    options=delivery_statuses,
    default=['All']
)

# Apply filters
filtered_df = df.copy()

if 'All' not in selected_shipping:
    filtered_df = filtered_df[filtered_df['Shipping Mode'].isin(selected_shipping)]

if 'All' not in selected_region:
    filtered_df = filtered_df[filtered_df['Order Region'].isin(selected_region)]

if 'All' not in selected_market:
    filtered_df = filtered_df[filtered_df['Market'].isin(selected_market)]

if 'All' not in selected_segment:
    filtered_df = filtered_df[filtered_df['Customer Segment'].isin(selected_segment)]

if 'All' not in selected_delivery:
    filtered_df = filtered_df[filtered_df['Delivery Status'].isin(selected_delivery)]

# Display filter summary
st.sidebar.markdown("---")
st.sidebar.metric("📊 Filtered Records", f"{len(filtered_df):,}")
st.sidebar.metric("📊 Total Records", f"{len(df):,}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview & KPIs",
    "💰 Financial Analysis",
    "🚚 Shipping Performance",
    "🔮 Predictive Insights",
    "🗺️ Geographic Distribution",
    "📋 Detailed Reports"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW & KPIs
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("📊 Key Performance Indicators")
    
    # Calculate KPIs
    total_orders = len(filtered_df)
    total_revenue = filtered_df['Sales'].sum()
    total_profit = filtered_df['Order Profit Per Order'].sum()
    avg_profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    ontime_rate = (filtered_df['On_Time'].mean() * 100)
    avg_delay = filtered_df['delay_gap'].mean()
    late_delivery_risk = filtered_df['Late_delivery_risk'].sum()
    
    # Display KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Total Orders", f"{total_orders:,}")
        st.metric("💵 Total Revenue", format_number(total_revenue))
    
    with col2:
        st.metric("💰 Total Profit", format_number(total_profit))
        st.metric("📈 Profit Margin", f"{avg_profit_margin:.2f}%")
    
    with col3:
        st.metric("✅ On-Time Rate", f"{ontime_rate:.2f}%")
        st.metric("⏱️ Avg Delay", f"{avg_delay:.2f} days")
    
    with col4:
        st.metric("⚠️ Late Risk Orders", f"{late_delivery_risk:,}")
        sla_met = (filtered_df['SLA_Status'] == 'SLA Met').sum()
        st.metric("🎯 SLA Met", f"{sla_met:,}")
    
    st.markdown("---")
    
    # Delivery Status Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Delivery Status Distribution")
        delivery_counts = filtered_df['Delivery Status'].value_counts()
        
        colors = {
            'Advance shipping': '#2ecc71',
            'Shipping on time': '#3498db',
            'Late delivery': '#e74c3c',
            'Shipping canceled': '#95a5a6'
        }
        
        fig_delivery = go.Figure(data=[go.Pie(
            labels=delivery_counts.index,
            values=delivery_counts.values,
            marker_colors=[colors.get(label, '#7f8c8d') for label in delivery_counts.index],
            hole=0.4
        )])
        fig_delivery.update_layout(
            title="Distribution by Delivery Status",
            height=400
        )
        st.plotly_chart(fig_delivery, use_container_width=True)
    
    with col2:
        st.subheader("🎯 SLA Performance")
        sla_counts = filtered_df['SLA_Status'].value_counts()
        
        sla_colors = {
            'SLA Met': '#2ecc71',
            'Minor Breach': '#f39c12',
            'Critical Breach': '#e67e22',
            'Severe Breach': '#e74c3c'
        }
        
        fig_sla = go.Figure(data=[go.Bar(
            x=sla_counts.index,
            y=sla_counts.values,
            marker_color=[sla_colors.get(label, '#7f8c8d') for label in sla_counts.index],
            text=sla_counts.values,
            textposition='auto'
        )])
        fig_sla.update_layout(
            title="SLA Status Distribution",
            xaxis_title="SLA Status",
            yaxis_title="Number of Orders",
            height=400
        )
        st.plotly_chart(fig_sla, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: FINANCIAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("💰 Financial Performance Analysis")
    
    # Revenue and Profit by Region
    st.subheader("🌍 Revenue & Profit by Region")
    
    region_finance = filtered_df.groupby('Order Region').agg({
        'Sales': 'sum',
        'Order Profit Per Order': 'sum'
    }).round(2)
    
    fig_region = go.Figure()
    fig_region.add_trace(go.Bar(
        name='Revenue',
        x=region_finance.index,
        y=region_finance['Sales'],
        marker_color='#3498db'
    ))
    fig_region.add_trace(go.Bar(
        name='Profit',
        x=region_finance.index,
        y=region_finance['Order Profit Per Order'],
        marker_color='#2ecc71'
    ))
    
    fig_region.update_layout(
        title="Revenue vs Profit by Region",
        xaxis_title="Region",
        yaxis_title="Amount ($)",
        barmode='group',
        height=400
    )
    st.plotly_chart(fig_region, use_container_width=True)
    
    st.markdown("---")
    
    # Market Performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌎 Revenue by Market")
        market_revenue = filtered_df.groupby('Market')['Sales'].sum().sort_values(ascending=False)
        
        fig_market = go.Figure(data=[go.Bar(
            x=market_revenue.values,
            y=market_revenue.index,
            orientation='h',
            marker_color='#3498db',
            text=[format_number(v) for v in market_revenue.values],
            textposition='auto'
        )])
        fig_market.update_layout(
            title="Total Revenue by Market",
            xaxis_title="Revenue ($)",
            yaxis_title="Market",
            height=400
        )
        st.plotly_chart(fig_market, use_container_width=True)
    
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
# TAB 5: GEOGRAPHIC DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.header("🗺️ Geographic Distribution & Analysis")
    
    st.markdown("""
    <div class="info-box">
        <strong>📍 Geographic Insights</strong><br>
        Visualize customer locations and delivery performance across regions with interactive maps.
    </div>
    """, unsafe_allow_html=True)
    
    # Map Controls
    st.subheader("🎛️ Map Display Controls")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_customer_locations = st.checkbox("👥 Customer Locations", value=True)
    with col2:
        show_order_locations = st.checkbox("📦 Order Locations", value=False)
    with col3:
        color_by_metric = st.selectbox(
            "🎨 Color By",
            ["Delivery Status", "SLA Status", "Delay Gap", "Sales", "Profit"]
        )
    with col4:
        map_style = st.selectbox(
            "🗺️ Map Style",
            ["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain"]
        )
    
    st.markdown("---")
    
    # Prepare map data
    map_df = filtered_df.copy()
    
    # Remove rows with missing lat/long
    if show_customer_locations:
        map_df = map_df.dropna(subset=['Latitude', 'Longitude'])
    
    if len(map_df) > 0:
        # Limit to 5000 points for performance
        if len(map_df) > 5000:
            st.warning(f"⚠️ Showing sample of 5000 points out of {len(map_df):,} total orders for performance.")
            map_df = map_df.sample(n=5000, random_state=42)
        
        # Create color mapping based on selected metric
        if color_by_metric == "Delivery Status":
            color_column = 'Delivery Status'
            color_map = {
                'Advance shipping': '#2ecc71',
                'Shipping on time': '#3498db',
                'Late delivery': '#e74c3c',
                'Shipping canceled': '#95a5a6'
            }
        elif color_by_metric == "SLA Status":
            color_column = 'SLA_Status'
            color_map = {
                'SLA Met': '#2ecc71',
                'Minor Breach': '#f39c12',
                'Critical Breach': '#e67e22',
                'Severe Breach': '#e74c3c'
            }
        elif color_by_metric == "Delay Gap":
            color_column = 'delay_gap'
            color_map = None  # Will use continuous color scale
        elif color_by_metric == "Sales":
            color_column = 'Sales'
            color_map = None
        else:  # Profit
            color_column = 'Order Profit Per Order'
            color_map = None
        
        # Create the map
        if color_map:
            # Categorical coloring
            fig_map = px.scatter_mapbox(
                map_df,
                lat='Latitude',
                lon='Longitude',
                color=color_column,
                color_discrete_map=color_map,
                hover_data={
                    'Latitude': ':.4f',
                    'Longitude': ':.4f',
                    'Customer City': True,
                    'Order Region': True,
                    'Shipping Mode': True,
                    'Sales': ':$,.2f',
                    'delay_gap': ':.1f',
                    'Delivery Status': True,
                    'SLA_Status': True
                },
                size_max=15,
                zoom=1,
                height=600,
                title=f"Customer Locations colored by {color_by_metric}"
            )
        else:
            # Continuous coloring
            fig_map = px.scatter_mapbox(
                map_df,
                lat='Latitude',
                lon='Longitude',
                color=color_column,
                color_continuous_scale='RdYlGn_r' if color_by_metric == 'Delay Gap' else 'Viridis',
                hover_data={
                    'Latitude': ':.4f',
                    'Longitude': ':.4f',
                    'Customer City': True,
                    'Order Region': True,
                    'Shipping Mode': True,
                    'Sales': ':$,.2f',
                    'delay_gap': ':.1f',
                    'Delivery Status': True,
                    'SLA_Status': True
                },
                size_max=15,
                zoom=1,
                height=600,
                title=f"Customer Locations colored by {color_by_metric}"
            )
        
        fig_map.update_layout(
            mapbox_style=map_style,
            margin={"r": 0, "t": 50, "l": 0, "b": 0}
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
        
        st.markdown("---")
        
        # Geographic Statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Top 10 Cities by Order Volume")
            city_stats = map_df.groupby('Customer City').agg({
                'Sales': 'count',
                'Order Profit Per Order': 'sum',
                'On_Time': 'mean'
            }).round(2)
            city_stats.columns = ['Orders', 'Total_Profit', 'OnTime_Rate']
            city_stats['OnTime_Rate'] = (city_stats['OnTime_Rate'] * 100).round(1)
            city_stats = city_stats.sort_values('Orders', ascending=False).head(10)
            
            st.dataframe(city_stats, use_container_width=True)
        
        with col2:
            st.subheader("📊 Geographic Distribution by Metric")
            metric_option = st.selectbox(
                "Select Metric",
                ["Order Count", "Total Sales", "Total Profit", "On-Time Rate"]
            )
            
            if metric_option == "Order Count":
                geo_data = map_df.groupby('Order Region').size()
            elif metric_option == "Total Sales":
                geo_data = map_df.groupby('Order Region')['Sales'].sum()
            elif metric_option == "Total Profit":
                geo_data = map_df.groupby('Order Region')['Order Profit Per Order'].sum()
            else:  # On-Time Rate
                geo_data = (map_df.groupby('Order Region')['On_Time'].mean() * 100).round(2)
            
            geo_data = geo_data.sort_values(ascending=False)
            
            fig_geo_bar = go.Figure(data=[go.Bar(
                x=geo_data.index,
                y=geo_data.values,
                marker_color='#3498db',
                text=geo_data.values,
                textposition='auto'
            )])
            fig_geo_bar.update_layout(
                title=f"{metric_option} by Region",
                xaxis_title="Region",
                yaxis_title=metric_option,
                height=350
            )
            st.plotly_chart(fig_geo_bar, use_container_width=True)
        
        st.markdown("---")
        
        # Heat map of countries
        st.subheader("🌐 Country-Level Performance")
        
        country_perf = map_df.groupby('Customer Country').agg({
            'Sales': ['count', 'sum'],
            'Order Profit Per Order': 'sum',
            'On_Time': 'mean',
            'delay_gap': 'mean'
        }).round(2)
        
        country_perf.columns = ['Orders', 'Revenue', 'Profit', 'OnTime_Rate', 'Avg_Delay']
        country_perf['OnTime_Rate'] = (country_perf['OnTime_Rate'] * 100).round(1)
        country_perf = country_perf.sort_values('Orders', ascending=False).head(15)
        
        st.dataframe(country_perf, use_container_width=True)
    
    else:
        st.warning("⚠️ No data available with valid latitude/longitude coordinates for the selected filters.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6: DETAILED REPORTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
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
