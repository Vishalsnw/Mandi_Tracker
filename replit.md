# Mandli Bhav - Agricultural Market Price Tracker

## Overview
Mandli Bhav is an agricultural market price tracking application providing real-time commodity price information from APMC (Agricultural Produce Market Committee) mandis across India. It aims to serve farmers, traders, and agricultural stakeholders with multilingual support (English and Hindi), interactive visualizations, and location-based market insights. The application scrapes and aggregates agricultural commodity prices, presenting them through an intuitive web interface built with Streamlit, enabling users to search prices by state, district, and commodity type, view price trends, and identify market opportunities. The project's ambition is to offer a seamless, mobile-first experience mirroring modern grocery apps, focusing on honest UX with only real data from the APMC API.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
**Framework**: Streamlit is chosen for rapid development, offering built-in state management and responsive layouts.
**Key Design Decisions**:
- **Mobile-first Design**: Optimized for mobile with a "centered" layout and compact UI elements.
- **Multilingual Support**: English and Hindi language toggles.
- **Visuals**: Uses Plotly for interactive charts and custom CSS for an agricultural-themed interface with green gradients and card-based layouts.
- **Theming**: Modern grocery app theme with a vibrant color palette (Fresh Green #0CAF60, Orange #FF6B35).
- **User Experience**: Auto-fetches data on category selection, provides helpful tips on empty screens, and a streamlined detail page for commodities.
- **Readability**: Increased font sizes, high-contrast white-on-green text, and clean HTML/CSS elements for maximum readability.

### Data Collection Architecture
**Strategy**: Fetches real agricultural market prices from the data.gov.in APMC API.
**Implementation**: `scraper.py` module handles API integration, commodity categorization, and error handling.
**Key Design Decisions**:
- **Real Data Focus**: The application exclusively displays real data from the APMC API; all mock data has been removed.
- **Error Handling**: Robust error handling is in place to manage API unavailability.

### Data Structure and State Management
**Configuration**: `data_config.py` centralizes reference data, including `INDIAN_STATES_DISTRICTS`, `COMMODITY_IMAGES`, and `TRANSLATIONS`.
**State Management**: Streamlit's session state is used to persist user selections (language, state, district, price data) across interactions.

### Data Models
- **Commodity Data Structure**: Includes English and Hindi names, unit, and base price.
- **Price Record Structure**: Contains commodity identification, min/max/modal prices, market location, and temporal data.

### Application Flow
1.  **Initialization**: Loads configurations and initializes session state.
2.  **User Input**: Collects state, district, and commodity filters.
3.  **Data Retrieval**: Invokes the scraper with user parameters.
4.  **Data Processing**: Transforms retrieved data into pandas DataFrames.
5.  **Visualization**: Generates Plotly charts for price analysis.
6.  **Presentation**: Renders results in styled cards and interactive charts.

## External Dependencies

### Core Framework Dependencies
-   **Streamlit**: Web application framework.
-   **Pandas**: Data manipulation and analysis.
-   **Plotly**: Interactive visualization library.

### Data Sources
-   **data.gov.in APMC API**: The primary source for real agricultural market prices (Resource ID: 9ef84268-d588-465a-a308-a864a43d0070). The API key is stored in Replit Secrets.

### Python Standard Libraries
-   **datetime**: For date/time manipulation.