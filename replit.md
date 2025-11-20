# Mandli Bhav - Agricultural Market Price Tracker

## Overview
Mandli Bhav is an agricultural market price tracking application providing real-time commodity price information from APMC (Agricultural Produce Market Committee) mandis across India. It serves farmers, traders, and agricultural stakeholders with:
- **Real-time APMC prices** from data.gov.in API
- **Multilingual support** (English and Hindi)
- **Historical price tracking** with 30-day trend analysis and line charts
- **AI-powered buy/wait/sell recommendations** based on price trends, volatility, and market position
- **Interactive visualizations** for market analysis
- **Mobile-first design** optimized for farmers in the field

The project uses only real data from the APMC API, providing honest market intelligence to help farmers make better selling decisions.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
**Framework**: Next.js 16 with React 19, TypeScript, and Tailwind CSS for modern, production-ready web application.
**State Management**: Zustand for lightweight, performant global state management.
**Key Design Decisions**:
- **Mobile-first Design**: Fully responsive layout optimized for mobile farmers in the field
- **Multilingual Support**: English and Hindi language toggles throughout the interface
- **Modern UI**: Clean, professional interface with Tailwind CSS styling
- **Theming**: Agricultural-themed design with emerald green accents (#059669, #10b981)
- **Interactive Visualizations**: Real-time price charts and trend analysis
- **Type Safety**: Full TypeScript implementation for reliability
- **Server-Side Rendering**: Next.js App Router for optimal performance

### Data Collection Architecture
**Strategy**: Fetches real agricultural market prices from the data.gov.in APMC API via Next.js API routes.
**Implementation**: `/app/api/scrape-prices/route.ts` handles API integration, commodity categorization, and error handling.
**Key Design Decisions**:
- **Real Data Focus**: The application exclusively displays real data from the APMC API; all mock data disclaimers have been removed.
- **Error Handling**: Robust error handling for API unavailability and network issues.
- **Server-Side Fetching**: API calls made from Next.js backend to avoid CORS issues.

### Historical Price Tracking (NEW)
**Strategy**: Stores historical price data locally using JSON files (Node.js filesystem).
**Implementation**: `/lib/priceHistory.ts` module manages price history storage, retrieval, and trend analysis.
**API Endpoint**: `/api/price-history` provides historical data and AI analysis.
**Features**:
- **30-day price history** automatically collected on each price fetch
- **AI-powered trend analysis** calculating:
  - Price position (percentile in 30-day range)
  - Volatility percentage (market stability indicator)
  - Trend percentage (price movement direction)
- **Smart recommendations**: Buy/Wait/Sell suggestions based on:
  - Current price position in 30-day range
  - Price trend (rising/falling)
  - Market volatility
- **Automatic data collection**: Every API call saves prices to history

**⚠️ Production Migration Required**: 
The current JSON-based storage works for demonstration. For production deployment:
1. Create PostgreSQL database using Replit's built-in PostgreSQL
2. Create schema: `price_history` table with: id, state, district, commodity, date, min_price, max_price, modal_price, created_at
3. Update `/lib/priceHistory.ts` to use a Postgres client (e.g., `@vercel/postgres` or `pg`)
4. Set up daily cron job or scheduled function to collect prices

### Data Structure and State Management
**Configuration**: `/data/states.json` and `/data/translations.json` centralize reference data.
**State Management**: Zustand store in `/lib/store.ts` manages:
  - User language preference (English/Hindi)
  - Selected location (state, district)
  - Price data from API
  - Selected category filter
  - Loading and error states

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

## Competitive Analysis (Nov 2025)

### Feature Gaps Identified vs. Top Competitors
Based on research of top mandi price apps on Google Play:

**Features We Have:**
✅ Real-time APMC prices from official API
✅ Multilingual support (English/Hindi)
✅ Location-based search (State/District)
✅ Category filtering (Vegetables/Fruits/Grains/Pulses)
✅ Historical price trends with line charts (NEW)
✅ AI-powered buy/wait/sell recommendations (NEW)
✅ Favorites system
✅ Mobile-first responsive design

**Features Missing (Future Roadmap):**
- **Price Alerts**: Notifications when prices hit targets
- **Weather Integration**: Forecasts for farming decisions
- **Multi-market Comparison**: Compare prices across nearby mandis
- **Trade News**: Expert analysis and agricultural news
- **Direct Trading/B2B**: Connect buyers and sellers
- **Export/Share**: Share prices via WhatsApp
- **AI Price Predictions**: Forecast future prices using ML
- **Offline Mode**: Cache data for offline access
- **Inventory Management**: For traders

**Our Competitive Advantages:**
1. Clean, modern UI focused on user experience
2. AI-powered recommendations based on historical trends
3. Interactive Plotly charts for better visualization
4. Bilingual interface throughout

## External Dependencies

### Core Framework Dependencies
-   **Streamlit**: Web application framework.
-   **Pandas**: Data manipulation and analysis.
-   **Plotly**: Interactive visualization library (charts and graphs).

### Data Sources
-   **data.gov.in APMC API**: The primary source for real agricultural market prices (Resource ID: 9ef84268-d588-465a-a308-a864a43d0070). The API key is stored in Replit Secrets.

### Python Standard Libraries
-   **datetime**: For date/time manipulation.