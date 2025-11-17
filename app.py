import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from scraper import scrape_apmc_data
from data_config import INDIAN_STATES_DISTRICTS, COMMODITY_IMAGES, TRANSLATIONS

st.set_page_config(
    page_title="Mandi Bhav",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#4CAF50">
""", unsafe_allow_html=True)

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
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'show_commodity_selector' not in st.session_state:
    st.session_state.show_commodity_selector = False

def get_text(key):
    return TRANSLATIONS[st.session_state.language][key]

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    * {
        font-family: 'Roboto', sans-serif;
    }
    
    /* Hide Streamlit UI elements for native app look */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    .stActionButton {display: none;}
    
    /* Mobile-first layout */
    .stApp {
        background-color: #F5F5F5;
        max-width: 100vw;
        margin: 0;
        padding: 0;
    }
    
    .main {
        background-color: #F5F5F5;
        padding: 0 !important;
        padding-bottom: 80px !important;
        max-width: 100vw;
        margin: 0;
        min-height: 100vh;
    }
    
    .block-container {
        padding: 12px 16px !important;
        max-width: 100vw !important;
        margin: 0 !important;
    }
    
    /* For larger screens, center with max-width */
    @media (min-width: 768px) {
        .stApp {
            max-width: 480px;
            margin: 0 auto;
        }
        .main {
            max-width: 480px;
        }
        .block-container {
            max-width: 480px !important;
        }
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #2E7D32 !important;
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
        color: #424242 !important;
    }
    
    .metric-card {
        background: #FFFFFF;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08);
        margin: 8px 0;
        border: none;
        transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.16), 0 2px 4px rgba(0,0,0,0.12);
    }
    
    .metric-card h4 {
        color: #757575 !important;
        font-size: 12px !important;
        font-weight: 400;
        margin-bottom: 4px;
    }
    
    .metric-card h2 {
        color: #2E7D32 !important;
        font-size: 28px !important;
        font-weight: 500;
        margin: 0;
    }
    
    .green-header {
        background: linear-gradient(135deg, #4CAF50 0%, #388E3C 50%, #2E7D32 100%);
        color: white;
        padding: 20px 16px;
        border-radius: 16px;
        margin-bottom: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3), 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .green-header h1 {
        color: white !important;
        margin: 0;
    }
    
    .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: 500;
        border-radius: 28px;
        border: none;
        padding: 14px 32px;
        width: 100%;
        font-size: 16px;
        letter-spacing: 0.5px;
        text-transform: none;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.25), 0 1px 3px rgba(0,0,0,0.12);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stButton>button:hover {
        background-color: #43A047 !important;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.35), 0 2px 6px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 0 2px 6px rgba(76, 175, 80, 0.3);
    }
    
    [data-testid="stSelectbox"] {
        background-color: #FFFFFF;
        border-radius: 8px;
    }
    
    [data-testid="stSelectbox"] label {
        color: #424242 !important;
        font-size: 14px !important;
        font-weight: 500;
    }
    
    input, select, textarea {
        background-color: #F5F5F5 !important;
        color: #424242 !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }
    
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        width: 100vw;
        background: #FFFFFF;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.15);
        border-top: 1px solid #E0E0E0;
        z-index: 9999;
        padding: 8px 0 safe-area-inset-bottom;
        padding-bottom: max(8px, env(safe-area-inset-bottom));
    }
    
    @media (min-width: 768px) {
        .bottom-nav {
            left: 50%;
            transform: translateX(-50%);
            max-width: 480px;
            width: 480px;
        }
    }
    
    /* Bottom navigation buttons - Android Material Design style */
    .bottom-nav .stButton > button {
        background: transparent !important;
        color: #757575 !important;
        border: none !important;
        padding: 6px 12px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        text-align: center !important;
        width: 100% !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
        min-height: 56px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 2px !important;
        letter-spacing: 0.4px !important;
    }
    
    .bottom-nav .stButton > button:hover {
        background: rgba(76, 175, 80, 0.08) !important;
        color: #4CAF50 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    
    .bottom-nav .stButton > button:active {
        background: rgba(76, 175, 80, 0.15) !important;
        transform: none !important;
    }
    
    /* Active tab styling */
    .bottom-nav .stButton > button[kind="primary"] {
        color: #4CAF50 !important;
        background: transparent !important;
    }
    
    .bottom-nav .stButton > button[kind="primary"]:hover {
        background: rgba(76, 175, 80, 0.08) !important;
    }
    
    .nav-icon {
        font-size: 24px;
        display: block;
        margin-bottom: 4px;
    }
    
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
    }
    
    .stRadio > label {
        color: #424242 !important;
        font-weight: 500;
    }
    
    .stRadio [data-baseweb="radio"] {
        background-color: #F5F5F5;
    }
    
    div[data-baseweb="select"] > div {
        background-color: #F5F5F5 !important;
        color: #424242 !important;
    }
    
    [data-testid="stMarkdownContainer"] p {
        color: #424242 !important;
    }
    
    hr {
        border-color: #E0E0E0 !important;
    }
    
    .commodity-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin: 16px 0;
    }
    
    .commodity-item {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 14px 12px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05);
        cursor: pointer;
        border: 2px solid transparent;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .commodity-item:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 14px rgba(76, 175, 80, 0.25), 0 2px 6px rgba(0,0,0,0.1);
    }
    
    .commodity-item img {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 8px;
    }
    
    .commodity-name {
        font-size: 12px;
        color: #424242;
        font-weight: 500;
    }
    
    .freshness-badge {
        background: linear-gradient(135deg, #4CAF50, #66BB6A);
        color: white;
        padding: 5px 14px;
        border-radius: 16px;
        font-size: 11px;
        font-weight: 500;
        display: inline-block;
        margin-left: 8px;
        box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
        letter-spacing: 0.3px;
    }
    
    .price-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 14px 16px;
        margin: 10px 0;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid #F5F5F5;
    }
    
    .price-card:hover {
        box-shadow: 0 4px 10px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.08);
        border-color: #E8F5E9;
    }
    
    .price-card img {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
    }
    
    .price-info {
        flex: 1;
    }
    
    .price-info h3 {
        margin: 0;
        font-size: 16px;
        color: #2E7D32 !important;
    }
    
    .price-info p {
        margin: 0;
        font-size: 12px;
        color: #757575 !important;
    }
    
    .price-value {
        font-size: 18px;
        font-weight: 600;
        color: #2E7D32 !important;
    }
    </style>
""", unsafe_allow_html=True)

def render_home():
    st.markdown("""
    <div class="green-header">
        <h1>🌾 Mandi Bhav</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">आपकी मंडी के सभी भाव</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        with st.spinner("Fetching prices from data.gov.in API..."):
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
            
            for idx, row in top_commodities.iterrows():
                commodity_en = row['commodity_en']
                commodity_hi = row['commodity_hi']
                commodity_img = COMMODITY_IMAGES.get(commodity_en, 'attached_assets/stock_images/agricultural_market__f7641e9d.jpg')
                
                col_a, col_b = st.columns([4, 1])
                
                with col_a:
                    st.markdown(f"""
                    <div class="price-card">
                        <img src="{commodity_img}" alt="{commodity_en}">
                        <div class="price-info">
                            <h3>{commodity_en}</h3>
                            <p>{commodity_hi}</p>
                            <p style="color: #757575 !important;">₹{row['min_price']:.0f} - ₹{row['max_price']:.0f} / Quintal</p>
                        </div>
                        <div>
                            <div class="price-value">₹{row['modal_price']:.0f}</div>
                            <span class="freshness-badge">● Today</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_b:
                    fav_key = f"{commodity_en}_{idx}"
                    is_favorite = any(f['name'] == commodity_en for f in st.session_state.favorites)
                    
                    if st.button("⭐" if is_favorite else "☆", key=fav_key, width="stretch"):
                        if is_favorite:
                            st.session_state.favorites = [f for f in st.session_state.favorites if f['name'] != commodity_en]
                            st.toast(f"Removed {commodity_en} from favorites")
                        else:
                            st.session_state.favorites.append({
                                'name': commodity_en,
                                'name_hi': commodity_hi,
                                'price': row['modal_price'],
                                'location': st.session_state.selected_district,
                                'image': commodity_img
                            })
                            st.toast(f"Added {commodity_en} to favorites!")
                        st.rerun()
        else:
            st.warning("No commodities found for this category.")
    elif st.session_state.price_data is not None and st.session_state.price_data.empty:
        st.warning(f"⚠️ No price data found for {selected_state} - {selected_district}")
        st.info("💡 **Tip:** The API updates daily with data from various mandis. Try selecting different states like 'Andhra Pradesh' or 'Haryana' which have recent data, or search without selecting to see all available prices.")
        
        if st.button("📋 Show All Available Prices"):
            with st.spinner("Fetching all available prices..."):
                st.session_state.price_data = scrape_apmc_data(None, None)
            st.rerun()
    else:
        st.info("👆 Select a location and click 'Search Prices' to view real mandi data from data.gov.in")
        
        st.image("attached_assets/stock_images/agricultural_market__f7641e9d.jpg", width="stretch")
        
        st.markdown("""
        ### About Mandi Bhav
        
        Get real agricultural commodity prices from APMC mandis via data.gov.in API.
        
        **Features:**
        - 📡 Real data from government data portal
        - 🌾 Latest commodity prices  
        - 📊 Multiple states & districts
        - 💯 100% authentic market data
        """)

def render_trends():
    st.markdown("""
    <div class="green-header">
        <h1>📊 Dashboard</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">All Favorite Mandi at One Place</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⭐ Your Favorites")
    
    if len(st.session_state.favorites) == 0:
        st.info("No favorites yet! Add commodities from the home tab by clicking the star button.")
    else:
        for fav in st.session_state.favorites:
            st.markdown(f"""
            <div class="price-card">
                <img src="{fav.get('image', 'attached_assets/stock_images/agricultural_market__f7641e9d.jpg')}" alt="{fav['name']}">
                <div class="price-info">
                    <h3>{fav['name']}</h3>
                    <p>{fav.get('name_hi', '')}</p>
                    <p style="color: #757575 !important;">{fav.get('location', '')} ● ₹{fav['price']:.0f}</p>
                </div>
                <div class="price-value">₹{fav['price']:.0f}</div>
            </div>
            """, unsafe_allow_html=True)
    

def render_markets():
    st.markdown("""
    <div class="green-header">
        <h1>🔍 Search Mandi</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">मंडी खोजने</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Search for mandi prices by selecting state and district from the Home tab.")

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

def render_commodity_selector():
    st.markdown("""
    <div class="green-header">
        <h1>🔍 Search Prices</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">मंडी के भाव खोजें</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Use the Home tab to select your state and district, then search for real market prices from the data.gov.in API.")

tabs = {
    'home': {'icon': '🏠', 'label': 'Home', 'render': render_home},
    'commodities': {'icon': '🔍', 'label': 'Search', 'render': render_commodity_selector},
    'dashboard': {'icon': '📊', 'label': 'Dashboard', 'render': render_trends},
    'about': {'icon': 'ℹ️', 'label': 'About', 'render': render_about}
}

tabs[st.session_state.current_tab]['render']()

st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="bottom-nav">
<style>
.bottom-nav {
    display: block !important;
    visibility: visible !important;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(f"{tabs['home']['icon']}\n{tabs['home']['label']}", key="nav_home", width="stretch", type="primary" if st.session_state.current_tab == 'home' else "secondary"):
        st.session_state.current_tab = 'home'
        st.rerun()

with col2:
    if st.button(f"{tabs['commodities']['icon']}\n{tabs['commodities']['label']}", key="nav_commodities", width="stretch", type="primary" if st.session_state.current_tab == 'commodities' else "secondary"):
        st.session_state.current_tab = 'commodities'
        st.rerun()

with col3:
    if st.button(f"{tabs['dashboard']['icon']}\n{tabs['dashboard']['label']}", key="nav_dashboard", width="stretch", type="primary" if st.session_state.current_tab == 'dashboard' else "secondary"):
        st.session_state.current_tab = 'dashboard'
        st.rerun()

with col4:
    if st.button(f"{tabs['about']['icon']}\n{tabs['about']['label']}", key="nav_about", width="stretch", type="primary" if st.session_state.current_tab == 'about' else "secondary"):
        st.session_state.current_tab = 'about'
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
