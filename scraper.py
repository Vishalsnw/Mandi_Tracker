import requests
import pandas as pd
from datetime import datetime
import os

def categorize_commodity(commodity_name):
    """
    Categorize commodity into vegetables, fruits, grains, or pulses.
    """
    commodity_lower = commodity_name.lower()
    
    vegetables = ['tomato', 'onion', 'potato', 'cabbage', 'cauliflower', 'carrot', 'brinjal', 
                  'chilli', 'pepper', 'capsicum', 'cucumber', 'pumpkin', 'gourd', 'radish',
                  'beetroot', 'spinach', 'coriander', 'ginger', 'garlic', 'ladyfinger', 'okra']
    
    fruits = ['apple', 'mango', 'banana', 'orange', 'grapes', 'pomegranate', 'papaya', 
              'watermelon', 'muskmelon', 'guava', 'pineapple', 'lemon', 'lime', 'coconut']
    
    grains = ['wheat', 'rice', 'maize', 'bajra', 'jowar', 'ragi', 'barley', 'paddy']
    
    pulses = ['tur', 'moong', 'urad', 'chana', 'masoor', 'dal', 'peas', 'gram', 'lentil', 'arhar']
    
    for veg in vegetables:
        if veg in commodity_lower:
            return 'vegetables'
    
    for fruit in fruits:
        if fruit in commodity_lower:
            return 'fruits'
    
    for grain in grains:
        if grain in commodity_lower:
            return 'grains'
    
    for pulse in pulses:
        if pulse in commodity_lower:
            return 'pulses'
    
    return 'vegetables'

def scrape_apmc_data(state, district, commodity=None):
    """
    Fetch real APMC mandi price data from data.gov.in API.
    Returns empty DataFrame if API fails or no data found.
    """
    api_key = os.environ.get('DATA_GOV_API_KEY')
    
    if not api_key:
        print("ERROR: API key not found. Please set DATA_GOV_API_KEY environment variable.")
        return pd.DataFrame()
    
    try:
        resource_id = "9ef84268-d588-465a-a308-a864a43d0070"
        base_url = f"https://api.data.gov.in/resource/{resource_id}"
        
        params = {
            'api-key': api_key,
            'format': 'json',
            'offset': 0,
            'limit': 100
        }
        
        print(f"Fetching latest mandi prices from API...")
        response = requests.get(base_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            if not records:
                print(f"No records found in API")
                return pd.DataFrame()
            
            processed_data = []
            for record in records:
                rec_state = record.get('state', '')
                rec_district = record.get('district', '')
                commodity_name = record.get('commodity', 'Unknown')
                
                if state and state.lower() not in rec_state.lower():
                    continue
                    
                if district and district.lower() not in rec_district.lower():
                    continue
                
                if commodity and commodity.lower() not in commodity_name.lower():
                    continue
                
                category = categorize_commodity(commodity_name)
                
                try:
                    min_p = float(record.get('min_price', 0))
                except:
                    min_p = 0
                    
                try:
                    max_p = float(record.get('max_price', 0))
                except:
                    max_p = 0
                    
                try:
                    modal_p = float(record.get('modal_price', 0))
                except:
                    modal_p = 0
                
                processed_data.append({
                    'commodity_en': commodity_name,
                    'commodity_hi': commodity_name,
                    'category': category,
                    'min_price': min_p,
                    'max_price': max_p,
                    'modal_price': modal_p,
                    'unit': 'Quintal',
                    'state': rec_state,
                    'district': rec_district,
                    'arrival_date': record.get('arrival_date', datetime.now().strftime('%d/%m/%Y')),
                    'market': record.get('market', f"{rec_district} Mandi"),
                    'variety': record.get('variety', ''),
                    'grade': record.get('grade', '')
                })
            
            df = pd.DataFrame(processed_data)
            
            if len(df) == 0:
                print(f"No records found for {state} - {district} after filtering")
                print(f"API returned {len(records)} total records")
                available_states = sorted(set(r.get('state', '') for r in records))
                print(f"Available states: {', '.join(available_states[:5])}")
            else:
                print(f"Successfully fetched {len(df)} records matching {state} - {district}")
            
            return df
        else:
            print(f"API request failed with status {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error fetching API data: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
