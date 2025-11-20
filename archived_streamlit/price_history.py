import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from scraper import scrape_apmc_data

HISTORY_DIR = Path("price_history_data")
HISTORY_DIR.mkdir(exist_ok=True)

def get_history_filename(state, district, commodity):
    """Generate filename for historical data"""
    safe_state = state.replace(" ", "_")
    safe_district = district.replace(" ", "_")
    safe_commodity = commodity.replace(" ", "_")
    return HISTORY_DIR / f"{safe_state}_{safe_district}_{safe_commodity}.json"

def save_price_record(state, district, commodity, min_price, max_price, modal_price):
    """Save a single price record to history"""
    filename = get_history_filename(state, district, commodity)
    
    # Load existing history
    history = []
    if filename.exists():
        try:
            with open(filename, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    # Add new record
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Check if record for today already exists
    existing_today = [h for h in history if h['date'] == today]
    if existing_today:
        # Update existing record
        for record in history:
            if record['date'] == today:
                record['min_price'] = min_price
                record['max_price'] = max_price
                record['modal_price'] = modal_price
                record['updated_at'] = datetime.now().isoformat()
    else:
        # Add new record
        history.append({
            'date': today,
            'min_price': min_price,
            'max_price': max_price,
            'modal_price': modal_price,
            'created_at': datetime.now().isoformat()
        })
    
    # Keep only last 90 days
    history = sorted(history, key=lambda x: x['date'], reverse=True)[:90]
    
    # Save back to file
    with open(filename, 'w') as f:
        json.dump(history, f, indent=2)
    
    return history

def collect_and_store_prices(state, district):
    """Collect current prices and store them in history"""
    try:
        df = scrape_apmc_data(state, district)
        
        if df.empty:
            return 0
        
        count = 0
        for _, row in df.iterrows():
            commodity = row.get('commodity_en', 'Unknown')
            min_price = float(row.get('min_price', 0))
            max_price = float(row.get('max_price', 0))
            modal_price = float(row.get('modal_price', 0))
            
            if modal_price > 0:
                save_price_record(state, district, commodity, min_price, max_price, modal_price)
                count += 1
        
        return count
    except Exception as e:
        print(f"Error collecting prices: {e}")
        return 0

def get_price_history(state, district, commodity, days=30):
    """Get historical price data for a commodity"""
    filename = get_history_filename(state, district, commodity)
    
    if not filename.exists():
        return pd.DataFrame()
    
    try:
        with open(filename, 'r') as f:
            history = json.load(f)
        
        if not history:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Filter to requested days
        cutoff_date = datetime.now() - timedelta(days=days)
        df = df[df['date'] >= cutoff_date]
        
        return df
    except Exception as e:
        print(f"Error loading history: {e}")
        return pd.DataFrame()

def analyze_price_trend(history_df):
    """Analyze price trend and return recommendation"""
    if history_df.empty or len(history_df) < 2:
        return {
            'trend': 'insufficient_data',
            'recommendation': '➡️ Monitor market',
            'reason': 'Not enough historical data',
            'color': '#808080'
        }
    
    # Calculate trend metrics
    recent_prices = history_df.tail(7)['modal_price'].values
    older_prices = history_df.head(min(7, len(history_df)))['modal_price'].values
    
    recent_avg = recent_prices.mean() if len(recent_prices) > 0 else 0
    older_avg = older_prices.mean() if len(older_prices) > 0 else recent_avg
    
    current_price = history_df.iloc[-1]['modal_price']
    max_price_30d = history_df['modal_price'].max()
    min_price_30d = history_df['modal_price'].min()
    avg_price_30d = history_df['modal_price'].mean()
    
    # Calculate price position (percentile)
    price_range = max_price_30d - min_price_30d
    if price_range > 0:
        price_percentile = ((current_price - min_price_30d) / price_range) * 100
    else:
        price_percentile = 50
    
    # Calculate volatility
    std_dev = history_df['modal_price'].std()
    volatility_pct = (std_dev / avg_price_30d * 100) if avg_price_30d > 0 else 0
    
    # Calculate trend (percentage change)
    if older_avg > 0:
        trend_pct = ((recent_avg - older_avg) / older_avg) * 100
    else:
        trend_pct = 0
    
    # Determine recommendation
    if price_percentile > 75 and trend_pct < -2:
        # Price is high and declining - SELL
        return {
            'trend': 'declining',
            'recommendation': '✅ Good time to sell',
            'reason': f'Price is {price_percentile:.0f}% of 30-day range and declining',
            'color': '#0CAF60',
            'trend_pct': trend_pct,
            'price_percentile': price_percentile,
            'volatility': volatility_pct
        }
    elif price_percentile > 70 and volatility_pct < 15:
        # Price is high and stable - SELL
        return {
            'trend': 'high_stable',
            'recommendation': '✅ Good time to sell',
            'reason': f'Price is near 30-day high ({price_percentile:.0f}%) and stable',
            'color': '#0CAF60',
            'trend_pct': trend_pct,
            'price_percentile': price_percentile,
            'volatility': volatility_pct
        }
    elif price_percentile < 30 and trend_pct > 2:
        # Price is low and rising - HOLD/BUY
        return {
            'trend': 'rising',
            'recommendation': '⏳ Wait - prices are rising',
            'reason': f'Price is {price_percentile:.0f}% of 30-day range and rising {abs(trend_pct):.1f}%',
            'color': '#FFA500',
            'trend_pct': trend_pct,
            'price_percentile': price_percentile,
            'volatility': volatility_pct
        }
    elif price_percentile < 40:
        # Price is low - WAIT
        return {
            'trend': 'low',
            'recommendation': '⏳ Wait for better prices',
            'reason': f'Price is only {price_percentile:.0f}% of 30-day range',
            'color': '#FFA500',
            'trend_pct': trend_pct,
            'price_percentile': price_percentile,
            'volatility': volatility_pct
        }
    elif volatility_pct > 25:
        # High volatility - CAUTION
        return {
            'trend': 'volatile',
            'recommendation': '⚠️ Market unstable, monitor closely',
            'reason': f'High price volatility ({volatility_pct:.1f}%)',
            'color': '#FF6B35',
            'trend_pct': trend_pct,
            'price_percentile': price_percentile,
            'volatility': volatility_pct
        }
    else:
        # Normal conditions - MONITOR
        return {
            'trend': 'stable',
            'recommendation': '➡️ Monitor market',
            'reason': f'Prices are stable around {price_percentile:.0f}% of range',
            'color': '#808080',
            'trend_pct': trend_pct,
            'price_percentile': price_percentile,
            'volatility': volatility_pct
        }

def generate_mock_history(state, district, commodity, days=30):
    """Generate mock historical data for testing (will be replaced by real data collection)"""
    import random
    
    filename = get_history_filename(state, district, commodity)
    
    # Don't overwrite existing data
    if filename.exists():
        return
    
    history = []
    base_price = random.randint(1000, 5000)
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        
        # Simulate price fluctuation with slight trend
        variation = random.uniform(-0.1, 0.15)
        modal_price = base_price * (1 + variation)
        min_price = modal_price * random.uniform(0.85, 0.95)
        max_price = modal_price * random.uniform(1.05, 1.15)
        
        history.append({
            'date': date,
            'min_price': round(min_price, 2),
            'max_price': round(max_price, 2),
            'modal_price': round(modal_price, 2),
            'created_at': datetime.now().isoformat()
        })
        
        # Slight trend for next day
        base_price = modal_price
    
    with open(filename, 'w') as f:
        json.dump(history, f, indent=2)
