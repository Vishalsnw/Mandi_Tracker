import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from scraper import scrape_apmc_data, generate_price_trends, get_nearby_mandis
from data_config import INDIAN_STATES_DISTRICTS, COMMODITY_IMAGES, TRANSLATIONS

st.set_page_config(
    page_title="Mandi Bhav",
    page_icon="🌾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'selected_state' not in st.session_state:
    st.session_state.selected_state = 'Punjab'
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = 'Ludhiana'
if 'price_data' not in st.session_state:
    st.session_state.price_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'category_filter' not in st.session_state:
    st.session_state.category_filter = 'all'

def get_text(key):
    return TRANSLATIONS[st.session_state.language][key]

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    * {
        font-family: 'Roboto', sans-serif;
    }
    
    .stApp {
        background: #121212;
        color: #E0E0E0;
        max-width: 480px;
        margin: 0 auto;
    }
    
    .main {
        background: #121212;
        padding: 0;
        padding-bottom: 80px;
    }
    
    [data-testid="stHeader"] {
        background: #1E1E1E;
        border-bottom: 1px solid #2C2C2C;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
        font-weight: 500;
    }
    
    .app-header {
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
        padding: 16px;
        border-radius: 0 0 16px 16px;
        margin: -16px -16px 16px -16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .app-title {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: 500;
        margin: 0;
        text-align: center;
    }
    
    .app-subtitle {
        color: #B2DFDB;
        font-size: 12px;
        text-align: center;
        margin-top: 4px;
    }
    
    .metric-card {
        background: #1E1E1E;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        color: #B0B0B0;
        font-size: 12px;
        margin-bottom: 4px;
    }
    
    .metric-value {
        color: #FFFFFF;
        font-size: 24px;
        font-weight: 500;
    }
    
    .commodity-card {
        background: #1E1E1E;
        padding: 14px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 3px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .commodity-name {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    .price-row {
        display: flex;
        justify-content: space-between;
        margin: 4px 0;
    }
    
    .price-label {
        color: #B0B0B0;
        font-size: 12px;
    }
    
    .price-value {
        color: #4CAF50;
        font-size: 14px;
        font-weight: 500;
    }
    
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 480px;
        background: #1E1E1E;
        border-top: 1px solid #2C2C2C;
        display: flex;
        justify-content: space-around;
        padding: 8px 0;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.3);
        z-index: 999;
    }
    
    .nav-item {
        flex: 1;
        text-align: center;
        padding: 8px;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .nav-item.active {
        background: rgba(76, 175, 80, 0.1);
    }
    
    .nav-icon {
        font-size: 24px;
        display: block;
        margin-bottom: 2px;
    }
    
    .nav-label {
        font-size: 11px;
        color: #B0B0B0;
    }
    
    .nav-item.active .nav-label {
        color: #4CAF50;
    }
    
    .stButton>button {
        background: #4CAF50;
        color: white;
        font-weight: 500;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        width: 100%;
        box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
    }
    
    .stButton>button:hover {
        background: #45A049;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
    }
    
    .stSelectbox>div>div {
        background: #1E1E1E;
        color: #E0E0E0;
        border: 1px solid #2C2C2C;
        border-radius: 8px;
    }
    
    .stRadio>div {
        background: transparent;
    }
    
    .stRadio label {
        color: #E0E0E0;
    }
    
    div[data-baseweb="select"] > div {
        background-color: #1E1E1E;
        border-color: #2C2C2C;
    }
    
    input {
        background-color: #1E1E1E;
        color: #E0E0E0;
        border: 1px solid #2C2C2C;
    }
    
    .search-section {
        background: #1E1E1E;
        padding: 16px;
        border-radius: 12px;
        margin: 16px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .section-title {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 16px;
    }
    
    .chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0;
    }
    
    .chip {
        background: #2C2C2C;
        color: #E0E0E0;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        cursor: pointer;
        border: 1px solid #3C3C3C;
    }
    
    .chip.active {
        background: #4CAF50;
        color: white;
        border-color: #4CAF50;
    }
    
    [data-testid="stDataFrame"] {
        background: #1E1E1E;
    }
    
    .stPlotlyChart {
        background: #1E1E1E;
        border-radius: 12px;
        padding: 8px;
    }
    
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="app-header">
        <div class="app-title">🌾 Mandi Bhav</div>
        <div class="app-subtitle">{get_text('tagline')}</div>
    </div>
""", unsafe_allow_html=True)

def show_home_page():
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox(
            "🌐 Lang",
            options=['en', 'hi'],
            format_func=lambda x: 'English' if x == 'en' else 'हिंदी',
            index=0 if st.session_state.language == 'en' else 1,
            key='lang_select'
        )
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()
    
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">📍 {get_text("select_state")} & {get_text("select_district")}</div>', unsafe_allow_html=True)
    
    state_options = list(INDIAN_STATES_DISTRICTS.keys())
    selected_state = st.selectbox(
        get_text('select_state'),
        options=state_options,
        index=state_options.index(st.session_state.selected_state) if st.session_state.selected_state in state_options else 0,
        label_visibility='collapsed'
    )
    
    district_options = INDIAN_STATES_DISTRICTS[selected_state]['districts']
    if isinstance(district_options[0], dict):
        district_keys = [d['en'] for d in district_options]
        selected_district = st.selectbox(
            get_text('select_district'),
            options=district_keys,
            label_visibility='collapsed'
        )
    else:
        selected_district = st.selectbox(
            get_text('select_district'),
            options=district_options,
            label_visibility='collapsed'
        )
    
    st.session_state.selected_state = selected_state
    st.session_state.selected_district = selected_district
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-title">🏷️ {get_text("filter_category")}</div>', unsafe_allow_html=True)
    
    categories = ['all', 'vegetables', 'fruits', 'grains', 'pulses']
    category_icons = {'all': '🌟', 'vegetables': '🥬', 'fruits': '🍎', 'grains': '🌾', 'pulses': '🫘'}
    
    cols = st.columns(5)
    for idx, cat in enumerate(categories):
        with cols[idx]:
            label = get_text('all_categories') if cat == 'all' else get_text(cat)
            if st.button(f"{category_icons[cat]}\n{label[:3]}", key=f"cat_{cat}", use_container_width=True):
                st.session_state.category_filter = cat
    
    if st.button(f"🔍 {get_text('search_prices')}", use_container_width=True, type="primary"):
        with st.spinner(get_text('fetching_prices')):
            st.session_state.price_data = scrape_apmc_data(selected_state, selected_district)
        st.rerun()
    
    if st.session_state.price_data is not None and not st.session_state.price_data.empty:
        df = st.session_state.price_data
        
        if st.session_state.category_filter != 'all':
            df = df[df['category'] == st.session_state.category_filter]
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{get_text('total_commodities')}</div>
                <div class="metric-value">{len(df)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_price = df['modal_price'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Price</div>
                <div class="metric-value">₹{avg_price:.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            price_range = f"₹{df['min_price'].min():.0f}-{df['max_price'].max():.0f}"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Range</div>
                <div class="metric-value" style="font-size: 16px;">{price_range}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="section-title">📊 {get_text("commodity")} Prices</div>', unsafe_allow_html=True)
        
        for _, row in df.head(20).iterrows():
            commodity_name = row['commodity_hi'] if st.session_state.language == 'hi' else row['commodity_en']
            st.markdown(f"""
            <div class="commodity-card">
                <div class="commodity-name">{commodity_name}</div>
                <div class="price-row">
                    <span class="price-label">Min</span>
                    <span class="price-value">₹{row['min_price']:.2f}</span>
                </div>
                <div class="price-row">
                    <span class="price-label">Max</span>
                    <span class="price-value">₹{row['max_price']:.2f}</span>
                </div>
                <div class="price-row">
                    <span class="price-label">Modal</span>
                    <span class="price-value" style="font-size: 16px;">₹{row['modal_price']:.2f}</span>
                </div>
                <div class="price-row">
                    <span class="price-label">Market</span>
                    <span class="price-label">{row['market']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"👆 {get_text('select_state')} and {get_text('select_district')} to see prices")

def show_trends_page():
    st.markdown(f'<div class="section-title">📈 {get_text("price_trends")}</div>', unsafe_allow_html=True)
    
    if st.session_state.price_data is not None and not st.session_state.price_data.empty:
        df = st.session_state.price_data
        
        commodity_options = df['commodity_en'].unique().tolist()
        selected_commodity = st.selectbox(
            get_text('commodity'),
            options=commodity_options
        )
        
        if selected_commodity:
            trend_data = generate_price_trends(selected_commodity, days=7)
            
            if not trend_data.empty and trend_data['price'].sum() > 0:
                fig = px.area(
                    trend_data,
                    x='date',
                    y='price',
                    title=f"{get_text('last_7_days')} - {selected_commodity}",
                )
                
                fig.update_traces(
                    fillcolor='rgba(76, 175, 80, 0.2)',
                    line_color='#4CAF50',
                    line_width=3
                )
                
                fig.update_layout(
                    plot_bgcolor='#121212',
                    paper_bgcolor='#1E1E1E',
                    font=dict(color='#E0E0E0'),
                    xaxis=dict(gridcolor='#2C2C2C', title=''),
                    yaxis=dict(gridcolor='#2C2C2C', title='Price (₹)'),
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No trend data available for this commodity")
    else:
        st.info("Please search for prices first from the Home page")

def show_markets_page():
    st.markdown(f'<div class="section-title">🏪 {get_text("nearby_mandis")}</div>', unsafe_allow_html=True)
    
    if st.session_state.selected_state and st.session_state.selected_district:
        nearby_mandis = get_nearby_mandis(st.session_state.selected_state, st.session_state.selected_district)
        
        if not nearby_mandis.empty:
            for _, row in nearby_mandis.iterrows():
                st.markdown(f"""
                <div class="commodity-card">
                    <div class="commodity-name">📍 {row['name']}</div>
                    <div class="price-row">
                        <span class="price-label">Distance</span>
                        <span class="price-value">{row['distance_km']} km</span>
                    </div>
                    <div class="price-row">
                        <span class="price-label">Facilities</span>
                        <span class="price-label">{row['facilities']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No market data available")
    else:
        st.info("Please select a state and district from the Home page")

def show_about_page():
    st.markdown(f'<div class="section-title">ℹ️ About Mandi Bhav</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="commodity-card">
        <div class="commodity-name">Real-time Market Prices</div>
        <p style="color: #B0B0B0; font-size: 14px; line-height: 1.6;">
        Get live agricultural commodity prices from APMC mandis across India. 
        Data is fetched directly from the official data.gov.in API.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="commodity-card">
        <div class="commodity-name">Features</div>
        <p style="color: #B0B0B0; font-size: 14px; line-height: 1.6;">
        ✅ Live prices from government sources<br>
        ✅ State & district-wise data<br>
        ✅ Category filtering<br>
        ✅ Price trends<br>
        ✅ Nearby market information<br>
        ✅ Bilingual support (English/Hindi)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="commodity-card">
        <div class="commodity-name">Data Source</div>
        <p style="color: #B0B0B0; font-size: 14px; line-height: 1.6;">
        All price data is sourced from the official data.gov.in agricultural market API, 
        managed by the Ministry of Agriculture and Farmers Welfare, Government of India.
        </p>
    </div>
    """, unsafe_allow_html=True)

pages = {
    'home': ('🏠', 'Home', show_home_page),
    'trends': ('📈', 'Trends', show_trends_page),
    'markets': ('🏪', 'Markets', show_markets_page),
    'about': ('ℹ️', 'About', show_about_page)
}

query_params = st.query_params
if 'page' in query_params:
    new_page = query_params['page']
    if new_page in pages and new_page != st.session_state.current_page:
        st.session_state.current_page = new_page
        st.query_params.clear()
        st.rerun()

current = st.session_state.current_page
pages[current][2]()

nav_items = []
for page_key, (icon, label, _) in pages.items():
    active_class = 'active' if page_key == current else ''
    nav_items.append(f'<div class="nav-item {active_class}" onclick="window.location.href=\'?page={page_key}\'"><span class="nav-icon">{icon}</span><span class="nav-label">{label}</span></div>')

nav_html = f'<div class="bottom-nav">{"".join(nav_items)}</div>'

st.markdown(nav_html, unsafe_allow_html=True)
