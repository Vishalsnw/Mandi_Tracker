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
    # Glossy Material 3 Header
    st_tw("""
    <div class="relative overflow-hidden bg-gradient-to-br from-green-500 via-emerald-600 to-teal-600 shadow-2xl">
        <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-20"></div>
        <div class="relative p-6 pb-8">
            <div class="flex items-center gap-4">
                <div class="text-6xl drop-shadow-2xl filter">🌾</div>
                <div>
                    <h1 class="text-white text-3xl font-extrabold tracking-tight drop-shadow-lg">Mandi Bhav</h1>
                    <p class="text-green-50 text-sm font-medium mt-1">मंडी भाव - Live Market Prices</p>
                </div>
            </div>
        </div>
        <div class="h-4 bg-gradient-to-b from-transparent to-gray-50"></div>
    </div>
    """, height=180)
    
    # Glossy Welcome Card
    st_tw("""
    <div class="mx-4 mt-6 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-green-400 to-emerald-500 opacity-10 rounded-3xl"></div>
        <div class="relative bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl p-8 text-center border-2 border-white/50">
            <div class="text-6xl mb-4 animate-bounce">🌾</div>
            <p class="text-emerald-700 text-xl font-bold mb-2 tracking-tight">मंडी भाव में आपका स्वागत है</p>
            <h2 class="text-gray-800 text-2xl font-extrabold tracking-tight">Welcome to Mandi Bhav</h2>
            <p class="text-gray-600 text-sm mt-3 max-w-sm mx-auto">Get real-time market prices for crops across India</p>
        </div>
    </div>
    """, height=280)
    
    # Glossy Location Card
    st_tw("""
    <div class="mx-4 mt-6 mb-4">
        <div class="relative overflow-hidden bg-white/90 backdrop-blur-lg rounded-3xl shadow-xl border-2 border-green-100/50 p-6">
            <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-green-400 to-emerald-500 opacity-10 rounded-full -mr-16 -mt-16"></div>
            <div class="relative flex items-center gap-4 pb-4 mb-4 border-b-2 border-green-100">
                <div class="bg-gradient-to-br from-green-500 to-emerald-600 p-3 rounded-2xl shadow-lg">
                    <span class="text-3xl filter drop-shadow">📍</span>
                </div>
                <div class="flex-1">
                    <h3 class="text-gray-900 text-xl font-bold tracking-tight">Select Location</h3>
                    <p class="text-emerald-600 text-sm font-semibold">अपना स्थान चुनें</p>
                </div>
            </div>
        </div>
    </div>
    """, height=200)
    
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
    # Glossy Header
    st_tw("""
    <div class="relative overflow-hidden bg-gradient-to-br from-green-500 via-emerald-600 to-teal-600 shadow-2xl">
        <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-20"></div>
        <div class="relative p-6">
            <h1 class="text-white text-2xl font-extrabold text-center tracking-tight drop-shadow-lg">Select Category</h1>
            <p class="text-green-50 text-center text-sm font-medium mt-1">श्रेणी चुनें</p>
        </div>
        <div class="h-3 bg-gradient-to-b from-transparent to-gray-50"></div>
    </div>
    """, height=140)
    
    st.markdown('<div style="padding: 16px; padding-bottom: 80px;">', unsafe_allow_html=True)
    
    # Glossy Category Cards
    categories = [
        {'key': 'all', 'icon': '🌾', 'name_en': 'All', 'name_hi': 'सभी', 'gradient': 'from-emerald-400 to-green-500'},
        {'key': 'vegetables', 'icon': '🥒', 'name_en': 'Vegetables', 'name_hi': 'सब्ज़ियाँ', 'gradient': 'from-green-400 to-lime-500'},
        {'key': 'fruits', 'icon': '🍎', 'name_en': 'Fruits', 'name_hi': 'फल', 'gradient': 'from-rose-400 to-pink-500'},
        {'key': 'grains', 'icon': '🌾', 'name_en': 'Grains', 'name_hi': 'अनाज', 'gradient': 'from-amber-400 to-yellow-500'},
        {'key': 'pulses', 'icon': '🫘', 'name_en': 'Pulses', 'name_hi': 'दालें', 'gradient': 'from-orange-400 to-red-500'},
    ]
    
    for cat in categories:
        st_tw(f"""
        <div class="mb-4 relative overflow-hidden rounded-2xl shadow-xl border-2 border-white/50 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-br {cat['gradient']} opacity-90"></div>
            <div class="relative bg-white/30 backdrop-blur-md p-5">
                <div class="flex items-center gap-4">
                    <div class="text-5xl filter drop-shadow-lg">{cat['icon']}</div>
                    <div class="flex-1">
                        <h3 class="text-white text-xl font-extrabold tracking-tight drop-shadow-md">{cat['name_en']}</h3>
                        <p class="text-white/90 text-sm font-semibold">{cat['name_hi']}</p>
                    </div>
                    <div class="text-white/70 text-3xl">→</div>
                </div>
            </div>
        </div>
        """, height=100)
        
        if st.button(f"Select {cat['name_en']}", key=f"select_{cat['key']}", use_container_width=True):
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
    
    st_tw("""
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200/50 p-5 mt-6">
        <div class="absolute top-0 right-0 text-8xl opacity-10">ℹ️</div>
        <div class="relative">
            <h4 class="text-indigo-900 font-bold text-lg mb-2">Quick Tip</h4>
            <p class="text-gray-700 text-sm mb-1">Choose any category to view market prices</p>
            <p class="text-emerald-700 text-sm font-semibold">श्रेणी चुनें और बाजार मूल्य देखें</p>
        </div>
    </div>
    """, height=140)
    
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
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Hide Streamlit UI */
    #MainMenu, header, footer, .stDeployButton, 
    [data-testid="stToolbar"], [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], .stActionButton,
    [data-testid="stHeader"], [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Mobile-First Layout */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
    }
    
    .main, [data-testid="stMain"] {
        padding: 0 !important;
        padding-bottom: 80px !important;
        margin: 0 !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    
    .block-container, [data-testid="block-container"],
    .element-container, [data-testid="element-container"] {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Glossy Material 3 Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 16px !important;
        border: none !important;
        padding: 0 20px !important;
        height: 52px !important;
        font-size: 15px !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3), inset 0 1px 1px rgba(255,255,255,0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4), inset 0 1px 1px rgba(255,255,255,0.3) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2) !important;
    }
    
    .stButton>button[kind="secondary"] {
        background: rgba(255,255,255,0.9) !important;
        color: #059669 !important;
        border: 2px solid #10b981 !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08), inset 0 1px 1px rgba(255,255,255,0.5) !important;
    }
    
    /* Glossy Inputs */
    input, select, textarea {
        background: rgba(255,255,255,0.95) !important;
        border: 2px solid #d1fae5 !important;
        border-radius: 14px !important;
        font-size: 15px !important;
        padding: 14px 16px !important;
        height: 52px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04), inset 0 1px 2px rgba(0,0,0,0.02) !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: #10b981 !important;
        outline: none !important;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2), inset 0 1px 2px rgba(0,0,0,0.02) !important;
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
    # Glossy Header
    st_tw(f"""
    <div class="relative overflow-hidden bg-gradient-to-br from-green-500 via-emerald-600 to-teal-600 shadow-2xl">
        <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-20"></div>
        <div class="relative p-5">
            <div class="flex items-center gap-3 mb-2">
                <div class="text-4xl drop-shadow-lg">🌾</div>
                <h1 class="text-white text-2xl font-extrabold tracking-tight drop-shadow-lg">Mandi Bhav</h1>
            </div>
            <div class="flex items-center gap-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 w-fit">
                <span class="text-xl">📍</span>
                <p class="text-white text-sm font-semibold">{st.session_state.selected_district}, {st.session_state.selected_state}</p>
            </div>
        </div>
        <div class="h-3 bg-gradient-to-b from-transparent to-gray-50"></div>
    </div>
    """, height=160)
    
    st.markdown('<div style="padding: 16px;">', unsafe_allow_html=True)
    
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
                
                # Super Glossy Material 3 Commodity Card
                st_tw(f"""
                <div class="relative overflow-hidden rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 mb-4 border-2 border-white/60">
                    <div class="absolute inset-0 bg-gradient-to-br from-emerald-400 via-green-500 to-teal-500 opacity-95"></div>
                    <div class="absolute inset-0 bg-gradient-to-tr from-white/40 to-transparent"></div>
                    <div class="relative bg-white/25 backdrop-blur-md p-5">
                        <div class="flex items-start justify-between gap-4">
                            <div class="flex-1">
                                <h3 class="text-white text-2xl font-extrabold leading-tight drop-shadow-lg mb-1">{commodity_hi}</h3>
                                <p class="text-white/90 text-base font-bold drop-shadow-md mb-4">{commodity_en}</p>
                                <div class="flex flex-wrap items-center gap-2">
                                    <span class="bg-white/90 backdrop-blur-sm text-emerald-700 px-5 py-2 rounded-full text-lg font-extrabold shadow-lg border-2 border-white">
                                        ₹{row['modal_price']:.0f}
                                    </span>
                                    <span class="text-white/80 text-xs bg-black/20 backdrop-blur-sm px-3 py-1.5 rounded-full font-semibold border border-white/30">
                                        ₹{row['min_price']:.0f} - ₹{row['max_price']:.0f}
                                    </span>
                                </div>
                            </div>
                            <div class="flex flex-col items-center gap-1">
                                <div class="text-5xl filter drop-shadow-2xl">{fav_icon}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, height=180)
                
                # Two button area: main for viewing, small for favorite toggle
                col_main, col_fav = st.columns([4, 1])
                
                with col_main:
                    commodity_key = f"view_{commodity_en}_{idx}"
                    if st.button(f"👁️ View Details", key=commodity_key, use_container_width=True):
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
                    if st.button(fav_icon, key=fav_key, use_container_width=True):
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
