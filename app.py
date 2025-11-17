import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from scraper import scrape_apmc_data, generate_price_trends, get_nearby_mandis
from data_config import INDIAN_STATES_DISTRICTS, COMMODITY_IMAGES, TRANSLATIONS

st.set_page_config(
    page_title="Mandli Bhav - Agricultural Market Price Tracker",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'selected_state' not in st.session_state:
    st.session_state.selected_state = None
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = None
if 'price_data' not in st.session_state:
    st.session_state.price_data = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'home'

def get_text(key):
    return TRANSLATIONS[st.session_state.language][key]

st.markdown("""
    <style>
    .main {
        background-color: #f5f7f3;
        padding-bottom: 80px;
    }
    .stApp {
        background: linear-gradient(to bottom, #f5f7f3, #e8f5e9);
    }
    h1 {
        color: #2e7d32;
        font-weight: 700;
    }
    h2, h3 {
        color: #388e3c;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #ff9800;
    }
    .commodity-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-left: 3px solid #4caf50;
    }
    .price-high {
        color: #f44336;
        font-weight: bold;
    }
    .price-low {
        color: #4caf50;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #4caf50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 10px 25px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-around;
        padding: 10px 0;
        z-index: 999;
        border-top: 2px solid #4caf50;
    }
    .nav-item {
        flex: 1;
        text-align: center;
        padding: 8px;
        cursor: pointer;
        color: #666;
        text-decoration: none;
        transition: all 0.3s;
    }
    .nav-item:hover {
        background-color: #f0f0f0;
        color: #4caf50;
    }
    .nav-item.active {
        color: #4caf50;
        font-weight: bold;
    }
    .nav-icon {
        font-size: 24px;
        display: block;
    }
    .nav-label {
        font-size: 12px;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

st.title(get_text('app_title'))
st.markdown(f"### {get_text('tagline')}")
st.markdown("---")

col_lang, col_empty = st.columns([1, 3])
with col_lang:
    language = st.selectbox(
        get_text('select_language'),
        options=['en', 'hi'],
        format_func=lambda x: 'English' if x == 'en' else 'हिंदी',
        index=0 if st.session_state.language == 'en' else 1
    )
    if language != st.session_state.language:
        st.session_state.language = language
        st.rerun()

with st.sidebar:
    st.header("🔍 " + get_text('search_prices'))
    
    state_options = list(INDIAN_STATES_DISTRICTS.keys())
    if st.session_state.language == 'hi':
        state_display = [f"{state} ({INDIAN_STATES_DISTRICTS[state]['name_hi']})" for state in state_options]
    else:
        state_display = state_options
    
    selected_state_display = st.selectbox(
        get_text('select_state'),
        options=state_display,
        index=state_display.index(st.session_state.selected_state) if st.session_state.selected_state in state_display else 0
    )
    
    selected_state = state_options[state_display.index(selected_state_display)]
    
    district_options = INDIAN_STATES_DISTRICTS[selected_state]['districts']
    
    if isinstance(district_options[0], dict):
        if st.session_state.language == 'hi':
            district_display = [d['hi'] for d in district_options]
            district_keys = [d['en'] for d in district_options]
        else:
            district_display = [d['en'] for d in district_options]
            district_keys = [d['en'] for d in district_options]
        
        selected_district_display = st.selectbox(
            get_text('select_district'),
            options=district_display
        )
        selected_district = district_keys[district_display.index(selected_district_display)]
    else:
        if st.session_state.language == 'hi':
            district_display = [f"{district} (जिला)" for district in district_options]
            selected_district_display = st.selectbox(
                get_text('select_district'),
                options=district_display
            )
            selected_district = district_options[district_display.index(selected_district_display)]
        else:
            selected_district = st.selectbox(
                get_text('select_district'),
                options=district_options
            )
    
    if st.button("🔍 " + get_text('search_prices'), use_container_width=True):
        st.session_state.selected_state = selected_state_display
        st.session_state.selected_district = selected_district
        with st.spinner(get_text('fetching_prices')):
            st.session_state.price_data = scrape_apmc_data(selected_state, selected_district)
    
    st.markdown("---")
    
    category_filter = st.radio(
        get_text('filter_category'),
        options=['all', 'vegetables', 'fruits', 'grains', 'pulses'],
        format_func=lambda x: get_text('all_categories') if x == 'all' else get_text(x)
    )

if st.session_state.price_data is not None and not st.session_state.price_data.empty:
    df = st.session_state.price_data
    
    if category_filter != 'all':
        df = df[df['category'] == category_filter]
    
    if len(df) == 0:
        st.warning("No commodities found in this category. Please select a different category or search for a different location.")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{get_text('total_commodities')}</h4>
                <h2>{len(df)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_price = df['modal_price'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h4>{get_text('avg_price')}</h4>
                <h2>₹{avg_price:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            price_range = f"₹{df['min_price'].min():.0f} - ₹{df['max_price'].max():.0f}"
            st.markdown(f"""
            <div class="metric-card">
                <h4>{get_text('price_range')}</h4>
                <h2>{price_range}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📊 " + get_text('commodity') + " " + get_text('modal_price'))
        top_commodities = df.nlargest(min(10, len(df)), 'modal_price')
        
        if st.session_state.language == 'hi':
            commodity_names = top_commodities['commodity_hi'].tolist()
        else:
            commodity_names = top_commodities['commodity_en'].tolist()
        
        fig = go.Figure(data=[
            go.Bar(
                y=commodity_names,
                x=top_commodities['modal_price'],
                orientation='h',
                marker=dict(
                    color=top_commodities['modal_price'],
                    colorscale='Greens',
                    showscale=True
                ),
                text=top_commodities['modal_price'].apply(lambda x: f'₹{x:.2f}'),
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f"{get_text('top_10_commodities')} {get_text('commodity')} {get_text('by')} {get_text('modal_price')}",
            xaxis_title=get_text('modal_price') + " (₹)",
            yaxis_title=get_text('commodity'),
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📋 " + get_text('detailed_price_table'))
        
        display_df = df.copy()
        
        if st.session_state.language == 'hi':
            display_df = display_df[[
                'commodity_hi', 'min_price', 'max_price', 'modal_price', 'unit', 'market', 'arrival_date'
            ]]
            display_df.columns = [
                get_text('commodity'),
                get_text('min_price'),
                get_text('max_price'),
                get_text('modal_price'),
                get_text('unit'),
                get_text('market'),
                get_text('date')
            ]
        else:
            display_df = display_df[[
                'commodity_en', 'min_price', 'max_price', 'modal_price', 'unit', 'market', 'arrival_date'
            ]]
            display_df.columns = [
                get_text('commodity'),
                get_text('min_price'),
                get_text('max_price'),
                get_text('modal_price'),
                get_text('unit'),
                get_text('market'),
                get_text('date')
            ]
        
        st.dataframe(
            display_df.style.format({
                get_text('min_price'): '₹{:.2f}',
                get_text('max_price'): '₹{:.2f}',
                get_text('modal_price'): '₹{:.2f}'
            }).background_gradient(subset=[get_text('modal_price')], cmap='Greens'),
            use_container_width=True,
            height=400
        )
        
        st.markdown("---")
        
        col_trend1, col_trend2 = st.columns([1, 2])
        
        with col_trend1:
            st.markdown("### 📈 " + get_text('price_trends'))
            st.markdown(get_text('select_commodity'))
        
            if st.session_state.language == 'hi':
                commodity_options = df[['commodity_en', 'commodity_hi']].drop_duplicates().values.tolist()
                commodity_display = [f"{row[1]} ({row[0]})" for row in commodity_options]
                selected_commodity_display = st.selectbox(
                    get_text('commodity'),
                    options=commodity_display,
                    label_visibility='collapsed'
                )
                selected_commodity_index = commodity_display.index(selected_commodity_display)
                selected_commodity = commodity_options[selected_commodity_index][0]
                selected_commodity_name = commodity_options[selected_commodity_index][1]
            else:
                commodity_options = df['commodity_en'].unique().tolist()
                selected_commodity = st.selectbox(
                    get_text('commodity'),
                    options=commodity_options,
                    label_visibility='collapsed'
                )
                selected_commodity_name = selected_commodity
        
        with col_trend2:
            if selected_commodity:
                trend_data = generate_price_trends(selected_commodity, days=7)
            
                fig_trend = px.line(
                    trend_data,
                    x='date',
                    y='price',
                    title=f"{get_text('last_7_days')} - {selected_commodity_name}",
                    markers=True
                )
            
                fig_trend.update_traces(
                    line_color='#4caf50',
                    line_width=3,
                    marker=dict(size=8, color='#ff9800')
                )
            
                fig_trend.update_layout(
                    xaxis_title=get_text('date'),
                    yaxis_title=get_text('modal_price') + " (₹)",
                    hovermode='x unified'
                )
            
                st.plotly_chart(fig_trend, use_container_width=True)
            
                commodity_image = COMMODITY_IMAGES.get(selected_commodity)
                if commodity_image:
                    st.image(commodity_image, caption=selected_commodity_name, use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### 🏪 " + get_text('nearby_mandis'))
        
        nearby_mandis = get_nearby_mandis(selected_state, st.session_state.selected_district)
        
        nearby_df = nearby_mandis.copy()
        nearby_df.columns = [
            get_text('mandi_name'),
            get_text('distance'),
            get_text('facilities')
        ]
        
        st.dataframe(nearby_df, use_container_width=True)

else:
    st.info("👈 " + ("कृपया प्रारंभ करने के लिए एक राज्य और जिला चुनें" if st.session_state.language == 'hi' else "Please select a state and district from the sidebar to get started"))
    
    st.markdown("---")
    st.markdown("### 🌾 " + get_text('about_mandli_bhav'))
    
    col_about1, col_about2 = st.columns(2)
    
    with col_about1:
        st.image("attached_assets/stock_images/agricultural_market__f7641e9d.jpg", use_container_width=True)
        
        if st.session_state.language == 'hi':
            st.markdown("""
            **मंडली भाव** एक व्यापक कृषि बाजार मूल्य ट्रैकर है जो किसानों को सूचित निर्णय लेने में मदद करता है।
            
            **विशेषताएं:**
            - 🇮🇳 सभी भारतीय राज्यों और जिलों को कवर करता है
            - 🌾 सब्जियां, फल, अनाज और दालों की कीमतें
            - 📊 मूल्य रुझान विश्लेषण
            - 🏪 आस-पास की मंडी जानकारी
            - 🌐 द्विभाषी समर्थन (हिंदी/अंग्रेजी)
            """)
        else:
            st.markdown("""
            **Mandli Bhav** is a comprehensive agricultural market price tracker designed to help farmers make informed decisions.
            
            **Features:**
            - 🇮🇳 Covers all Indian states and districts
            - 🌾 Prices for vegetables, fruits, grains, and pulses
            - 📊 Price trend analysis
            - 🏪 Nearby mandi information
            - 🌐 Bilingual support (Hindi/English)
            """)
    
    with col_about2:
        st.image("attached_assets/stock_images/agricultural_market__0dc6c3a3.jpg", use_container_width=True)
        
        if st.session_state.language == 'hi':
            st.markdown("""
            **उत्पादन तैनाती के लिए:**
            
            1. GitHub Actions का उपयोग करके scraper.py को शेड्यूल करें
            2. वास्तविक APMC पोर्टल डेटा प्राप्त करें
            3. PostgreSQL डेटाबेस में मूल्य संग्रहीत करें
            4. ऐतिहासिक रुझान विश्लेषण जोड़ें
            5. मूल्य अलर्ट सेटअप करें
            """)
        else:
            st.markdown("""
            **For Production Deployment:**
            
            1. Schedule scraper.py using GitHub Actions
            2. Fetch real APMC portal data
            3. Store prices in PostgreSQL database
            4. Add historical trend analysis
            5. Setup price alerts
            """)

st.markdown("---")
st.info(get_text('disclaimer'))
st.success(get_text('github_info'))

st.markdown(f"""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🌾 {get_text('made_for_farmers')}</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    if st.button("🏠\n\nHome", key="nav_home", use_container_width=True):
        st.session_state.current_tab = 'home'
        st.rerun()

with nav_col2:
    if st.button("📈\n\nTrends", key="nav_trends", use_container_width=True):
        st.session_state.current_tab = 'trends'
        st.rerun()

with nav_col3:
    if st.button("🏪\n\nMarkets", key="nav_markets", use_container_width=True):
        st.session_state.current_tab = 'markets'
        st.rerun()

with nav_col4:
    if st.button("ℹ️\n\nAbout", key="nav_about", use_container_width=True):
        st.session_state.current_tab = 'about'
        st.rerun()

st.markdown(f"""
    <div class="bottom-nav" style="text-align: center; padding: 10px; background: white; box-shadow: 0 -2px 10px rgba(0,0,0,0.1);">
        <small style="color: #666;">Current tab: {st.session_state.current_tab.title()}</small>
    </div>
""", unsafe_allow_html=True)
