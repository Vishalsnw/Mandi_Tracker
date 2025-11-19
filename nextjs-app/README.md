# Mandi Bhav - मंडी भाव

A Next.js application that provides real-time market prices for agricultural commodities across India from APMC mandis.

## Features

- 🌾 Real-time APMC mandi prices from data.gov.in
- 🗺️ Location-based price search (State & District)
- 📊 Price analysis with volatility indicators
- 🌐 Bilingual support (English & Hindi)
- 📱 Mobile-responsive design
- 🎨 Modern UI with Tailwind CSS

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **API**: Data.gov.in APMC API
- **Deployment**: Optimized for Vercel

## Getting Started

### Prerequisites

- Node.js 20+ installed
- Data.gov.in API key ([Get one here](https://data.gov.in/))

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file in the root directory:
   ```env
   DATA_GOV_API_KEY=your_api_key_here
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:5000](http://localhost:5000) in your browser

## Deployment to Vercel

### Steps:

1. **Push to GitHub**: Ensure your code is in a GitHub repository

2. **Import to Vercel**: 
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository

3. **Configure Environment Variable**:
   - In Vercel dashboard, go to Project Settings → Environment Variables
   - Add: `DATA_GOV_API_KEY` = `your_api_key_here`

4. **Deploy**: Click "Deploy" - Vercel will automatically build and deploy your app!

### Vercel Settings (Framework Preset)

When deploying to Vercel, use these settings:

- **Framework Preset**: Next.js
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `.next` (auto-detected)
- **Install Command**: `npm install` (auto-detected)
- **Root Directory**: Leave empty OR set to `nextjs-app` if deploying from parent directory

The project includes a `vercel.json` file with optimized settings for Indian deployment (Mumbai region).

## Project Structure

```
nextjs-app/
├── app/
│   ├── api/
│   │   └── scrape-prices/   # API route for fetching APMC data
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Main page
├── components/
│   ├── OnboardingScreen.tsx # Location selection screen
│   └── PriceDisplay.tsx     # Price display with filters
├── data/
│   ├── states.json          # State and district data
│   └── translations.json    # Bilingual translations
├── lib/
│   └── store.ts             # Zustand state management
└── vercel.json              # Vercel deployment config
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATA_GOV_API_KEY` | API key from data.gov.in | Yes |

## API Routes

### GET /api/scrape-prices

Fetches APMC market prices from data.gov.in

**Query Parameters:**
- `state` (optional): State name
- `district` (optional): District name  
- `commodity` (optional): Commodity name

**Response:**
```json
{
  "success": true,
  "data": [...],
  "count": 150
}
```

## Features in Detail

### 1. Onboarding Screen
- Select state and district
- Language switcher (English/Hindi)
- Clean, mobile-friendly interface

### 2. Price Display
- Real-time commodity prices
- Category filters (Vegetables, Fruits, Grains, Pulses)
- Price volatility indicators
- Min, Max, and Modal prices
- Market information

### 3. Bilingual Support
- Complete UI translation
- English and Hindi languages
- State and district names in both languages

## License

This project is licensed under the MIT License.

## Acknowledgments

- Data source: [data.gov.in](https://data.gov.in/) - Government of India Open Data Portal
- Built with ❤️ for Indian farmers
