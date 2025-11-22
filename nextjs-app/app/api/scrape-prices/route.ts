import { NextRequest, NextResponse } from 'next/server';
import { savePriceRecord } from '@/lib/priceHistory';
import { getHindiName } from '@/lib/hindiNames';

interface PriceRecord {
  commodity_en: string;
  commodity_hi: string;
  category: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  unit: string;
  state: string;
  district: string;
  arrival_date: string;
  market: string;
  variety: string;
  grade: string;
}

function categorizeCommodity(commodityName: string): string {
  const commodity_lower = commodityName.toLowerCase();
  
  const vegetables = ['tomato', 'onion', 'potato', 'cabbage', 'cauliflower', 'carrot', 'brinjal', 
                      'chilli', 'pepper', 'capsicum', 'cucumber', 'pumpkin', 'gourd', 'radish',
                      'beetroot', 'spinach', 'coriander', 'ginger', 'garlic', 'ladyfinger', 'okra'];
  
  const fruits = ['apple', 'mango', 'banana', 'orange', 'grapes', 'pomegranate', 'papaya', 
                  'watermelon', 'muskmelon', 'guava', 'pineapple', 'lemon', 'lime', 'coconut'];
  
  const grains = ['wheat', 'rice', 'maize', 'bajra', 'jowar', 'ragi', 'barley', 'paddy'];
  
  const pulses = ['tur', 'moong', 'urad', 'chana', 'masoor', 'dal', 'peas', 'gram', 'lentil', 'arhar'];
  
  for (const veg of vegetables) {
    if (commodity_lower.includes(veg)) return 'vegetables';
  }
  
  for (const fruit of fruits) {
    if (commodity_lower.includes(fruit)) return 'fruits';
  }
  
  for (const grain of grains) {
    if (commodity_lower.includes(grain)) return 'grains';
  }
  
  for (const pulse of pulses) {
    if (commodity_lower.includes(pulse)) return 'pulses';
  }
  
  return 'vegetables';
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const state = searchParams.get('state');
  const district = searchParams.get('district');
  const commodity = searchParams.get('commodity');

  const API_KEY = process.env.APMC_API_KEY || "579b464db66ec23bdd0000011a8be7e716d24aad697fad89aa08940a";
  const RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070";
  const BASE_URL = `https://api.data.gov.in/resource/${RESOURCE_ID}`;

  try {
    let params = new URLSearchParams({
      'api-key': API_KEY,
      'format': 'json',
      'offset': '0',
      'limit': '500'
    });

    if (state) {
      params.append('filters[state]', state);
    }
    if (district) {
      params.append('filters[district]', district);
    }
    if (commodity) {
      params.append('filters[commodity]', commodity);
    }

    let response = await fetch(`${BASE_URL}?${params.toString()}`, {
      headers: {
        'User-Agent': 'Mozilla/5.0'
      }
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch data from API', data: [] },
        { status: response.status }
      );
    }

    let data = await response.json();
    let records = data.records || [];
    let isFallback = false;

    if (records.length === 0 && state && district) {
      params = new URLSearchParams({
        'api-key': API_KEY,
        'format': 'json',
        'offset': '0',
        'limit': '500'
      });
      
      params.append('filters[state]', state);
      
      if (commodity) {
        params.append('filters[commodity]', commodity);
      }

      response = await fetch(`${BASE_URL}?${params.toString()}`, {
        headers: {
          'User-Agent': 'Mozilla/5.0'
        }
      });

      if (response.ok) {
        data = await response.json();
        records = data.records || [];
        isFallback = records.length > 0;
      }
    }

    const processedData: PriceRecord[] = records.map((record: any) => {
      const commodityName = record.commodity || 'Unknown';
      const category = categorizeCommodity(commodityName);
      const hindiName = getHindiName(commodityName);

      return {
        commodity_en: commodityName,
        commodity_hi: hindiName,
        category,
        min_price: parseFloat(record.min_price || '0'),
        max_price: parseFloat(record.max_price || '0'),
        modal_price: parseFloat(record.modal_price || '0'),
        unit: 'Quintal',
        state: record.state || '',
        district: record.district || '',
        arrival_date: record.arrival_date || new Date().toLocaleDateString('en-GB'),
        market: record.market || `${record.district} Mandi`,
        variety: record.variety || '',
        grade: record.grade || ''
      };
    }).filter((record: PriceRecord) => record.state && record.district);

    // Save prices to history
    if (state && district && processedData.length > 0) {
      try {
        for (const record of processedData) {
          await savePriceRecord(
            state,
            district,
            record.commodity_en,
            record.min_price,
            record.max_price,
            record.modal_price
          );
        }
      } catch (err) {
        console.error('Error saving price history:', err);
      }
    }

    return NextResponse.json({
      success: true,
      data: processedData,
      count: processedData.length,
      isFallback,
      requestedDistrict: district
    });

  } catch (error: any) {
    console.error('Error fetching APMC data:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error.message, data: [] },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    
    await savePriceRecord(
      data.state,
      data.district,
      data.commodity,
      data.min_price,
      data.max_price,
      data.modal_price
    );
    
    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json(
      { error: 'Error saving price record', message: error.message },
      { status: 500 }
    );
  }
}
