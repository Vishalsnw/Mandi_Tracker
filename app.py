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
    
    .stApp {
        background-color: #F5F5F5;
        max-width: 480px;
        margin: 0 auto;
    }
    
    .main {
        background-color: #F5F5F5;
        padding: 0;
        padding-bottom: 80px;
    }
    
    .block-container {
        padding: 1rem;
        max-width: 480px;
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 8px 0;
        border: 1px solid #E0E0E0;
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
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        text-align: center;
    }
    
    .green-header h1 {
        color: white !important;
        margin: 0;
    }
    
    .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: 500;
        border-radius: 24px;
        border: none;
        padding: 14px 32px;
        width: 100%;
        font-size: 16px;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
    }
    
    .stButton>button:hover {
        background-color: #45a049 !important;
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.4);
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
        left: 50%;
        transform: translateX(-50%);
        max-width: 480px;
        width: 100%;
        background: #FFFFFF;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
        border-top: 1px solid #E0E0E0;
        z-index: 999;
        padding: 8px 0;
        border-radius: 16px 16px 0 0;
    }
    
    .nav-button {
        background: transparent !important;
        color: #757575 !important;
        border: none !important;
        padding: 8px !important;
        font-size: 11px !important;
        text-align: center !important;
        width: 100% !important;
    }
    
    .nav-button:hover {
        background: #F5F5F5 !important;
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
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .commodity-item:hover {
        border-color: #4CAF50;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
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
        background: #4CAF50;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 11px;
        display: inline-block;
        margin-left: 8px;
    }
    
    .price-card {
        background: #F5F5F5;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 12px;
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
            
            for idx, row in top_commodities.iterrows():
                commodity_en = row['commodity_en']
                commodity_hi = row['commodity_hi']
                commodity_img = COMMODITY_IMAGES.get(commodity_en, 'attached_assets/stock_images/agricultural_market__f7641e9d.jpg')
                
                col_a, col_b = st.columns([4, 1])
                
                with col_a:
                    st.markdown(f"""
                    <div class="price-card">
                        <img src="app/{commodity_img}" alt="{commodity_en}">
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
                    
                    if st.button("⭐" if is_favorite else "☆", key=fav_key, use_container_width=True):
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
    st.markdown("""
    <div class="green-header">
        <h1>📊 Dashboard</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">All Favorite Mandi at One Place</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⭐ Your Favorites")
    
    if len(st.session_state.favorites) == 0:
        st.info("No favorites yet! Add commodities from the home tab.")
        
        st.markdown(f"""
        <div class="price-card">
            <img src="app/attached_assets/stock_images/indian_fruits_apples_d5558a79.jpg" alt="Mustard">
            <div class="price-info">
                <h3>Mustard</h3>
                <p>सरसों</p>
                <p style="color: #757575 !important;">Alwar ● ₹6100 - 6925 / Q</p>
            </div>
            <div class="price-value">₹6100</div>
        </div>
        
        <div class="price-card">
            <img src="app/attached_assets/stock_images/fresh_indian_vegetab_fc6a58ec.jpg" alt="Dhaincha">
            <div class="price-info">
                <h3>Dhaincha</h3>
                <p>ढैंचा</p>
                <p style="color: #757575 !important;">Alwar ● ₹3675 - 3675 / Q</p>
            </div>
            <div class="price-value">₹3675</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for fav in st.session_state.favorites:
            st.markdown(f"""
            <div class="price-card">
                <img src="app/{fav.get('image', 'attached_assets/stock_images/agricultural_market__f7641e9d.jpg')}" alt="{fav['name']}">
                <div class="price-info">
                    <h3>{fav['name']}</h3>
                    <p>{fav.get('name_hi', '')}</p>
                    <p style="color: #757575 !important;">{fav.get('location', '')} ● ₹{fav['price']:.0f}</p>
                </div>
                <div class="price-value">₹{fav['price']:.0f}</div>
            </div>
            """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Alwar(FV)", use_container_width=True):
            st.toast("Filtering for Alwar(FV)")
    with col2:
        if st.button("Alwar", use_container_width=True):
            st.toast("Filtering for Alwar")
    
    st.markdown("### 📰 News")
    st.markdown("#### Agricultural & Market Updates")
    
    news_items = [
        {
            "title": "भेड़ पालन कैसे शुरू करें...",
            "subtitle": "खेती के साथ साथ कई तरह के काम किये जिन्हे...",
            "image": "attached_assets/stock_images/agricultural_market__f7641e9d.jpg"
        },
        {
            "title": "बरसीम की खेती कैसे करें...",
            "subtitle": "बरसीम की खेती तो सारे देश के रूप में की जाती है...",
            "image": "attached_assets/stock_images/agricultural_market__f7641e9d.jpg"
        }
    ]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="cursor: pointer;">
            <img src="app/{news_items[0]['image']}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 8px; margin-bottom: 8px;">
            <h4 style="color: #2E7D32 !important; font-size: 14px !important; font-weight: 500 !important;">{news_items[0]['title']}</h4>
            <p style="font-size: 12px; margin: 0;">{news_items[0]['subtitle']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="cursor: pointer;">
            <img src="app/{news_items[1]['image']}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 8px; margin-bottom: 8px;">
            <h4 style="color: #2E7D32 !important; font-size: 14px !important; font-weight: 500 !important;">{news_items[1]['title']}</h4>
            <p style="font-size: 12px; margin: 0;">{news_items[1]['subtitle']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🎥 Videos")
    st.markdown("#### Farming Tips & Tutorials")
    
    st.info("🎬 Video tutorials coming soon! Watch expert farming techniques, market insights, and crop management tips.")

def render_markets():
    st.markdown("""
    <div class="green-header">
        <h1>🏪 Your Mandi Bhav</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">आपकी मंडी के सभी भाव</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### Ch. Dadri Mandi Bhav")
    
    sample_prices = [
        {"name": "Banana", "name_hi": "केला", "price": 2500, "img": "indian_fruits_apples_2da2d798.jpg"},
        {"name": "Green Chilli", "name_hi": "हरी मिर्च", "price": 2300, "img": "fresh_indian_vegetab_9663b242.jpg"},
        {"name": "Cucumber", "name_hi": "खीरा", "price": 1800, "img": "fresh_indian_vegetab_fc6a58ec.jpg"},
        {"name": "Tomato", "name_hi": "टमाटर", "price": 1500, "img": "fresh_indian_vegetab_9663b242.jpg"},
        {"name": "Apple", "name_hi": "सेब", "price": 4000, "img": "indian_fruits_apples_5c94b2a3.jpg"},
        {"name": "Pomegranate", "name_hi": "अनार", "price": 5000, "img": "indian_fruits_apples_eb181843.jpg"},
        {"name": "Cauliflower", "name_hi": "फूलगोभी", "price": 1200, "img": "fresh_indian_vegetab_37b1c21e.jpg"}
    ]
    
    for item in sample_prices:
        st.markdown(f"""
        <div class="price-card">
            <img src="app/attached_assets/stock_images/{item['img']}" alt="{item['name']}">
            <div class="price-info">
                <h3>{item['name']}</h3>
                <p>{item['name_hi']}</p>
            </div>
            <div style="text-align: right;">
                <div class="price-value">₹ {item['price']}</div>
                <span class="freshness-badge">● Today</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 🔍 Search All Mandi")
    st.markdown("#### मंडी खोजने")
    
    search_query = st.text_input("Search for commodity...", placeholder="neem", label_visibility="collapsed")
    
    if search_query:
        st.markdown(f"""
        <div class="price-card">
            <div class="price-info">
                <h3>Neemuch</h3>
                <span class="freshness-badge">2 days ago</span>
            </div>
        </div>
        
        <div class="price-card">
            <div class="price-info">
                <h3>Neem Ka Thana</h3>
                <span class="freshness-badge">● Today</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card" style="background: #E8F5E9; border-left: 4px solid #4CAF50;">
        <h4 style="color: #2E7D32 !important; font-size: 14px !important; margin-bottom: 8px;">🎤 Voice Search Feature</h4>
        <p style="font-size: 13px; margin: 0;">For hands-free operation, farmers can use their device's built-in voice input:</p>
        <ul style="font-size: 12px; margin: 8px 0 0 0; padding-left: 20px;">
            <li>On Android: Tap the microphone icon on your keyboard</li>
            <li>On iPhone: Tap the microphone icon next to spacebar</li>
            <li>Speak clearly in your preferred language (Hindi, Gujarati, etc.)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

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
        <h1>🌾 Select Commodity</h1>
        <p style="color: white !important; margin: 0; font-size: 14px;">वस्तु चुने</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Grains • अनाज")
    
    grains = [
        {"name": "Bajra", "name_hi": "बाजरा", "img": "indian_grains_wheat__6b7e9189.jpg"},
        {"name": "Bengal Gram", "name_hi": "चना", "img": "indian_grains_wheat__6a7e6f6d.jpg"},
        {"name": "Cotton", "name_hi": "कपास", "img": "indian_grains_wheat__827f1eb9.jpg"},
        {"name": "Dhaincha", "name_hi": "ढैंचा", "img": "fresh_indian_vegetab_fc6a58ec.jpg"},
        {"name": "Mustard", "name_hi": "सरसों", "img": "indian_grains_wheat__54064495.jpg"},
        {"name": "Til", "name_hi": "तिल", "img": "indian_grains_wheat__0e9ca628.jpg"},
        {"name": "Wheat", "name_hi": "गेहूं", "img": "indian_grains_wheat__6b7e9189.jpg"},
        {"name": "Barley", "name_hi": "जौ", "img": "indian_grains_wheat__827f1eb9.jpg"},
        {"name": "Maize", "name_hi": "मक्का", "img": "indian_grains_wheat__6b7e9189.jpg"},
        {"name": "Guar Seeds", "name_hi": "ग्वार", "img": "indian_grains_wheat__54064495.jpg"},
        {"name": "Tur/Red Gram", "name_hi": "तूर", "img": "indian_grains_wheat__0e9ca628.jpg"},
        {"name": "Sorghum", "name_hi": "ज्वार", "img": "indian_grains_wheat__827f1eb9.jpg"}
    ]
    
    cols = st.columns(3)
    for idx, grain in enumerate(grains):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="commodity-item" style="margin-bottom: 12px;">
                <img src="app/attached_assets/stock_images/{grain['img']}" alt="{grain['name']}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 8px;">
                <div class="commodity-name" style="font-size: 13px; font-weight: 500; color: #2E7D32 !important;">{grain['name']}</div>
                <div class="commodity-name" style="font-size: 11px; color: #757575 !important;">{grain['name_hi']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select", key=f"grain_{idx}", use_container_width=True):
                st.toast(f"Selected: {grain['name']}")
                st.session_state.current_tab = 'home'
                st.rerun()
    
    st.markdown("### Vegetables • सब्जियां")
    
    vegetables = [
        {"name": "Green Chilli", "name_hi": "हरी मिर्च", "img": "fresh_indian_vegetab_9663b242.jpg"},
        {"name": "Beetroot", "name_hi": "चुकंदर", "img": "fresh_indian_vegetab_f8e5985c.jpg"},
        {"name": "Banana", "name_hi": "केला", "img": "indian_fruits_apples_2da2d798.jpg"},
        {"name": "Tomato", "name_hi": "टमाटर", "img": "fresh_indian_vegetab_9663b242.jpg"},
        {"name": "Onion", "name_hi": "प्याज", "img": "fresh_indian_vegetab_f8e5985c.jpg"},
        {"name": "Potato", "name_hi": "आलू", "img": "fresh_indian_vegetab_7839eef3.jpg"}
    ]
    
    cols = st.columns(3)
    for idx, veg in enumerate(vegetables):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="commodity-item" style="margin-bottom: 12px;">
                <img src="app/attached_assets/stock_images/{veg['img']}" alt="{veg['name']}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 8px;">
                <div class="commodity-name" style="font-size: 13px; font-weight: 500; color: #2E7D32 !important;">{veg['name']}</div>
                <div class="commodity-name" style="font-size: 11px; color: #757575 !important;">{veg['name_hi']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select", key=f"veg_{idx}", use_container_width=True):
                st.toast(f"Selected: {veg['name']}")
                st.session_state.current_tab = 'home'
                st.rerun()

tabs = {
    'home': {'icon': '🏠', 'label': 'Home', 'render': render_home},
    'commodities': {'icon': '🔍', 'label': 'Search', 'render': render_commodity_selector},
    'dashboard': {'icon': '📊', 'label': 'Dashboard', 'render': render_trends},
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
    if st.button(f"{tabs['commodities']['icon']}\n{tabs['commodities']['label']}", key="nav_commodities", use_container_width=True, type="primary" if st.session_state.current_tab == 'commodities' else "secondary"):
        st.session_state.current_tab = 'commodities'
        st.rerun()

with col3:
    if st.button(f"{tabs['dashboard']['icon']}\n{tabs['dashboard']['label']}", key="nav_dashboard", use_container_width=True, type="primary" if st.session_state.current_tab == 'dashboard' else "secondary"):
        st.session_state.current_tab = 'dashboard'
        st.rerun()

with col4:
    if st.button(f"{tabs['about']['icon']}\n{tabs['about']['label']}", key="nav_about", use_container_width=True, type="primary" if st.session_state.current_tab == 'about' else "secondary"):
        st.session_state.current_tab = 'about'
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
