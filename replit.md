# Mandli Bhav - Agricultural Market Price Tracker

## Overview

Mandli Bhav is an agricultural market price tracking application designed to provide real-time commodity price information from APMC (Agricultural Produce Market Committee) mandis across India. The application serves farmers, traders, and agricultural stakeholders by offering multilingual support (English and Hindi), interactive visualizations, and location-based market insights.

The system scrapes and aggregates agricultural commodity prices from various mandis, presenting them through an intuitive web interface built with Streamlit. Users can search for prices by state, district, and commodity type, view price trends, and discover nearby market opportunities.

## Recent Changes

**November 17, 2025 - Mobile Redesign & Real API Integration**:
- **Complete UI Redesign**: Transformed from bright website-style to dark-themed Android mobile app
  - Dark theme (#121212 background, #1E1E1E cards) for better readability
  - Mobile-centered layout (480px max-width) for app-like experience
  - Fixed bottom navigation bar with 4 tabs (Home, Trends, Markets, About)
  - Material Design-inspired cards with shadows and rounded corners
  - Category filter buttons with emoji icons
- **Real Data Integration**: Replaced all mock data with live data.gov.in API
  - Integrated official AGMARKNET API for real commodity prices
  - Secure API key storage using Replit secrets (DATA_GOV_IN_API_KEY)
  - Smart categorization system for vegetables, fruits, grains, and pulses
  - Graceful fallback for API errors
- **Enhanced UX**: Query parameter-based navigation, improved color contrast, mobile-first design

**November 17, 2025 - Initial Setup**:
- Installed Python 3.11 and all dependencies (Streamlit, Pandas, Plotly, etc.)
- Created Streamlit configuration to allow all hosts (0.0.0.0) for Replit proxy compatibility
- Configured workflow to run Streamlit app on port 5000
- Set up deployment configuration for production (autoscale)
- Added Python .gitignore file

## User Preferences

Preferred communication style: Simple, everyday language.

## Replit Environment Configuration

**Development Workflow**:
- Workflow name: `streamlit-app`
- Command: `cd MandiTracker && streamlit run app.py --server.port=5000 --server.address=0.0.0.0`
- Port: 5000 (required for Replit webview)
- Output type: webview

**Streamlit Configuration** (MandiTracker/.streamlit/config.toml):
- Server binds to 0.0.0.0:5000 (allows Replit proxy access)
- CORS disabled for development environment
- Headless mode enabled for production deployment

**Deployment**:
- Target: autoscale (stateless web application)
- Run command: `streamlit run MandiTracker/app.py --server.port=5000 --server.address=0.0.0.0`

## System Architecture

### Frontend Architecture

**Framework**: Streamlit  
**Rationale**: Streamlit was chosen for rapid development of data-centric web applications with minimal frontend code. It provides built-in state management, responsive layouts, and seamless integration with Python data science libraries.

**Key Design Decisions**:
- **Wide layout with sidebar**: Maximizes data visualization space while keeping navigation accessible
- **Session state management**: Maintains user selections (language, state, district, price data) across interactions without requiring backend persistence
- **Multilingual support**: Built-in language toggle stored in session state for English/Hindi translations
- **Responsive CSS styling**: Custom styles create an agricultural-themed interface with green gradients and card-based layouts

**Visualization Layer**: Plotly (plotly.express and plotly.graph_objects)  
**Rationale**: Plotly provides interactive, publication-quality charts that work seamlessly with Streamlit. The library supports both simple express charts and complex graph objects for advanced customizations.

### Data Collection Architecture

**Scraping Strategy**: Template-based web scraping with fallback mechanisms  
**Primary Target**: AgMarkNet (government agricultural market data portal)  
**Implementation**: `scraper.py` module with `trafilatura` for content extraction and `BeautifulSoup` for HTML parsing

**Key Design Decisions**:
- **Graceful degradation**: When live scraping fails (network issues, API changes), the system falls back to `generate_sample_data()` to maintain application availability
- **Sample data generation**: Realistic synthetic data mimics actual APMC data structure for development and demonstration purposes
- **Modular scraping functions**: Separated functions for different data operations (scraping, trend generation, nearby mandi discovery)

**Planned Enhancement**: GitHub Actions scheduled scraping for periodic data updates (mentioned in comments but not yet implemented)

### Data Structure and State Management

**Configuration Layer**: `data_config.py` centralizes reference data  
**Contents**:
- `INDIAN_STATES_DISTRICTS`: Hierarchical mapping of Indian states to districts with bilingual names
- `COMMODITY_IMAGES`: Visual assets for different agricultural commodities
- `TRANSLATIONS`: Language resource bundles for UI text

**State Management**: Streamlit session state  
**Tracked State Variables**:
- `language`: User's selected language (English/Hindi)
- `selected_state`: Currently selected state
- `selected_district`: Currently selected district
- `price_data`: Cached commodity price information

**Rationale**: Session state provides stateful behavior in Streamlit's stateless execution model without requiring external databases or caching layers.

### Data Models

**Commodity Data Structure**:
```python
{
    'name_en': str,      # English name
    'name_hi': str,      # Hindi name (Devanagari script)
    'unit': str,         # Measurement unit (typically 'Quintal')
    'base_price': int    # Base price for calculation
}
```

**Price Record Structure** (inferred from scraping logic):
- Commodity identification (name, category)
- Price metrics (min, max, modal/average)
- Market location (mandi, district, state)
- Temporal data (date, trends)
- Volume/quantity information

### Application Flow

1. **Initialization**: Load translations, state/district mappings, and initialize session state
2. **User Input**: Collect state, district, and optional commodity filters via sidebar
3. **Data Retrieval**: Invoke scraper with user parameters (with fallback to sample data)
4. **Data Processing**: Transform scraped data into pandas DataFrames for analysis
5. **Visualization**: Generate Plotly charts showing price distributions, trends, and comparisons
6. **Presentation**: Render results in styled cards and interactive charts

## External Dependencies

### Core Framework Dependencies

- **Streamlit**: Web application framework for data apps
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualization library (express and graph_objects modules)

### Web Scraping Dependencies

- **requests**: HTTP library for fetching web pages
- **BeautifulSoup** (bs4): HTML/XML parsing for web scraping
- **trafilatura**: Web scraping library optimized for extracting main textual content

### Data Sources

- **AgMarkNet** (https://agmarknet.gov.in): Government portal for agricultural market data
  - Primary data source for APMC mandi prices
  - Provides state-wise, district-wise, and commodity-wise price information
  - Currently accessed via template URL pattern with query parameters

### Python Standard Libraries

- **datetime**: Date/time manipulation for time series data and trend analysis
- **random**: Used in sample data generation for realistic price variations

### Potential Future Dependencies

Based on code comments and architectural patterns:
- **Database system**: Not currently implemented, but the architecture would benefit from persistent storage for historical price data
- **GitHub Actions**: Mentioned for scheduled scraping automation
- **Caching layer**: Could improve performance for frequently accessed data
- **Authentication system**: May be needed if user-specific features are added