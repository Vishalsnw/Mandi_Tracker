import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import random
import trafilatura

def get_website_text_content(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded)
    return text

def scrape_apmc_data(state, district, commodity=None):
    """
    Scrape APMC mandi price data.
    Note: This is a template function. In production, you would connect to actual APMC portals.
    For GitHub Actions, you would schedule this to run periodically.
    """
    try:
        agmarknet_url = f"https://agmarknet.gov.in/SearchCmmMkt.aspx"
        
        response = requests.get(agmarknet_url, timeout=10)
        
        if response.status_code == 200:
            return generate_sample_data(state, district, commodity)
        else:
            return generate_sample_data(state, district, commodity)
            
    except Exception as e:
        print(f"Error scraping data: {e}")
        return generate_sample_data(state, district, commodity)

def generate_sample_data(state, district, commodity=None):
    """
    Generate realistic sample APMC data for demonstration.
    In production, this would be replaced with actual scraping logic.
    """
    commodities = {
        'vegetables': [
            {'name_en': 'Tomato', 'name_hi': 'टमाटर', 'unit': 'Quintal', 'base_price': 800},
            {'name_en': 'Onion', 'name_hi': 'प्याज', 'unit': 'Quintal', 'base_price': 1200},
            {'name_en': 'Potato', 'name_hi': 'आलू', 'unit': 'Quintal', 'base_price': 900},
            {'name_en': 'Cabbage', 'name_hi': 'पत्तागोभी', 'unit': 'Quintal', 'base_price': 600},
            {'name_en': 'Cauliflower', 'name_hi': 'फूलगोभी', 'unit': 'Quintal', 'base_price': 700},
            {'name_en': 'Carrot', 'name_hi': 'गाजर', 'unit': 'Quintal', 'base_price': 1000},
            {'name_en': 'Brinjal', 'name_hi': 'बैंगन', 'unit': 'Quintal', 'base_price': 850},
            {'name_en': 'Chilli', 'name_hi': 'मिर्च', 'unit': 'Quintal', 'base_price': 3500},
        ],
        'fruits': [
            {'name_en': 'Apple', 'name_hi': 'सेब', 'unit': 'Quintal', 'base_price': 4000},
            {'name_en': 'Mango', 'name_hi': 'आम', 'unit': 'Quintal', 'base_price': 3000},
            {'name_en': 'Banana', 'name_hi': 'केला', 'unit': 'Dozen', 'base_price': 40},
            {'name_en': 'Orange', 'name_hi': 'संतरा', 'unit': 'Quintal', 'base_price': 2500},
            {'name_en': 'Grapes', 'name_hi': 'अंगूर', 'unit': 'Quintal', 'base_price': 3500},
            {'name_en': 'Pomegranate', 'name_hi': 'अनार', 'unit': 'Quintal', 'base_price': 5000},
        ],
        'grains': [
            {'name_en': 'Wheat', 'name_hi': 'गेहूं', 'unit': 'Quintal', 'base_price': 2125},
            {'name_en': 'Rice', 'name_hi': 'चावल', 'unit': 'Quintal', 'base_price': 2500},
            {'name_en': 'Maize', 'name_hi': 'मक्का', 'unit': 'Quintal', 'base_price': 1870},
            {'name_en': 'Bajra', 'name_hi': 'बाजरा', 'unit': 'Quintal', 'base_price': 2350},
            {'name_en': 'Jowar', 'name_hi': 'ज्वार', 'unit': 'Quintal', 'base_price': 3180},
        ],
        'pulses': [
            {'name_en': 'Tur Dal', 'name_hi': 'तुअर दाल', 'unit': 'Quintal', 'base_price': 7000},
            {'name_en': 'Moong Dal', 'name_hi': 'मूंग दाल', 'unit': 'Quintal', 'base_price': 7500},
            {'name_en': 'Urad Dal', 'name_hi': 'उड़द दाल', 'unit': 'Quintal', 'base_price': 6500},
            {'name_en': 'Chana Dal', 'name_hi': 'चना दाल', 'unit': 'Quintal', 'base_price': 5500},
            {'name_en': 'Masoor Dal', 'name_hi': 'मसूर दाल', 'unit': 'Quintal', 'base_price': 6000},
        ]
    }
    
    all_commodities = []
    for category, items in commodities.items():
        for item in items:
            variation = random.uniform(-0.15, 0.15)
            current_price = item['base_price'] * (1 + variation)
            min_price = current_price * 0.95
            max_price = current_price * 1.05
            
            all_commodities.append({
                'commodity_en': item['name_en'],
                'commodity_hi': item['name_hi'],
                'category': category,
                'min_price': round(min_price, 2),
                'max_price': round(max_price, 2),
                'modal_price': round(current_price, 2),
                'unit': item['unit'],
                'state': state,
                'district': district,
                'arrival_date': datetime.now().strftime('%Y-%m-%d'),
                'market': f"{district} Mandi"
            })
    
    return pd.DataFrame(all_commodities)

def generate_price_trends(commodity_name, days=7):
    """
    Generate price trend data for the last N days.
    In production, this would fetch historical data from database or APMC portal.
    """
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days-1, -1, -1)]
    
    base_price = random.uniform(500, 5000)
    prices = []
    
    for i in range(days):
        variation = random.uniform(-0.10, 0.10)
        if i > 0:
            price = prices[-1] * (1 + variation)
        else:
            price = base_price
        prices.append(round(price, 2))
    
    return pd.DataFrame({
        'date': dates,
        'price': prices
    })

def get_nearby_mandis(state, district):
    """
    Get list of nearby mandis with basic information.
    In production, this would query a database of registered mandis.
    """
    mandis = [
        {'name': f"{district} Main Mandi", 'distance_km': 0, 'facilities': 'Cold Storage, Grading'},
        {'name': f"{district} Krishi Mandi", 'distance_km': 5, 'facilities': 'Warehouse, Banking'},
        {'name': f"{district} Wholesale Market", 'distance_km': 12, 'facilities': 'Cold Storage'},
    ]
    
    return pd.DataFrame(mandis)
