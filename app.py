import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from scraper import scrape_apmc_data, generate_price_trends, get_nearby_mandis
from data_config import INDIAN_STATES_DISTRICTS, COMMODITY_IMAGES, TRANSLATIONS

st.set_page_config(
    page_title="Mandli Bhav",
    page_icon="🌾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'selected_state' not in st.session_state:
    st.session_state.selected_state = 'Gujarat'
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = 'Ahmedabad'
if 'price_data' not in st.session_state:
    st.session_state.price_data = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'home'

def get_text(key):
    return TRANSLATIONS[st.session_state.language][key]

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    * {
        font-family: 'Roboto', sans-serif;
    }
    
    .stApp {
        background-color: #121212;
        max-width: 480px;
        margin: 0 auto;
    }
    
    .main {
        background-color: #121212;
        padding: 0;
        padding-bottom: 80px;
    }
    
    .block-container {
        padding: 1rem;
        max-width: 480px;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 500;
    }
    
    h1 {
        font-size: 24px !important;
        margin-bottom: 8px !important;
    }
    
    h2 {
        font-size: 20px !important;
    }
    
    h3 {
        font-size: 18px !important;
    }
    
    p, div, span, label {
        color: #E0E0E0 !important;
    }
    
    .metric-card {
        background: #1E1E1E;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        margin: 8px 0;
        border: 1px solid #2C2C2C;
    }
    
    .metric-card h4 {
        color: #B0B0B0 !important;
        font-size: 12px !important;
        font-weight: 400;
        margin-bottom: 4px;
    }
    
    .metric-card h2 {
        color: #4CAF50 !important;
        font-size: 28px !important;
        font-weight: 500;
        margin: 0;
    }
    
    .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: 500;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        width: 100%;
        font-size: 14px;
    }
    
    .stButton>button:hover {
        background-color: #45a049 !important;
    }
    
    [data-testid="stSelectbox"] {
        background-color: #1E1E1E;
        border-radius: 8px;
    }
    
    [data-testid="stSelectbox"] label {
        color: #B0B0B0 !important;
        font-size: 12px !important;
    }
    
    input, select, textarea {
        background-color: #2C2C2C !important;
        color: #E0E0E0 !important;
        border: 1px solid #3C3C3C !important;
        border-radius: 8px !important;
    }
    
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        max-width: 480px;
        width: 100%;
        background: #1E1E1E;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.5);
        border-top: 1px solid #2C2C2C;
        z-index: 999;
        padding: 8px 0;
    }
    
    .nav-button {
        background: transparent !important;
        color: #B0B0B0 !important;
        border: none !important;
        padding: 8px !important;
        font-size: 11px !important;
        text-align: center !important;
        width: 100% !important;
    }
    
    .nav-button:hover {
        background: #2C2C2C !important;
    }
    
    .nav-button-active {
        color: #4CAF50 !important;
    }
    
    .nav-icon {
        font-size: 24px;
        display: block;
        margin-bottom: 4px;
    }
    
    [data-testid="stDataFrame"] {
        background-color: #1E1E1E;
    }
    
    .stRadio > label {
        color: #B0B0B0 !important;
    }
    
    .stRadio [data-baseweb="radio"] {
        background-color: #2C2C2C;
    }
    
    div[data-baseweb="select"] > div {
        background-color: #2C2C2C !important;
        color: #E0E0E0 !important;
    }
    
    [data-testid="stMarkdownContainer"] p {
        color: #E0E0E0 !important;
    }
    
    hr {
        border-color: #2C2C2C !important;
    }
    </style>
""", unsafe_allow_html=True)

def render_home():
    st.markdown("# 🌾 Mandli Bhav")
    st.markdown("### Real-time Mandi Prices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        state_options = list(INDIAN_STATES_DISTRICTS.keys())
        selected_state = st.selectbox(
            "State",
            options=state_options,
            index=state_options.index(st.session_state.selected_state) if st.session_state.selected_state in state_options else 0
        )
        st.session_state.selected_state = selected_state
    
    with col2:
        district_options = INDIAN_STATES_DISTRICTS[selected_state]['districts']
        if isinstance(district_options[0], dict):
            district_keys = [d['en'] for d in district_options]
            selected_district = st.selectbox(
                "District",
                options=district_keys
            )
        else:
            selected_district = st.selectbox(
                "District",
                options=district_options
            )
        st.session_state.selected_district = selected_district
    
    if st.button("🔍 Search Prices"):
        with st.spinner("Fetching prices..."):
            st.session_state.price_data = scrape_apmc_data(selected_state, selected_district)
        st.rerun()
    
    if st.session_state.price_data is not None and not st.session_state.price_data.empty:
        df = st.session_state.price_data
        
        category_filter = st.radio(
            "Category",
            options=['all', 'vegetables', 'fruits', 'grains', 'pulses'],
            format_func=lambda x: get_text('all_categories') if x == 'all' else get_text(x),
            horizontal=True
        )
        
        if category_filter != 'all':
            df = df[df['category'] == category_filter]
        
        if len(df) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Items</h4>
                    <h2>{len(df)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_price = df['modal_price'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Avg Price</h4>
                    <h2>₹{avg_price:.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                price_range = f"₹{df['min_price'].min():.0f}-{df['max_price'].max():.0f}"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Range</h4>
                    <h2 style="font-size: 18px !important;">{price_range}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 📊 Top Commodities")
            
            top_commodities = df.nlargest(min(8, len(df)), 'modal_price')
            
            for _, row in top_commodities.iterrows():
                commodity_name = row['commodity_hi'] if st.session_state.language == 'hi' else row['commodity_en']
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4>{commodity_name}</h4>
                            <p style="font-size: 12px; margin: 0;">₹{row['min_price']:.0f} - ₹{row['max_price']:.0f}</p>
                        </div>
                        <h2 style="margin: 0;">₹{row['modal_price']:.0f}</h2>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No commodities found for this category.")
    else:
        st.info("👆 Select a location and search to view prices")
        
        st.image("attached_assets/stock_images/agricultural_market__f7641e9d.jpg", use_container_width=True)
        
        st.markdown("""
        ### About Mandli Bhav
        
        Get real-time commodity prices from APMC mandis across India.
        
        **Features:**
        - 🇮🇳 All Indian states & districts
        - 🌾 Vegetables, fruits, grains & pulses
        - 📊 Price trends & analysis
        - 🏪 Nearby mandi information
        """)

def render_trends():
    st.markdown("# 📈 Price Trends")
    
    if st.session_state.price_data is not None and not st.session_state.price_data.empty:
        df = st.session_state.price_data
        
        commodity_options = df['commodity_en'].unique().tolist()
        selected_commodity = st.selectbox(
            "Select Commodity",
            options=commodity_options
        )
        
        if selected_commodity:
            trend_data = generate_price_trends(selected_commodity, days=7)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_data['date'],
                y=trend_data['price'],
                mode='lines+markers',
                line=dict(color='#4CAF50', width=3),
                marker=dict(size=8, color='#FF9800'),
                fill='tonexty',
                fillcolor='rgba(76, 175, 80, 0.1)'
            ))
            
            fig.update_layout(
                title=f"Last 7 Days - {selected_commodity}",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                plot_bgcolor='#1E1E1E',
                paper_bgcolor='#1E1E1E',
                font=dict(color='#E0E0E0'),
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            commodity_image = COMMODITY_IMAGES.get(selected_commodity)
            if commodity_image:
                st.image(commodity_image, use_container_width=True)
    else:
        st.info("Search for prices first to view trends")

def render_markets():
    st.markdown("# 🏪 Nearby Mandis")
    
    if st.session_state.selected_state and st.session_state.selected_district:
        nearby_mandis = get_nearby_mandis(st.session_state.selected_state, st.session_state.selected_district)
        
        for _, mandi in nearby_mandis.iterrows():
            st.markdown(f"""
            <div class="metric-card">
                <h3>{mandi['name']}</h3>
                <p style="font-size: 14px; margin: 4px 0;">📍 {mandi['distance_km']} km away</p>
                <p style="font-size: 12px; margin: 0; color: #4CAF50 !important;">{mandi['facilities']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Select a location from Home tab first")

def render_about():
    st.markdown("# ℹ️ About")
    
    st.markdown("""
    ## Mandli Bhav
    
    **Your trusted agricultural market price tracker**
    
    ### Features
    
    🇮🇳 **Pan-India Coverage**  
    Access prices from all Indian states and districts
    
    🌾 **Wide Range**  
    Vegetables, fruits, grains, and pulses
    
    📊 **Price Trends**  
    7-day historical price analysis
    
    🏪 **Mandi Finder**  
    Locate nearby agricultural markets
    
    🌐 **Bilingual**  
    Available in English and Hindi
    
    ---
    
    ### Data Source
    
    Price data is sourced from official APMC portals across India.
    
    ### For Farmers
    
    Make informed decisions about when and where to sell your produce for the best prices.
    
    ---
    
    **Made for Indian Farmers | 2024**
    """)
    
    lang_col1, lang_col2 = st.columns(2)
    with lang_col1:
        if st.button("🇬🇧 English"):
            st.session_state.language = 'en'
            st.rerun()
    with lang_col2:
        if st.button("🇮🇳 हिंदी"):
            st.session_state.language = 'hi'
            st.rerun()

tabs = {
    'home': {'icon': '🏠', 'label': 'Home', 'render': render_home},
    'trends': {'icon': '📈', 'label': 'Trends', 'render': render_trends},
    'markets': {'icon': '🏪', 'label': 'Markets', 'render': render_markets},
    'about': {'icon': 'ℹ️', 'label': 'About', 'render': render_about}
}

tabs[st.session_state.current_tab]['render']()

st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

st.markdown('<div class="bottom-nav">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(f"{tabs['home']['icon']}\n{tabs['home']['label']}", key="nav_home", use_container_width=True, type="primary" if st.session_state.current_tab == 'home' else "secondary"):
        st.session_state.current_tab = 'home'
        st.rerun()

with col2:
    if st.button(f"{tabs['trends']['icon']}\n{tabs['trends']['label']}", key="nav_trends", use_container_width=True, type="primary" if st.session_state.current_tab == 'trends' else "secondary"):
        st.session_state.current_tab = 'trends'
        st.rerun()

with col3:
    if st.button(f"{tabs['markets']['icon']}\n{tabs['markets']['label']}", key="nav_markets", use_container_width=True, type="primary" if st.session_state.current_tab == 'markets' else "secondary"):
        st.session_state.current_tab = 'markets'
        st.rerun()

with col4:
    if st.button(f"{tabs['about']['icon']}\n{tabs['about']['label']}", key="nav_about", use_container_width=True, type="primary" if st.session_state.current_tab == 'about' else "secondary"):
        st.session_state.current_tab = 'about'
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
