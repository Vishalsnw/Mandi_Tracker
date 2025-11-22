# Database Setup for MandiMitra

## Problem: Charts Not Loading on Vercel

The price history charts work on Replit but not on Vercel because Vercel's serverless environment has a **read-only filesystem**. The app was originally using local JSON files to store price history data, which doesn't work in production on Vercel.

## Solution: PostgreSQL Database

The app now supports **both file-based storage (for local development) and database storage (for production)**:

- **Local Development (Replit)**: Uses JSON files in `data/price-history/`
- **Production (Vercel)**: Uses PostgreSQL database

## Setting Up Database on Vercel

### Option 1: Vercel Postgres (Recommended)

1. Go to your Vercel project dashboard
2. Navigate to the "Storage" tab
3. Click "Create Database" and select "Postgres"
4. Follow the wizard to create your database
5. Vercel will automatically add the `POSTGRES_URL` environment variable to your project
6. After deploying, visit `https://your-app.vercel.app/api/init-db` to initialize the database tables

### Option 2: External PostgreSQL Database

If you prefer to use an external PostgreSQL provider (like Neon, Supabase, Railway, etc.):

1. Create a PostgreSQL database with your provider
2. Get the connection string (should look like: `postgresql://user:password@host:port/database`)
3. In your Vercel project settings, go to "Environment Variables"
4. Add a new variable:
   - **Name**: `DATABASE_URL`
   - **Value**: Your PostgreSQL connection string
5. Redeploy your application
6. Visit `https://your-app.vercel.app/api/init-db` to initialize the database tables

## Database Schema

The app creates two tables:

### price_history
- Stores historical price data for commodities
- Indexed by state, district, commodity, and date
- Automatically handles duplicate entries (upsert on conflict)

### user_commodity_history
- Tracks which commodities users have checked
- Used for analytics and popular commodity features

## How It Works

The app automatically:
1. Tries to use the database if `DATABASE_URL` or `POSTGRES_URL` is available
2. Falls back to file system storage if no database is configured
3. Uses existing JSON files on Replit for development
4. Stores new data in the database on Vercel

**Performance Optimization**: The app uses connection pooling optimized for serverless:
- Development: Up to 20 concurrent connections
- Production (Vercel): Limited to 1 connection per serverless function to prevent connection exhaustion

## Verifying Setup

After deploying to Vercel with a database:

1. Visit your app
2. Check some commodity prices
3. View the price history charts - they should now load and update
4. Data will persist between deployments and serverless function invocations

## Troubleshooting

**Charts still not loading?**
- Check that the `DATABASE_URL` or `POSTGRES_URL` environment variable is set in Vercel
- Visit `/api/init-db` to ensure tables are created
- Check Vercel function logs for any database connection errors

**Database connection errors?**
- Ensure your connection string is correct
- For production databases, SSL is usually required (automatically handled)
- Check that your database allows connections from Vercel's IP ranges
