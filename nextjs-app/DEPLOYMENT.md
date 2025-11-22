# Deploying MandiMitra to Vercel

## Simple Deployment (No Database Needed)

Your app already has **173 historical price JSON files** committed to the git repo. These files will work on Vercel!

### How It Works

- **Historical Charts**: ✅ Work perfectly! Shows 30 days of data from git-committed JSON files
- **Real-time Prices**: ✅ Work perfectly! Fetches live data from APMC API
- **New Data Persistence**: ❌ On Vercel, newly fetched prices won't save to history (Vercel's filesystem is read-only)

### Quick Deploy to Vercel

1. **Connect your GitHub repo** to Vercel
2. **Set environment variable**:
   - `APMC_API_KEY`: Your data.gov.in API key (optional, has fallback)
3. **Deploy** - that's it!

Your charts will show historical data from the JSON files in your repo. Users can see price trends and AI recommendations based on the existing 30-day history.

---

## Advanced: Full Persistence with Database (Optional)

If you want newly fetched prices to persist on Vercel, add a PostgreSQL database:

### Option 1: Vercel Postgres (Recommended)

1. In Vercel dashboard → Storage → Create Database → Postgres
2. Vercel auto-adds `POSTGRES_URL` environment variable
3. After deploying, visit `/api/init-db` to create tables
4. Done! New prices now persist between deployments

### Option 2: External Database

1. Create PostgreSQL database (Neon, Supabase, Railway, etc.)
2. Add `DATABASE_URL` environment variable in Vercel
3. Visit `/api/init-db` after deployment
4. Done!

### How Hybrid Storage Works

The app intelligently chooses storage:
- **If database exists**: Saves and reads from PostgreSQL ✅ Full persistence
- **If no database**: Reads from JSON files in git ✅ Works great for display

---

## Recommended Approach for Most Users

**Start simple**: Deploy without database - charts work great with git-committed JSON files!

**Upgrade later**: Add database only if you need long-term persistence of newly collected data.

---

## Keeping Historical Data Fresh (Optional)

If you want to update the JSON files with fresh data:

### On Replit (Development):
1. Run the app and check various commodities
2. New price data automatically saves to JSON files
3. Commit and push updated JSON files to git
4. Redeploy to Vercel

This way, your Vercel deployment always has recent historical data!

### Automation Idea:
- Set up a daily scheduled job on Replit
- Fetch popular commodities automatically
- Auto-commit updated JSON files
- Vercel auto-deploys on new git commits

---

## Testing Your Deployment

After deploying to Vercel:

1. ✅ Select a state and district
2. ✅ View commodity prices (should load from APMC API)
3. ✅ Click on a commodity detail
4. ✅ Check if price history chart displays (should show data from JSON files)
5. ✅ Verify AI recommendations appear

All core features work without a database!
