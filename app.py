import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from scraper import scrape_apmc_data
from data_config import INDIAN_STATES_DISTRICTS, COMMODITY_IMAGES, TRANSLATIONS

st.set_page_config(
    page_title="Mandi Bhav - मंडी भाव",
    page_icon="🌾",
    layout="centered",
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
if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False
if 'selected_state' not in st.session_state:
    st.session_state.selected_state = None
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = None
if 'price_data' not in st.session_state:
    st.session_state.price_data = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'home'
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'show_commodity_selector' not in st.session_state:
    st.session_state.show_commodity_selector = False
if 'search_commodity' not in st.session_state:
    st.session_state.search_commodity = None
if 'all_commodities_data' not in st.session_state:
    st.session_state.all_commodities_data = None
if 'selected_commodity' not in st.session_state:
    st.session_state.selected_commodity = None
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = 'all'

def get_text(key):
    return TRANSLATIONS[st.session_state.language][key]

def render_onboarding():
    st.markdown("""
    <style>
    .onboarding-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 20px;
        background: linear-gradient(135deg, #4CAF50 0%, #388E3C 50%, #2E7D32 100%);
    }
    .onboarding-card {
        background: white;
        border-radius: 24px;
        padding: 32px 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        max-width: 400px;
        width: 100%;
        text-align: center;
    }
    .welcome-icon {
        font-size: 64px;
        margin-bottom: 16px;
    }
    .welcome-title {
        font-size: 28px;
        font-weight: 600;
        color: #2E7D32 !important;
        margin-bottom: 8px;
    }
    .welcome-subtitle {
        font-size: 16px;
        color: #757575 !important;
        margin-bottom: 32px;
    }
    </style>
    <div class="onboarding-card">
        <div class="welcome-icon">🌾</div>
        <div class="welcome-title">Mandi Bhav में आपका स्वागत है</div>
        <div class="welcome-title">Welcome to Mandi Bhav</div>
        <div class="welcome-subtitle">Your agricultural market price tracker</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📍 Select Your Location")
    st.markdown("Choose your state and district to get personalized market prices")
    
    state_options = list(INDIAN_STATES_DISTRICTS.keys())
    selected_state = st.selectbox(
        "राज्य चुनें / Select State",
        options=state_options,
        index=state_options.index('Gujarat')
    )
    
    district_options = INDIAN_STATES_DISTRICTS[selected_state]['districts']
    if isinstance(district_options[0], dict):
        district_keys = [d['en'] for d in district_options]
        selected_district = st.selectbox(
            "जिला चुनें / Select District",
            options=district_keys,
            index=0
        )
    else:
        selected_district = st.selectbox(
            "जिला चुनें / Select District",
            options=district_options,
            index=0
        )
    
    if st.button("✅ Continue / जारी रखें", type="primary"):
        st.session_state.selected_state = selected_state
        st.session_state.selected_district = selected_district
        st.session_state.onboarding_complete = True
        st.rerun()

def render_commodity_detail():
    commodity = st.session_state.selected_commodity
    
    if commodity is None:
        st.session_state.current_tab = 'home'
        st.rerun()
        return
    
    st.markdown(f"""
    <div class="app-header">
        <h1>{commodity['name_hi']} | {commodity['name_en']}</h1>
        <p>📊 Price Analysis | मूल्य विश्लेषण</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    if st.button("← Back to Home / वापस जाएं", use_container_width=True):
        st.session_state.selected_commodity = None
        st.session_state.current_tab = 'home'
        st.rerun()
    
    st.markdown(f"""
    <div class="metric-card">
        <h4>न्यूनतम / Minimum Price</h4>
        <h2>₹{commodity['min_price']:.0f}</h2>
    </div>
    <div class="metric-card">
        <h4>मॉडल / Modal Price</h4>
        <h2>₹{commodity['modal_price']:.0f}</h2>
    </div>
    <div class="metric-card">
        <h4>अधिकतम / Maximum Price</h4>
        <h2>₹{commodity['max_price']:.0f}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Price Analysis / मूल्य विश्लेषण")
    
    prices_data = {
        'Price Type': ['Minimum\nन्यूनतम', 'Modal\nमॉडल', 'Maximum\nअधिकतम'],
        'Price (₹)': [commodity['min_price'], commodity['modal_price'], commodity['max_price']]
    }
    
    fig = px.bar(
        prices_data,
        x='Price Type',
        y='Price (₹)',
        title=f'{commodity["name_en"]} - {commodity["name_hi"]} Price Range',
        color='Price (₹)',
        color_continuous_scale='Greens'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Roboto', size=14),
        showlegend=False,
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    
    price_diff = commodity['max_price'] - commodity['min_price']
    avg_price = (commodity['min_price'] + commodity['max_price']) / 2
    variation_pct = (price_diff / avg_price) * 100 if avg_price > 0 else 0
    
    st.markdown(f"""
    ### 💡 Price Insights / मूल्य जानकारी
    
    - **Price Range / मूल्य सीमा:** ₹{commodity['min_price']:.0f} - ₹{commodity['max_price']:.0f}
    - **Price Variation / मूल्य भिन्नता:** ₹{price_diff:.0f} ({variation_pct:.1f}%)
    - **Category / श्रेणी:** {commodity.get('category', 'N/A').title()}
    - **Location / स्थान:** {st.session_state.selected_district}, {st.session_state.selected_state}
    
    """)
    
    is_favorite = any(f['name'] == commodity['name_en'] for f in st.session_state.favorites)
    
    if st.button("⭐ Add to Favorites / पसंदीदा में जोड़ें" if not is_favorite else "✅ Remove from Favorites / पसंदीदा से हटाएं", type="primary"):
        if is_favorite:
            st.session_state.favorites = [f for f in st.session_state.favorites if f['name'] != commodity['name_en']]
            st.toast(f"Removed {commodity['name_en']} / {commodity['name_hi']} हटाया गया")
        else:
            st.session_state.favorites.append({
                'name': commodity['name_en'],
                'name_hi': commodity['name_hi'],
                'price': commodity['modal_price'],
                'location': st.session_state.selected_district,
                'image': commodity.get('image', 'attached_assets/stock_images/agricultural_market__f7641e9d.jpg')
            })
            st.toast(f"Added {commodity['name_en']} / {commodity['name_hi']} जोड़ा गया")
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Material 3 Design System */
    :root {
        /* Material 3 Color Tokens */
        --md-sys-color-primary: #2D6A4F;
        --md-sys-color-on-primary: #FFFFFF;
        --md-sys-color-primary-container: #B7E4C7;
        --md-sys-color-on-primary-container: #052E16;
        
        --md-sys-color-secondary: #52796F;
        --md-sys-color-on-secondary: #FFFFFF;
        --md-sys-color-secondary-container: #D8F3DC;
        
        --md-sys-color-surface: #FEFEFE;
        --md-sys-color-surface-variant: #F1F3F4;
        --md-sys-color-on-surface: #1A1C1E;
        --md-sys-color-on-surface-variant: #42474E;
        
        --md-sys-color-outline: #72787E;
        --md-sys-color-outline-variant: #C2C8CE;
        
        --md-sys-color-error: #BA1A1A;
        --md-sys-color-error-container: #FFDAD6;
        
        /* Spacing Tokens */
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 16px;
        --spacing-lg: 24px;
        --spacing-xl: 32px;
        
        /* Typography Scale */
        --type-display-large: 57px;
        --type-headline-large: 32px;
        --type-headline-medium: 28px;
        --type-headline-small: 24px;
        --type-title-large: 22px;
        --type-title-medium: 16px;
        --type-title-small: 14px;
        --type-body-large: 16px;
        --type-body-medium: 14px;
        --type-label-large: 14px;
        
        /* Elevation */
        --elevation-0: none;
        --elevation-1: 0 1px 2px 0 rgba(0, 0, 0, 0.3), 0 1px 3px 1px rgba(0, 0, 0, 0.15);
        --elevation-2: 0 1px 2px 0 rgba(0, 0, 0, 0.3), 0 2px 6px 2px rgba(0, 0, 0, 0.15);
        --elevation-3: 0 4px 8px 3px rgba(0, 0, 0, 0.15), 0 1px 3px 0 rgba(0, 0, 0, 0.3);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Hide Streamlit UI */
    #MainMenu, header, footer, .stDeployButton, 
    [data-testid="stToolbar"], [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], .stActionButton {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Mobile-First Root Layout */
    html, body, .stApp {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        background: var(--md-sys-color-surface-variant);
    }
    
    .main {
        background: var(--md-sys-color-surface-variant);
        padding: 0 !important;
        padding-bottom: env(safe-area-inset-bottom, 80px) !important;
        max-width: 100vw;
        height: 100vh;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        -webkit-overflow-scrolling: touch;
        scroll-behavior: smooth;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    
    /* Typography */
    h1 {
        font-size: var(--type-headline-large) !important;
        font-weight: 600 !important;
        color: var(--md-sys-color-on-surface) !important;
        margin: 0 0 var(--spacing-sm) 0 !important;
        line-height: 1.2 !important;
    }
    
    h2 {
        font-size: var(--type-headline-small) !important;
        font-weight: 600 !important;
        color: var(--md-sys-color-on-surface) !important;
        margin: var(--spacing-md) 0 var(--spacing-sm) 0 !important;
    }
    
    h3 {
        font-size: var(--type-title-large) !important;
        font-weight: 500 !important;
        color: var(--md-sys-color-on-surface) !important;
        margin: var(--spacing-md) 0 var(--spacing-sm) 0 !important;
    }
    
    p, div, span, label {
        color: var(--md-sys-color-on-surface-variant) !important;
        font-size: var(--type-body-medium) !important;
        line-height: 1.5 !important;
    }
    
    /* Modern App Header */
    .app-header {
        background: var(--md-sys-color-primary);
        color: var(--md-sys-color-on-primary);
        padding: var(--spacing-lg) var(--spacing-md);
        padding-top: calc(env(safe-area-inset-top, 0px) + var(--spacing-md));
        box-shadow: var(--elevation-2);
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .app-header h1 {
        color: var(--md-sys-color-on-primary) !important;
        font-size: var(--type-headline-medium) !important;
        margin: 0 !important;
    }
    
    .app-header p {
        color: var(--md-sys-color-on-primary) !important;
        opacity: 0.9;
        margin: var(--spacing-xs) 0 0 0 !important;
        font-size: var(--type-body-medium) !important;
    }
    
    /* Content Container */
    .content-section {
        padding: var(--spacing-md);
    }
    
    /* Material 3 Cards */
    .metric-card {
        background: var(--md-sys-color-surface);
        padding: var(--spacing-md);
        border-radius: 16px;
        box-shadow: var(--elevation-1);
        margin: var(--spacing-sm) 0;
        border: 1px solid var(--md-sys-color-outline-variant);
        transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
    }
    
    .metric-card:active {
        box-shadow: var(--elevation-2);
        transform: scale(0.98);
    }
    
    .metric-card h4 {
        color: var(--md-sys-color-on-surface-variant) !important;
        font-size: var(--type-body-medium) !important;
        font-weight: 500 !important;
        margin-bottom: var(--spacing-xs) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card h2 {
        color: var(--md-sys-color-primary) !important;
        font-size: var(--type-headline-small) !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    
    /* Material 3 Buttons */
    .stButton>button {
        background-color: var(--md-sys-color-primary) !important;
        color: var(--md-sys-color-on-primary) !important;
        font-weight: 600 !important;
        border-radius: 100px !important;
        border: none !important;
        padding: var(--spacing-md) var(--spacing-lg) !important;
        min-height: 48px !important;
        width: 100% !important;
        font-size: var(--type-label-large) !important;
        letter-spacing: 0.1px !important;
        text-transform: none !important;
        box-shadow: var(--elevation-1) !important;
        transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
    }
    
    .stButton>button:hover {
        background-color: var(--md-sys-color-primary) !important;
        box-shadow: var(--elevation-2) !important;
    }
    
    .stButton>button:active {
        transform: scale(0.98) !important;
        box-shadow: var(--elevation-1) !important;
    }
    
    .stButton>button[kind="secondary"] {
        background-color: var(--md-sys-color-surface) !important;
        color: var(--md-sys-color-primary) !important;
        border: 1px solid var(--md-sys-color-outline) !important;
        box-shadow: none !important;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background-color: var(--md-sys-color-secondary-container) !important;
        box-shadow: none !important;
    }
    
    /* Form Inputs */
    [data-testid="stSelectbox"], [data-testid="stTextInput"] {
        margin-bottom: var(--spacing-md) !important;
    }
    
    [data-testid="stSelectbox"] label, [data-testid="stTextInput"] label {
        color: var(--md-sys-color-on-surface) !important;
        font-size: var(--type-body-large) !important;
        font-weight: 500 !important;
        margin-bottom: var(--spacing-sm) !important;
    }
    
    input, select, textarea {
        background-color: var(--md-sys-color-surface) !important;
        color: var(--md-sys-color-on-surface) !important;
        border: 1px solid var(--md-sys-color-outline) !important;
        border-radius: 12px !important;
        font-size: var(--type-body-large) !important;
        padding: var(--spacing-md) !important;
        min-height: 48px !important;
        transition: all 0.2s ease !important;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: var(--md-sys-color-primary) !important;
        outline: 2px solid var(--md-sys-color-primary-container) !important;
        outline-offset: 0px !important;
    }
    
    /* Material 3 Bottom Navigation */
    .bottom-nav {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        background: var(--md-sys-color-surface) !important;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.1) !important;
        border-top: 1px solid var(--md-sys-color-outline-variant) !important;
        z-index: 10000 !important;
        padding-bottom: env(safe-area-inset-bottom, 8px) !important;
        height: auto !important;
        min-height: 80px !important;
        display: flex !important;
        align-items: center !important;
    }
    
    .element-container:has(.bottom-nav) {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        z-index: 10000 !important;
    }
    
    /* Bottom Nav Buttons */
    .bottom-nav .stButton > button {
        background: transparent !important;
        color: var(--md-sys-color-on-surface-variant) !important;
        border: none !important;
        padding: var(--spacing-sm) var(--spacing-xs) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        text-align: center !important;
        width: 100% !important;
        border-radius: 16px !important;
        box-shadow: none !important;
        transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
        min-height: 64px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 4px !important;
        line-height: 1.2 !important;
    }
    
    .bottom-nav .stButton > button:hover {
        background: var(--md-sys-color-secondary-container) !important;
        box-shadow: none !important;
        transform: none !important;
    }
    
    .bottom-nav .stButton > button:active {
        background: var(--md-sys-color-secondary-container) !important;
        transform: scale(0.95) !important;
    }
    
    /* Active Tab - Material 3 Style */
    .bottom-nav .stButton > button[kind="primary"] {
        background: var(--md-sys-color-secondary-container) !important;
        color: var(--md-sys-color-on-secondary-container) !important;
    }
    
    .bottom-nav .stButton > button[kind="primary"]:hover {
        background: var(--md-sys-color-secondary-container) !important;
    }
    
    /* Material 3 Price Cards */
    .price-card {
        background: var(--md-sys-color-surface);
        border-radius: 20px;
        padding: var(--spacing-md);
        margin: var(--spacing-sm) 0;
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        box-shadow: var(--elevation-1);
        border: 1px solid var(--md-sys-color-outline-variant);
        transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
        cursor: pointer;
        min-height: 88px;
    }
    
    .price-card:active {
        transform: scale(0.98);
        box-shadow: var(--elevation-2);
    }
    
    .price-card img {
        width: 56px;
        height: 56px;
        border-radius: 16px;
        object-fit: cover;
        flex-shrink: 0;
    }
    
    .price-info {
        flex: 1;
        min-width: 0;
    }
    
    .price-info h3 {
        margin: 0 0 var(--spacing-xs) 0 !important;
        font-size: var(--type-title-medium) !important;
        color: var(--md-sys-color-on-surface) !important;
        font-weight: 600 !important;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .price-info p {
        margin: 0 !important;
        font-size: var(--type-body-medium) !important;
        color: var(--md-sys-color-on-surface-variant) !important;
    }
    
    .price-value {
        font-size: var(--type-title-large) !important;
        font-weight: 700 !important;
        color: var(--md-sys-color-primary) !important;
        white-space: nowrap;
    }
    
    /* Material 3 Badge */
    .freshness-badge {
        background: var(--md-sys-color-primary-container);
        color: var(--md-sys-color-on-primary-container);
        padding: var(--spacing-xs) var(--spacing-md);
        border-radius: 8px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
        margin-left: var(--spacing-sm);
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Chip Filters */
    .filter-chip {
        display: inline-flex;
        align-items: center;
        gap: var(--spacing-xs);
        padding: var(--spacing-sm) var(--spacing-md);
        background: var(--md-sys-color-surface);
        border: 1px solid var(--md-sys-color-outline);
        border-radius: 8px;
        font-size: var(--type-label-large);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .filter-chip.active {
        background: var(--md-sys-color-secondary-container);
        color: var(--md-sys-color-on-secondary-container);
        border-color: transparent;
    }
    
    /* Misc */
    hr {
        border-color: var(--md-sys-color-outline-variant) !important;
        margin: var(--spacing-lg) 0 !important;
    }
    
    [data-testid="stMarkdownContainer"] p {
        color: var(--md-sys-color-on-surface-variant) !important;
    }
    
    /* Loading & Spinner */
    [data-testid="stSpinner"] > div {
        border-color: var(--md-sys-color-primary) !important;
    }
    </style>
""", unsafe_allow_html=True)

def render_home():
    st.markdown(f"""
    <div class="app-header">
        <h1>🌾 Mandi Bhav | मंडी भाव</h1>
        <p>📍 {st.session_state.selected_district}, {st.session_state.selected_state}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    if st.button("⚙️ Settings / सेटिंग्स", use_container_width=True):
        st.session_state.onboarding_complete = False
        st.rerun()
    
    commodity_search = st.text_input(
        "🔍 Search Commodity / वस्तु खोजें",
        placeholder="टमाटर, प्याज़... / Tomato, Onion...",
        value=st.session_state.search_commodity or ""
    )
    if commodity_search:
        st.session_state.search_commodity = commodity_search
    
    st.markdown("### 🗂️ Categories / श्रेणियां")
    
    categories = {
        'all': {'icon': '🌾', 'name': 'सभी | All'},
        'vegetables': {'icon': '🥬', 'name': 'सब्ज़ियाँ | Vegetables'},
        'fruits': {'icon': '🍎', 'name': 'फल | Fruits'},
        'grains': {'icon': '🌾', 'name': 'अनाज | Grains'},
        'pulses': {'icon': '🫘', 'name': 'दालें | Pulses'}
    }
    
    for cat_key, cat_data in categories.items():
        is_selected = st.session_state.selected_category == cat_key
        btn_style = "primary" if is_selected else "secondary"
        if st.button(f"{cat_data['icon']} {cat_data['name']}", key=f"cat_{cat_key}", type=btn_style, use_container_width=True):
            st.session_state.selected_category = cat_key
            st.rerun()
    
    if st.button("🔍 Search Prices / मूल्य खोजें", type="primary"):
        with st.spinner("Fetching prices / मूल्य प्राप्त कर रहे हैं..."):
            st.session_state.price_data = scrape_apmc_data(
                st.session_state.selected_state, 
                st.session_state.selected_district, 
                commodity_search if commodity_search else None
            )
        st.rerun()
    
    if st.session_state.price_data is not None and not st.session_state.price_data.empty:
        df = st.session_state.price_data
        
        if st.session_state.selected_category != 'all':
            df = df[df['category'] == st.session_state.selected_category]
        
        if len(df) > 0:
            avg_price = df['modal_price'].mean()
            price_range = f"₹{df['min_price'].min():.0f}-{df['max_price'].max():.0f}"
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>वस्तुएँ / Items</h4>
                <h2>{len(df)}</h2>
            </div>
            <div class="metric-card">
                <h4>औसत / Average Price</h4>
                <h2>₹{avg_price:.0f}</h2>
            </div>
            <div class="metric-card">
                <h4>सीमा / Price Range</h4>
                <h2>{price_range}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📊 वस्तुओं की सूची / Commodities List")
            st.markdown('<div style="max-height: 60vh; overflow-y: auto; -webkit-overflow-scrolling: touch;">', unsafe_allow_html=True)
            
            display_commodities = df.head(min(20, len(df)))
            
            for idx, row in display_commodities.iterrows():
                commodity_en = row['commodity_en']
                commodity_hi = row['commodity_hi']
                commodity_img = COMMODITY_IMAGES.get(commodity_en, 'attached_assets/stock_images/agricultural_market__f7641e9d.jpg')
                is_favorite = any(f['name'] == commodity_en for f in st.session_state.favorites)
                fav_icon = "⭐" if is_favorite else "☆"
                
                commodity_key = f"view_{commodity_en}_{idx}"
                if st.button(f"{commodity_hi} / {commodity_en}", key=commodity_key, use_container_width=True):
                    st.session_state.selected_commodity = {
                        'name_en': commodity_en,
                        'name_hi': commodity_hi,
                        'min_price': row['min_price'],
                        'max_price': row['max_price'],
                        'modal_price': row['modal_price'],
                        'category': row['category'],
                        'image': commodity_img
                    }
                    st.rerun()
                
                st.markdown(f"""
                <div class="price-card">
                    <img src="{commodity_img}" alt="{commodity_en}">
                    <div class="price-info">
                        <h3>{commodity_hi} / {commodity_en}</h3>
                        <p>₹{row['min_price']:.0f} - ₹{row['max_price']:.0f} / क्विंटल</p>
                    </div>
                    <div>
                        <div class="price-value">₹{row['modal_price']:.0f}</div>
                        <span class="freshness-badge">आज</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                fav_key = f"fav_{commodity_en}_{idx}"
                if st.button(f"{fav_icon} Favorite / पसंदीदा", key=fav_key, use_container_width=True, type="secondary"):
                    if is_favorite:
                        st.session_state.favorites = [f for f in st.session_state.favorites if f['name'] != commodity_en]
                        st.toast(f"{commodity_hi} हटाया गया / Removed")
                    else:
                        st.session_state.favorites.append({
                            'name': commodity_en,
                            'name_hi': commodity_hi,
                            'price': row['modal_price'],
                            'location': st.session_state.selected_district,
                            'image': commodity_img
                        })
                        st.toast(f"{commodity_hi} जोड़ा गया / Added")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if len(df) > 20:
                st.info(f"📋 Showing 20 of {len(df)} commodities / {len(df)} में से 20 वस्तुएँ दिखाई जा रही हैं")
        else:
            st.warning("इस श्रेणी में कोई वस्तु नहीं मिली / No commodities found for this category.")
    elif st.session_state.price_data is not None and st.session_state.price_data.empty:
        st.warning(f"⚠️ No price data found for {st.session_state.selected_state} - {st.session_state.selected_district}")
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
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_charts():
    st.markdown("""
    <div class="app-header">
        <h1>📊 Charts | चार्ट</h1>
        <p>Price Analytics & Trends | मूल्य विश्लेषण</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    if st.session_state.price_data is not None and not st.session_state.price_data.empty:
        df = st.session_state.price_data
        
        # Top 10 Commodities by Price
        st.markdown("### 📈 Top 10 Highest Priced Commodities")
        top_10 = df.nlargest(10, 'modal_price')[['commodity_en', 'modal_price', 'min_price', 'max_price']]
        
        fig = px.bar(
            top_10, 
            x='commodity_en', 
            y='modal_price',
            title='Top 10 Commodities by Modal Price',
            labels={'commodity_en': 'Commodity', 'modal_price': 'Price (₹)'},
            color='modal_price',
            color_continuous_scale='Greens'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Roboto'),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Category Distribution
        st.markdown("### 🥬 Category Distribution")
        category_counts = df['category'].value_counts()
        
        fig2 = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title='Distribution by Category',
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Roboto'),
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Price Range Analysis
        st.markdown("### 💰 Price Range Analysis")
        fig3 = px.box(
            df, 
            x='category', 
            y='modal_price',
            title='Price Range by Category',
            labels={'category': 'Category', 'modal_price': 'Price (₹)'},
            color='category',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Roboto'),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("📊 Search for prices from the Home tab to see analytics and charts.")
        st.image("attached_assets/stock_images/agricultural_market__f7641e9d.jpg", width="stretch")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_trends():
    st.markdown("""
    <div class="app-header">
        <h1>⭐ Favorites | पसंदीदा</h1>
        <p>Your Saved Commodities | आपकी सहेजी वस्तुएँ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    

def render_about():
    st.markdown("""
    <div class="app-header">
        <h1>ℹ️ About | बारे में</h1>
        <p>About Mandi Bhav | मंडी भाव के बारे में</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    st.markdown("""
    ## Mandi Bhav
    
    **Your trusted agricultural market price tracker**
    
    ### Features
    
    🇮🇳 **Pan-India Coverage**  
    Access prices from all Indian states and districts
    
    🌾 **Wide Range**  
    Vegetables, fruits, grains, and pulses
    
    📊 **Price Analytics**  
    View charts and insights on commodity prices
    
    🔍 **Smart Search**  
    Search for specific commodities by location
    
    ⭐ **Favorites**  
    Save your frequently checked commodities
    
    ---
    
    ### Data Source
    
    Price data is sourced from official data.gov.in APMC API.
    
    ### For Farmers & Traders
    
    Make informed decisions about when and where to sell your produce for the best prices.
    
    ---
    
    **Made for Indian Farmers | 2024**
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.onboarding_complete:
    render_onboarding()
elif st.session_state.selected_commodity is not None:
    render_commodity_detail()
    
    st.markdown('<div style="height: 90px;"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="bottom-nav">
    <style>
    .bottom-nav {
        display: block !important;
        visibility: visible !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 होम | Home", key="nav_home_detail", use_container_width=True, type="primary"):
        st.session_state.selected_commodity = None
        st.session_state.current_tab = 'home'
        st.rerun()
    
    if st.button("⭐ पसंदीदा | Favorites", key="nav_fav_detail", use_container_width=True, type="secondary"):
        st.session_state.selected_commodity = None
        st.session_state.current_tab = 'favorites'
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    tabs = {
        'home': {'icon': '🏠', 'label': 'होम', 'render': render_home},
        'charts': {'icon': '📊', 'label': 'चार्ट', 'render': render_charts},
        'favorites': {'icon': '⭐', 'label': 'पसंदीदा', 'render': render_trends},
        'about': {'icon': 'ℹ️', 'label': 'बारे में', 'render': render_about}
    }
    
    tabs[st.session_state.current_tab]['render']()
    
    st.markdown('<div style="height: 90px;"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="bottom-nav">
    <style>
    .bottom-nav {
        display: block !important;
        visibility: visible !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button(f"{tabs['home']['icon']} {tabs['home']['label']}", key="nav_home", use_container_width=True, type="primary" if st.session_state.current_tab == 'home' else "secondary"):
        st.session_state.current_tab = 'home'
        st.rerun()
    
    if st.button(f"{tabs['charts']['icon']} {tabs['charts']['label']}", key="nav_charts", use_container_width=True, type="primary" if st.session_state.current_tab == 'charts' else "secondary"):
        st.session_state.current_tab = 'charts'
        st.rerun()
    
    if st.button(f"{tabs['favorites']['icon']} {tabs['favorites']['label']}", key="nav_favorites", use_container_width=True, type="primary" if st.session_state.current_tab == 'favorites' else "secondary"):
        st.session_state.current_tab = 'favorites'
        st.rerun()
    
    if st.button(f"{tabs['about']['icon']} {tabs['about']['label']}", key="nav_about", use_container_width=True, type="primary" if st.session_state.current_tab == 'about' else "secondary"):
        st.session_state.current_tab = 'about'
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
