from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import statistics

app = Flask(__name__)
CORS(app)

# In-memory price history storage
price_history = []

def calculate_recommendation(commodity, state, district, current_price, min_price, max_price):
    """
    Calculate hold/sell recommendation based on price analysis
    No AI - just statistical analysis
    """
    # Get historical data for this commodity
    history = [p for p in price_history if 
               p['commodity'] == commodity and 
               p['state'] == state and 
               p['district'] == district]
    
    if len(history) < 3:
        # Not enough data for trend analysis
        volatility = ((max_price - min_price) / current_price * 100) if current_price > 0 else 0
        
        if volatility > 30:
            return {
                'action': 'HOLD',
                'confidence': 'LOW',
                'reason': 'High price volatility detected. Wait for market stabilization.',
                'reason_hi': 'उच्च मूल्य अस्थिरता। बाजार स्थिरता की प्रतीक्षा करें।'
            }
        elif current_price > (min_price + max_price) / 2:
            return {
                'action': 'SELL',
                'confidence': 'MEDIUM',
                'reason': 'Price is above market average. Good time to sell.',
                'reason_hi': 'मूल्य बाजार औसत से ऊपर है। बेचने का अच्छा समय।'
            }
        else:
            return {
                'action': 'HOLD',
                'confidence': 'MEDIUM',
                'reason': 'Price below average. Consider holding for better rates.',
                'reason_hi': 'मूल्य औसत से नीचे। बेहतर दरों के लिए प्रतीक्षा करें।'
            }
    
    # Statistical analysis with historical data
    recent_prices = [p['modal_price'] for p in history[-10:]]
    avg_price = statistics.mean(recent_prices)
    
    # Calculate trend (last 5 vs previous 5)
    if len(recent_prices) >= 10:
        recent_avg = statistics.mean(recent_prices[-5:])
        older_avg = statistics.mean(recent_prices[-10:-5])
        trend_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
    else:
        trend_pct = 0
    
    # Calculate volatility
    volatility = (statistics.stdev(recent_prices) / avg_price * 100) if avg_price > 0 else 0
    
    # Price position
    price_percentile = (sum(1 for p in recent_prices if p < current_price) / len(recent_prices) * 100)
    
    # Decision logic
    if price_percentile > 75 and volatility < 20:
        return {
            'action': 'SELL',
            'confidence': 'HIGH',
            'reason': f'Price at {price_percentile:.0f}th percentile with stable market. Good opportunity to sell.',
            'reason_hi': f'मूल्य {price_percentile:.0f}वें प्रतिशतक पर स्थिर बाजार के साथ। बेचने का अच्छा अवसर।',
            'trend_pct': round(trend_pct, 1),
            'volatility': round(volatility, 1),
            'price_percentile': round(price_percentile, 0)
        }
    elif price_percentile > 60 and trend_pct < -5:
        return {
            'action': 'SELL',
            'confidence': 'MEDIUM',
            'reason': 'Prices declining from recent highs. Consider selling now.',
            'reason_hi': 'हाल के उच्चतम स्तर से मूल्य गिर रहे हैं। अब बेचने पर विचार करें।',
            'trend_pct': round(trend_pct, 1),
            'volatility': round(volatility, 1),
            'price_percentile': round(price_percentile, 0)
        }
    elif trend_pct > 10 and price_percentile > 30:
        return {
            'action': 'HOLD',
            'confidence': 'MEDIUM',
            'reason': 'Strong upward trend. Prices may rise further. Hold for better rates.',
            'reason_hi': 'मजबूत ऊपर की प्रवृत्ति। मूल्य और बढ़ सकते हैं। प्रतीक्षा करें।',
            'trend_pct': round(trend_pct, 1),
            'volatility': round(volatility, 1),
            'price_percentile': round(price_percentile, 0)
        }
    elif volatility > 25:
        return {
            'action': 'HOLD',
            'confidence': 'MEDIUM',
            'reason': 'Market highly volatile. Wait for stabilization before selling.',
            'reason_hi': 'बाजार अत्यधिक अस्थिर। बेचने से पहले स्थिरता की प्रतीक्षा करें।',
            'trend_pct': round(trend_pct, 1),
            'volatility': round(volatility, 1),
            'price_percentile': round(price_percentile, 0)
        }
    elif price_percentile < 30:
        return {
            'action': 'HOLD',
            'confidence': 'HIGH',
            'reason': 'Price well below recent average. Hold for better opportunities.',
            'reason_hi': 'मूल्य हाल के औसत से काफी नीचे। बेहतर अवसरों की प्रतीक्षा करें।',
            'trend_pct': round(trend_pct, 1),
            'volatility': round(volatility, 1),
            'price_percentile': round(price_percentile, 0)
        }
    else:
        return {
            'action': 'HOLD',
            'confidence': 'MEDIUM',
            'reason': 'Market conditions neutral. Monitor prices before deciding.',
            'reason_hi': 'बाजार की स्थिति तटस्थ। निर्णय लेने से पहले मूल्यों की निगरानी करें।',
            'trend_pct': round(trend_pct, 1),
            'volatility': round(volatility, 1),
            'price_percentile': round(price_percentile, 0)
        }

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    commodity = data.get('commodity')
    state = data.get('state')
    district = data.get('district')
    current_price = float(data.get('modal_price', 0))
    min_price = float(data.get('min_price', 0))
    max_price = float(data.get('max_price', 0))
    
    recommendation = calculate_recommendation(
        commodity, state, district, current_price, min_price, max_price
    )
    
    return jsonify(recommendation)

@app.route('/api/save-price', methods=['POST'])
def save_price():
    data = request.json
    price_record = {
        'commodity': data.get('commodity'),
        'state': data.get('state'),
        'district': data.get('district'),
        'modal_price': float(data.get('modal_price', 0)),
        'min_price': float(data.get('min_price', 0)),
        'max_price': float(data.get('max_price', 0)),
        'timestamp': datetime.now().isoformat()
    }
    
    price_history.append(price_record)
    
    # Keep only last 1000 records per commodity
    if len(price_history) > 10000:
        price_history.pop(0)
    
    return jsonify({'success': True})

@app.route('/api/price-history', methods=['GET'])
def get_price_history():
    commodity = request.args.get('commodity')
    state = request.args.get('state')
    district = request.args.get('district')
    days = int(request.args.get('days', 30))
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    history = [p for p in price_history if 
               p['commodity'] == commodity and 
               p['state'] == state and 
               p['district'] == district and
               datetime.fromisoformat(p['timestamp']) >= cutoff_date]
    
    return jsonify(history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
