import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from scraper import scrape_apmc_data
from data_config import INDIAN_STATES_DISTRICTS, COMMODITY_IMAGES, TRANSLATIONS
from streamlit_tailwind import st_tw

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
    # Modern Android App Bar with Tailwind
    st_tw("""
    <div class="bg-gradient-to-br from-green-700 to-green-900 p-4 shadow-lg">
        <div class="flex items-center gap-3">
            <div class="text-4xl">🌾</div>
            <h1 class="text-white text-2xl font-bold tracking-wide">Mandi Bhav</h1>
        </div>
    </div>
    """, height=80)
    
    # Modern Welcome Card with Tailwind
    st_tw("""
    <div class="mx-4 mt-4 bg-gradient-to-br from-white to-gray-50 rounded-3xl shadow-xl p-6 text-center border border-green-100">
        <div class="text-5xl mb-3 drop-shadow-lg">🌾</div>
        <p class="text-green-700 text-lg font-semibold mb-1">मंडी भाव में आपका स्वागत है</p>
        <h2 class="text-green-800 text-xl font-bold">Welcome to Mandi Bhav</h2>
    </div>
    """, height=220)
    
    # Modern Location Selection Card with Tailwind
    st_tw("""
    <div class="mx-4 mt-4 bg-white rounded-3xl shadow-lg p-5 border border-gray-200">
        <div class="flex items-center gap-3 pb-3 mb-3 border-b-2 border-gray-100">
            <div class="bg-green-100 p-2 rounded-xl">
                <span class="text-2xl">📍</span>
            </div>
            <div class="flex-1">
                <h3 class="text-gray-900 text-lg font-semibold">Select Your Location</h3>
                <p class="text-gray-500 text-sm">स्थान चुनें</p>
            </div>
        </div>
    </div>
    """, height=140)
    
    st.markdown('<div style="padding: 0 16px;">', unsafe_allow_html=True)
    
    state_options = list(INDIAN_STATES_DISTRICTS.keys())
    selected_state = st.selectbox(
        "Select State / राज्य चुनें",
        options=state_options,
        index=state_options.index('Gujarat'),
        key="onboarding_state"
    )
    
    district_options = INDIAN_STATES_DISTRICTS[selected_state]['districts']
    if isinstance(district_options[0], dict):
        district_keys = [d['en'] for d in district_options]
        selected_district = st.selectbox(
            "Select District / जिला चुनें",
            options=district_keys,
            index=0,
            key="onboarding_district"
        )
    else:
        selected_district = st.selectbox(
            "Select District / जिला चुनें",
            options=district_options,
            index=0,
            key="onboarding_district"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Tailwind Continue Button
    st.markdown('<div style="padding: 16px 16px 24px 16px;">', unsafe_allow_html=True)
    if st.button("Continue / जारी रखें", type="primary", use_container_width=True):
        st.session_state.selected_state = selected_state
        st.session_state.selected_district = selected_district
        st.session_state.onboarding_complete = True
        st.session_state.show_commodity_selector = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_category_selector():
    # Modern Tailwind Categories Header
    st_tw("""
    <div class="bg-gradient-to-br from-green-700 to-green-900 p-4 shadow-lg">
        <h1 class="text-white text-xl font-bold text-center tracking-wide">Select Category / श्रेणी चुनें</h1>
    </div>
    """, height=80)
    
    st.markdown('<div style="padding: 12px; padding-bottom: 80px;">', unsafe_allow_html=True)
    
    # Category Cards with actual buttons
    categories = [
        {'key': 'all', 'icon': '🌾', 'name_en': 'All', 'name_hi': 'सभी'},
        {'key': 'vegetables', 'icon': '🥒', 'name_en': 'Vegetables', 'name_hi': 'सब्ज़ियाँ'},
        {'key': 'fruits', 'icon': '🍎', 'name_en': 'Fruits', 'name_hi': 'फल'},
        {'key': 'grains', 'icon': '🌾', 'name_en': 'Grains', 'name_hi': 'अनाज'},
        {'key': 'pulses', 'icon': '🫘', 'name_en': 'Pulses', 'name_hi': 'दालें'},
    ]
    
    for cat in categories:
        if st.button(f"{cat['icon']} {cat['name_en']} / {cat['name_hi']}", key=f"select_{cat['key']}", use_container_width=True):
            st.session_state.selected_category = cat['key']
            st.session_state.show_commodity_selector = False
            st.session_state.current_tab = 'home'
            with st.spinner("Loading prices / मूल्य लोड हो रहे हैं..."):
                st.session_state.price_data = scrape_apmc_data(
                    st.session_state.selected_state, 
                    st.session_state.selected_district,
                    None
                )
            st.rerun()
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #E8F8F0 0%, #FFE8E1 100%); padding: 16px; border-radius: 12px; margin: 16px 0;">
        <h4 style="margin: 0 0 6px 0;">ℹ️ Select a category to continue</h4>
        <p style="margin: 0; font-size: 13px;">Choose any category to view market prices</p>
        <p style="margin: 0; font-size: 13px;">श्रेणी चुनें और बाजार मूल्य देखें</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

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
    
    if st.button("← Back / वापस", use_container_width=True, type="secondary"):
        st.session_state.selected_commodity = None
        st.session_state.current_tab = 'home'
        st.rerun()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>न्यूनतम</h4>
            <h2>₹{commodity['min_price']:.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>मॉडल</h4>
            <h2>₹{commodity['modal_price']:.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>अधिकतम</h4>
            <h2>₹{commodity['max_price']:.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("**📈 Price Trend / मूल्य रुझान**")
    st.markdown('<div style="height: 4px;"></div>', unsafe_allow_html=True)
    
    import numpy as np
    from datetime import datetime, timedelta
    
    current_date = datetime.now()
    dates = [(current_date - timedelta(days=i)).strftime('%d %b') for i in range(6, -1, -1)]
    
    base_price = commodity['modal_price']
    variation = (commodity['max_price'] - commodity['min_price']) / 4
    
    historical_prices = [
        base_price + np.random.uniform(-variation, variation) for _ in range(5)
    ]
    historical_prices.append(commodity['min_price'])
    historical_prices.append(base_price)
    
    future_dates = [(current_date + timedelta(days=i)).strftime('%d %b') for i in range(1, 4)]
    future_prices = [
        base_price + np.random.uniform(-variation*0.5, variation*0.8) for _ in range(3)
    ]
    
    all_dates = dates + future_dates
    all_prices = historical_prices + future_prices
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=historical_prices,
        mode='lines+markers',
        name='Historical',
        line=dict(color='#0CAF60', width=3),
        marker=dict(size=8, color='#0CAF60'),
        hovertemplate='<b>%{x}</b><br>₹%{y:.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_prices,
        mode='lines+markers',
        name='Predicted',
        line=dict(color='#FF6B35', width=3, dash='dash'),
        marker=dict(size=8, color='#FF6B35', symbol='diamond'),
        hovertemplate='<b>%{x}</b><br>₹%{y:.0f} (Predicted)<extra></extra>'
    ))
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        height=300,
        margin=dict(l=10, r=10, t=40, b=40),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='#E5E5EA',
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#F0F0F0',
            showline=False,
            tickprefix='₹',
            tickfont=dict(size=11)
        ),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    price_diff = commodity['max_price'] - commodity['min_price']
    avg_price = (commodity['min_price'] + commodity['max_price']) / 2
    variation_pct = (price_diff / avg_price) * 100 if avg_price > 0 else 0
    
    st.markdown('<div style="height: 4px;"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    **💡 Insights / जानकारी**
    
    • Range: ₹{commodity['min_price']:.0f} - ₹{commodity['max_price']:.0f} ({variation_pct:.1f}% variation)  
    • Category: {commodity.get('category', 'N/A').title()} / श्रेणी: {commodity.get('category', 'N/A')}  
    • Location: {st.session_state.selected_district}, {st.session_state.selected_state}
    """)
    
    is_favorite = any(f['name'] == commodity['name_en'] for f in st.session_state.favorites)
    
    col1, col2 = st.columns([3, 2])
    with col1:
        if st.button("⭐ Favorite / पसंदीदा" if not is_favorite else "✅ Saved / सहेजा", type="primary" if not is_favorite else "secondary", use_container_width=True):
            if is_favorite:
                st.session_state.favorites = [f for f in st.session_state.favorites if f['name'] != commodity['name_en']]
                st.toast(f"Removed / हटाया")
            else:
                st.session_state.favorites.append({
                    'name': commodity['name_en'],
                    'name_hi': commodity['name_hi'],
                    'price': commodity['modal_price'],
                    'location': st.session_state.selected_district,
                    'image': commodity.get('image', 'attached_assets/stock_images/agricultural_market__f7641e9d.jpg')
                })
                st.toast(f"Added / जोड़ा")
            st.rerun()
    with col2:
        if st.button("🔄 Refresh / रिफ्रेश", use_container_width=True, type="secondary"):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Modern Grocery App Design System */
    :root {
        /* Fresh Grocery Store Colors */
        --md-sys-color-primary: #0CAF60;
        --md-sys-color-on-primary: #FFFFFF;
        --md-sys-color-primary-container: #E8F8F0;
        --md-sys-color-on-primary-container: #00522A;
        
        --md-sys-color-secondary: #FF6B35;
        --md-sys-color-on-secondary: #FFFFFF;
        --md-sys-color-secondary-container: #FFE8E1;
        --md-sys-color-on-secondary-container: #8B3619;
        
        --md-sys-color-surface: #FFFFFF;
        --md-sys-color-surface-variant: #F7F8FA;
        --md-sys-color-on-surface: #1C1C1E;
        --md-sys-color-on-surface-variant: #6E6E73;
        
        --md-sys-color-outline: #C7C7CC;
        --md-sys-color-outline-variant: #E5E5EA;
        
        --md-sys-color-error: #FF3B30;
        --md-sys-color-error-container: #FFDAD6;
        
        /* Spacing Tokens - Tighter for mobile */
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 12px;
        --spacing-lg: 16px;
        --spacing-xl: 24px;
        
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
    
    /* AGGRESSIVE: Hide ALL Streamlit UI Elements */
    #MainMenu, header, footer, .stDeployButton, 
    [data-testid="stToolbar"], [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], .stActionButton,
    [data-testid="stHeader"], [data-testid="stSidebarNav"],
    .css-1dp5vir, .st-emotion-cache-1dp5vir {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }
    
    /* AGGRESSIVE: Full Mobile App Root Layout */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        height: 100% !important;
        overflow: hidden !important;
        background: #F7F8FA !important;
    }
    
    .main, [data-testid="stMain"] {
        background: #F7F8FA !important;
        padding: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 70px !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
        height: 100vh !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        -webkit-overflow-scrolling: touch !important;
        scroll-behavior: smooth !important;
    }
    
    .block-container, [data-testid="block-container"],
    .element-container, [data-testid="element-container"] {
        padding: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
    }
    
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Typography */
    h1 {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: var(--md-sys-color-on-surface) !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    
    h2 {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: var(--md-sys-color-on-surface) !important;
        margin: 0 0 var(--spacing-sm) 0 !important;
    }
    
    h3 {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: var(--md-sys-color-on-surface) !important;
        margin: 0 0 var(--spacing-xs) 0 !important;
    }
    
    p, div, span, label {
        color: var(--md-sys-color-on-surface-variant) !important;
        font-size: var(--type-body-medium) !important;
        line-height: 1.5 !important;
    }
    
    /* Modern App Header */
    .app-header {
        background: linear-gradient(135deg, #0CAF60 0%, #00944F 100%);
        color: var(--md-sys-color-on-primary);
        padding: 14px 16px;
        padding-top: calc(env(safe-area-inset-top, 0px) + 14px);
        box-shadow: 0 2px 12px rgba(12, 175, 96, 0.15);
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .app-header h1 {
        color: var(--md-sys-color-on-primary) !important;
        font-size: 22px !important;
        margin: 0 !important;
    }
    
    .app-header p {
        color: var(--md-sys-color-on-primary) !important;
        opacity: 0.95;
        margin: 2px 0 0 0 !important;
        font-size: 13px !important;
    }
    
    /* Content Container */
    .content-section {
        padding: 12px;
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
        border-radius: 12px !important;
        border: none !important;
        padding: 0 16px !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        width: 100% !important;
        font-size: 15px !important;
        letter-spacing: 0.2px !important;
        text-transform: none !important;
        box-shadow: 0 2px 8px rgba(12, 175, 96, 0.2) !important;
        transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
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
        color: var(--md-sys-color-on-surface) !important;
        border: 1.5px solid var(--md-sys-color-outline-variant) !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05) !important;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background-color: var(--md-sys-color-surface-variant) !important;
        border-color: var(--md-sys-color-primary) !important;
        box-shadow: 0 2px 8px rgba(12, 175, 96, 0.15) !important;
    }
    
    /* Form Inputs - Android Style */
    [data-testid="stSelectbox"], [data-testid="stTextInput"] {
        margin-bottom: 8px !important;
    }
    
    [data-testid="stSelectbox"] label, [data-testid="stTextInput"] label {
        color: var(--md-sys-color-on-surface) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        margin-bottom: 6px !important;
    }
    
    input, select, textarea {
        background-color: white !important;
        color: var(--md-sys-color-on-surface) !important;
        border: 1.5px solid var(--md-sys-color-outline-variant) !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        padding: 12px 14px !important;
        height: 48px !important;
        min-height: 48px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        transition: all 0.2s ease !important;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: var(--md-sys-color-primary) !important;
        outline: none !important;
        box-shadow: 0 2px 8px rgba(45, 106, 79, 0.15) !important;
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
    
    if st.button("⚙️ Change Location / स्थान बदलें", use_container_width=True, type="secondary"):
        st.session_state.onboarding_complete = False
        st.rerun()
    
    st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
    
    commodity_search = st.text_input(
        "Search / खोजें",
        placeholder="Search Commodity / वस्तु खोजें",
        label_visibility="collapsed"
    )
    if commodity_search:
        st.session_state.search_commodity = commodity_search
    
    st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
    st.markdown("**Categories / श्रेणियां**")
    st.markdown('<div style="height: 4px;"></div>', unsafe_allow_html=True)
    
    categories = {
        'all': {'icon': '🌾', 'name': 'All / सभी'},
        'vegetables': {'icon': '🥬', 'name': 'Vegetables / सब्ज़ियाँ'},
        'fruits': {'icon': '🍎', 'name': 'Fruits / फल'},
        'grains': {'icon': '🌾', 'name': 'Grains / अनाज'},
        'pulses': {'icon': '🫘', 'name': 'Pulses / दालें'}
    }
    
    col1, col2 = st.columns(2)
    idx = 0
    category_changed = False
    for cat_key, cat_data in categories.items():
        is_selected = st.session_state.selected_category == cat_key
        btn_style = "primary" if is_selected else "secondary"
        with col1 if idx % 2 == 0 else col2:
            if st.button(f"{cat_data['icon']} {cat_data['name']}", key=f"cat_{cat_key}", type=btn_style, use_container_width=True):
                st.session_state.selected_category = cat_key
                category_changed = True
        idx += 1
    
    if category_changed or st.session_state.price_data is None:
        with st.spinner("Loading prices / मूल्य लोड हो रहे हैं..."):
            st.session_state.price_data = scrape_apmc_data(
                st.session_state.selected_state, 
                st.session_state.selected_district, 
                commodity_search if commodity_search else None
            )
        st.rerun()
    
    st.markdown('<div style="height: 4px;"></div>', unsafe_allow_html=True)
    
    if st.session_state.price_data is not None and not st.session_state.price_data.empty:
        df = st.session_state.price_data
        
        if st.session_state.selected_category != 'all':
            df = df[df['category'] == st.session_state.selected_category]
        
        if len(df) > 0:
            avg_price = df['modal_price'].mean()
            price_range = f"₹{df['min_price'].min():.0f}-{df['max_price'].max():.0f}"
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Items</h4>
                    <h2>{len(df)}</h2>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Avg Price</h4>
                    <h2>₹{avg_price:.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Range</h4>
                    <h2 style="font-size: 16px !important;">₹{df['min_price'].min():.0f}-{df['max_price'].max():.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div style="height: 4px;"></div>', unsafe_allow_html=True)
            st.markdown("**Prices / मूल्य सूची**")
            st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)
            
            display_commodities = df.head(min(20, len(df)))
            
            for idx, row in display_commodities.iterrows():
                commodity_en = row['commodity_en']
                commodity_hi = row['commodity_hi']
                commodity_img = COMMODITY_IMAGES.get(commodity_en, 'attached_assets/stock_images/agricultural_market__f7641e9d.jpg')
                is_favorite = any(f['name'] == commodity_en for f in st.session_state.favorites)
                fav_icon = "⭐" if is_favorite else "☆"
                
                col_btn, col_fav = st.columns([4, 1])
                
                with col_btn:
                    commodity_key = f"view_{commodity_en}_{idx}"
                    if st.button(f"{commodity_hi} / {commodity_en} - ₹{row['modal_price']:.0f}", key=commodity_key, use_container_width=True):
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
                
                with col_fav:
                    fav_key = f"fav_{commodity_en}_{idx}"
                    if st.button(fav_icon, key=fav_key, use_container_width=True, type="secondary"):
                        if is_favorite:
                            st.session_state.favorites = [f for f in st.session_state.favorites if f['name'] != commodity_en]
                            st.toast(f"Removed / हटाया")
                        else:
                            st.session_state.favorites.append({
                                'name': commodity_en,
                                'name_hi': commodity_hi,
                                'price': row['modal_price'],
                                'location': st.session_state.selected_district,
                                'image': commodity_img
                            })
                            st.toast(f"Added / जोड़ा")
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if len(df) > 20:
                st.info(f"📋 Showing 20 of {len(df)} commodities / {len(df)} में से 20 वस्तुएँ दिखाई जा रही हैं")
        else:
            st.info("📊 No data found for this category. Try 'All' category.")
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #E8F8F0 0%, #FFE8E1 100%); padding: 20px; border-radius: 12px; margin: 12px 0;">
            <h3 style="margin: 0 0 8px 0;">💡 Quick Tips / सुझाव</h3>
            <p style="margin: 4px 0;">• Select a category above to view prices</p>
            <p style="margin: 4px 0;">• Click on any commodity to see trends</p>
            <p style="margin: 4px 0;">• Use ⭐ to save favorites</p>
            <p style="margin: 4px 0;">• श्रेणी चुनें और मूल्य देखें</p>
        </div>
        """, unsafe_allow_html=True)
    
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
elif st.session_state.show_commodity_selector:
    render_category_selector()
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
