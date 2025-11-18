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
    <div class="green-header">
        <h1>📊 {commodity['name_en']}</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">{commodity['name_hi']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    if st.button("← Back to Home / वापस जाएं"):
        st.session_state.selected_commodity = None
        st.session_state.current_tab = 'home'
        st.rerun()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>न्यूनतम / Min</h4>
            <h2>₹{commodity['min_price']:.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>मॉडल / Modal</h4>
            <h2>₹{commodity['modal_price']:.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>अधिकतम / Max</h4>
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
    
    /* Mobile-first layout - Android App Style */
    html, body {
        overflow: hidden;
        height: 100vh;
        width: 100vw;
    }
    
    .stApp {
        background-color: #F5F5F5;
        max-width: 100vw;
        height: 100vh;
        margin: 0;
        padding: 0;
        overflow: hidden;
    }
    
    .main {
        background-color: #F5F5F5;
        padding: 0 !important;
        padding-bottom: 70px !important;
        max-width: 100vw;
        margin: 0;
        height: calc(100vh - 70px);
        overflow-y: auto !important;
        overflow-x: hidden !important;
        -webkit-overflow-scrolling: touch;
    }
    
    .block-container {
        padding: 0px !important;
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
        border-radius: 0px;
        margin-bottom: 0px;
        margin: 0 0 16px 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    
    .content-section {
        padding: 16px;
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
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        background: #FFFFFF !important;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.15) !important;
        border-top: 1px solid #E0E0E0 !important;
        z-index: 10000 !important;
        padding: 4px 0 8px 0 !important;
        height: 70px !important;
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
    st.markdown(f"""
    <div class="green-header">
        <h1>🌾 Mandi Bhav</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">आपकी मंडी के सभी भाव</p>
        <p style="color: rgba(255,255,255,0.9) !important; margin: 4px 0 0 0; font-size: 12px;">📍 {st.session_state.selected_district}, {st.session_state.selected_state}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⚙️"):
            st.session_state.onboarding_complete = False
            st.rerun()
    with col2:
        commodity_search = st.text_input(
            "🔍 खोजें / Search",
            placeholder="टमाटर, प्याज़... / Tomato, Onion...",
            value=st.session_state.search_commodity or "",
            label_visibility="collapsed"
        )
        if commodity_search:
            st.session_state.search_commodity = commodity_search
    
    st.markdown("### 🗂️ Categories / श्रेणियां")
    
    categories = {
        'all': {'icon': '🌾', 'name_en': 'All', 'name_hi': 'सभी'},
        'vegetables': {'icon': '🥬', 'name_en': 'Vegetables', 'name_hi': 'सब्ज़ियाँ'},
        'fruits': {'icon': '🍎', 'name_en': 'Fruits', 'name_hi': 'फल'},
        'grains': {'icon': '🌾', 'name_en': 'Grains', 'name_hi': 'अनाज'},
        'pulses': {'icon': '🫘', 'name_en': 'Pulses', 'name_hi': 'दालें'}
    }
    
    cols = st.columns(5)
    for idx, (cat_key, cat_data) in enumerate(categories.items()):
        with cols[idx]:
            is_selected = st.session_state.selected_category == cat_key
            btn_style = "primary" if is_selected else "secondary"
            if st.button(f"{cat_data['icon']}\n{cat_data['name_hi']}\n{cat_data['name_en']}", key=f"cat_{cat_key}", type=btn_style):
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
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>वस्तुएँ / Items</h4>
                    <h2>{len(df)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_price = df['modal_price'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <h4>औसत / Avg</h4>
                    <h2>₹{avg_price:.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                price_range = f"₹{df['min_price'].min():.0f}-{df['max_price'].max():.0f}"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>सीमा / Range</h4>
                    <h2 style="font-size: 18px !important;">{price_range}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 📊 वस्तुओं की सूची / Commodities List")
            st.markdown('<div style="max-height: 60vh; overflow-y: auto; -webkit-overflow-scrolling: touch;">', unsafe_allow_html=True)
            
            display_commodities = df.head(min(20, len(df)))
            
            for idx, row in display_commodities.iterrows():
                commodity_en = row['commodity_en']
                commodity_hi = row['commodity_hi']
                commodity_img = COMMODITY_IMAGES.get(commodity_en, 'attached_assets/stock_images/agricultural_market__f7641e9d.jpg')
                
                col_a, col_b = st.columns([5, 1])
                
                with col_a:
                    if st.button(f"{commodity_hi}\n{commodity_en}", key=f"view_{commodity_en}_{idx}", use_container_width=True):
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
                    <div class="price-card" style="margin-top: -10px;">
                        <img src="{commodity_img}" alt="{commodity_en}">
                        <div class="price-info">
                            <h3>{commodity_hi} / {commodity_en}</h3>
                            <p style="color: #757575 !important;">₹{row['min_price']:.0f} - ₹{row['max_price']:.0f} / क्विंटल</p>
                        </div>
                        <div>
                            <div class="price-value">₹{row['modal_price']:.0f}</div>
                            <span class="freshness-badge">● आज</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_b:
                    fav_key = f"fav_{commodity_en}_{idx}"
                    is_favorite = any(f['name'] == commodity_en for f in st.session_state.favorites)
                    
                    if st.button("⭐" if is_favorite else "☆", key=fav_key):
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
    <div class="green-header">
        <h1>📊 Price Analytics</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">View Trends & Insights</p>
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
    <div class="green-header">
        <h1>⭐ Favorites</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">Your Saved Commodities</p>
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
    <div class="green-header">
        <h1>ℹ️ About</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">About This App</p>
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠\nHome\nहोम", key="nav_home_detail", width="stretch", type="primary"):
            st.session_state.selected_commodity = None
            st.session_state.current_tab = 'home'
            st.rerun()
    
    with col2:
        if st.button("⭐\nFavorites\nपसंदीदा", key="nav_fav_detail", width="stretch", type="secondary"):
            st.session_state.selected_commodity = None
            st.session_state.current_tab = 'favorites'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    tabs = {
        'home': {'icon': '🏠', 'label_en': 'Home', 'label_hi': 'होम', 'render': render_home},
        'charts': {'icon': '📊', 'label_en': 'Charts', 'label_hi': 'चार्ट', 'render': render_charts},
        'favorites': {'icon': '⭐', 'label_en': 'Favorites', 'label_hi': 'पसंदीदा', 'render': render_trends},
        'about': {'icon': 'ℹ️', 'label_en': 'About', 'label_hi': 'बारे में', 'render': render_about}
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
        if st.button(f"{tabs['home']['icon']}\n{tabs['home']['label_hi']}\n{tabs['home']['label_en']}", key="nav_home", width="stretch", type="primary" if st.session_state.current_tab == 'home' else "secondary"):
            st.session_state.current_tab = 'home'
            st.rerun()
    
    with col2:
        if st.button(f"{tabs['charts']['icon']}\n{tabs['charts']['label_hi']}\n{tabs['charts']['label_en']}", key="nav_charts", width="stretch", type="primary" if st.session_state.current_tab == 'charts' else "secondary"):
            st.session_state.current_tab = 'charts'
            st.rerun()
    
    with col3:
        if st.button(f"{tabs['favorites']['icon']}\n{tabs['favorites']['label_hi']}\n{tabs['favorites']['label_en']}", key="nav_favorites", width="stretch", type="primary" if st.session_state.current_tab == 'favorites' else "secondary"):
            st.session_state.current_tab = 'favorites'
            st.rerun()
    
    with col4:
        if st.button(f"{tabs['about']['icon']}\n{tabs['about']['label_hi']}\n{tabs['about']['label_en']}", key="nav_about", width="stretch", type="primary" if st.session_state.current_tab == 'about' else "secondary"):
            st.session_state.current_tab = 'about'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
