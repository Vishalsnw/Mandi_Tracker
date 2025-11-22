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

**Data Availability by Location** (November 2025):
- Data availability varies significantly by district in the government APMC database
- Some districts have abundant data (e.g., Maharashtra Pune: 72 commodities)
- Others have limited data (e.g., Maharashtra Jalgaon: 1 commodity, Punjab Bathinda: 0 commodities)
- The app now displays an informative message when limited data is available, suggesting users try larger districts
- This is a characteristic of the real government data source, not an application limitation

### Historical Price Tracking (UPDATED November 2025)
**Strategy**: Hybrid storage system - PostgreSQL database (production) with JSON file fallback (development/backup).
**Implementation**: `/lib/priceHistory.ts` module manages price history with intelligent storage detection.
**API Endpoint**: `/api/price-history` provides historical data and AI analysis.
**Features**:
- **30-day price history** automatically collected on each price fetch
- **173 pre-populated JSON files** with historical data committed to git
- **AI-powered trend analysis** calculating:
  - Price position (percentile in 30-day range)
  - Volatility percentage (market stability indicator)
  - Trend percentage (price movement direction)
- **Smart recommendations**: Buy/Wait/Sell suggestions based on:
  - Current price position in 30-day range
  - Price trend (rising/falling)
  - Market volatility
- **Automatic data collection**: Every API call saves prices to history

**✅ Production Deployment (Vercel)**: 
The app now supports **two deployment modes**:

**Mode 1: Simple Deployment (No Database)**
- Charts display historical data from 173 git-committed JSON files
- Real-time prices fetch perfectly from APMC API
- New data doesn't persist (Vercel filesystem is read-only)
- ✅ Perfect for most use cases - no database setup needed!

**Mode 2: Full Persistence (With Database)**
- Add PostgreSQL database (Vercel Postgres, Neon, Supabase, etc.)
- Set `DATABASE_URL` or `POSTGRES_URL` environment variable
- Visit `/api/init-db` to create tables
- ✅ New prices persist between deployments
- Falls back to JSON files if database unavailable

**Storage Priority**: Database (if configured) → JSON files (always available)

### User Commodity History Tracking (UPDATED November 2025)
**Strategy**: Hybrid storage - PostgreSQL database with JSON file fallback.
**Implementation**: `/lib/userHistory.ts` module with intelligent storage detection.
**API Endpoint**: `/api/user-history` provides history access and statistics.
**Features**:
- **Automatic tracking**: Every commodity detail view is saved to history
- **Usage statistics**: Commodity check frequency and popular items
- **Last 500 checks**: History automatically trimmed in file mode

**Production Behavior**:
- **With database**: Full persistence of user interaction history
- **Without database**: Tracking disabled (no persistence on Vercel's read-only filesystem)

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
1.  **Initialization**: Next.js loads the app with client-side state management (Zustand)
2.  **User Input**: Onboarding screen collects state and district selection
3.  **Data Retrieval**: Frontend calls `/api/scrape-prices` endpoint to fetch APMC data
4.  **Data Processing**: API route fetches, categorizes, and adds Hindi translations to commodity data
5.  **Visualization**: Frontend renders price cards with Recharts visualizations
6.  **Presentation**: Results displayed in responsive, mobile-optimized interface with filtering and search

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
✅ User commodity history tracking (NEW)
✅ WhatsApp sharing with Web Share API fallback (NEW)
✅ Favorites system
✅ Mobile-first responsive design

**Features Missing (Future Roadmap):**
- **Price Alerts**: Notifications when prices hit targets
- **Weather Integration**: Forecasts for farming decisions
- **Multi-market Comparison**: Compare prices across nearby mandis
- **Trade News**: Expert analysis and agricultural news
- **Direct Trading/B2B**: Connect buyers and sellers
- **AI Price Predictions**: Forecast future prices using ML
- **Offline Mode**: Cache data for offline access
- **Inventory Management**: For traders

**Our Competitive Advantages:**
1. Clean, modern UI focused on user experience
2. AI-powered recommendations based on historical trends
3. Interactive Plotly charts for better visualization
4. Bilingual interface throughout

## Recent Changes (November 2025)

### Migration from Streamlit to Next.js
- **Removed**: Streamlit, pandas, plotly Python dependencies
- **Architecture**: Pure Next.js application with TypeScript
- **Created Library Files**:
  - `/lib/store.ts`: Zustand state management store
  - `/lib/priceHistory.ts`: Price history management with filesystem operations
  - `/lib/hindiNames.ts`: Commodity name translation utility (English to Hindi)
- **Production Ready**: Build succeeds, deployment configured for Vercel autoscale
- **Environment Variables**: API key moved to `APMC_API_KEY` environment variable (with fallback)

## External Dependencies

### Core Framework Dependencies
-   **Next.js 16**: React framework with App Router and server-side rendering
-   **React 19**: UI library for building components
-   **TypeScript 5**: Type-safe development
-   **Tailwind CSS 4**: Utility-first CSS framework
-   **Zustand 5**: Lightweight state management
-   **Recharts 3**: Chart visualization library
-   **Axios**: HTTP client for API requests

### Data Sources
-   **data.gov.in APMC API**: The primary source for real agricultural market prices (Resource ID: 9ef84268-d588-465a-a308-a864a43d0070). The API key is configured via `APMC_API_KEY` environment variable.