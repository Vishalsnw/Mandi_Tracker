import { NextRequest, NextResponse } from 'next/server';
import { getPriceHistory } from '@/lib/priceHistory';

interface RecommendationRequest {
  commodity: string;
  state: string;
  district: string;
  modal_price: number;
  min_price: number;
  max_price: number;
}

function calculateRecommendation(
  commodity: string,
  state: string,
  district: string,
  currentPrice: number,
  minPrice: number,
  maxPrice: number
) {
  const history = getPriceHistory(state, district, commodity, 30);
  
  if (history.length < 3) {
    const volatility = ((maxPrice - minPrice) / currentPrice * 100);
    
    if (volatility > 30) {
      return {
        action: 'HOLD',
        confidence: 'LOW',
        reason: 'High price volatility detected. Wait for market stabilization.',
        reason_hi: 'उच्च मूल्य अस्थिरता। बाजार स्थिरता की प्रतीक्षा करें।'
      };
    } else if (currentPrice > (minPrice + maxPrice) / 2) {
      return {
        action: 'SELL',
        confidence: 'MEDIUM',
        reason: 'Price is above market average. Good time to sell.',
        reason_hi: 'मूल्य बाजार औसत से ऊपर है। बेचने का अच्छा समय।'
      };
    } else {
      return {
        action: 'HOLD',
        confidence: 'MEDIUM',
        reason: 'Price below average. Consider holding for better rates.',
        reason_hi: 'मूल्य औसत से नीचे। बेहतर दरों के लिए प्रतीक्षा करें।'
      };
    }
  }
  
  const recentPrices = history.slice(-10).map(h => h.modal_price);
  const avgPrice = recentPrices.reduce((a, b) => a + b, 0) / recentPrices.length;
  
  let trendPct = 0;
  if (recentPrices.length >= 10) {
    const recentAvg = recentPrices.slice(-5).reduce((a, b) => a + b, 0) / 5;
    const olderAvg = recentPrices.slice(-10, -5).reduce((a, b) => a + b, 0) / 5;
    trendPct = ((recentAvg - olderAvg) / olderAvg * 100);
  }
  
  const mean = recentPrices.reduce((a, b) => a + b, 0) / recentPrices.length;
  const squareDiffs = recentPrices.map(price => Math.pow(price - mean, 2));
  const avgSquareDiff = squareDiffs.reduce((a, b) => a + b, 0) / squareDiffs.length;
  const stdDev = Math.sqrt(avgSquareDiff);
  const volatility = (stdDev / avgPrice * 100);
  
  const pricePercentile = (recentPrices.filter(p => p < currentPrice).length / recentPrices.length * 100);
  
  if (pricePercentile > 75 && volatility < 20) {
    return {
      action: 'SELL',
      confidence: 'HIGH',
      reason: `Price at ${pricePercentile.toFixed(0)}th percentile with stable market. Good opportunity to sell.`,
      reason_hi: `मूल्य ${pricePercentile.toFixed(0)}वें प्रतिशतक पर स्थिर बाजार के साथ। बेचने का अच्छा अवसर।`,
      trend_pct: Math.round(trendPct * 10) / 10,
      volatility: Math.round(volatility * 10) / 10,
      price_percentile: Math.round(pricePercentile)
    };
  } else if (pricePercentile > 60 && trendPct < -5) {
    return {
      action: 'SELL',
      confidence: 'MEDIUM',
      reason: 'Prices declining from recent highs. Consider selling now.',
      reason_hi: 'हाल के उच्चतम स्तर से मूल्य गिर रहे हैं। अब बेचने पर विचार करें।',
      trend_pct: Math.round(trendPct * 10) / 10,
      volatility: Math.round(volatility * 10) / 10,
      price_percentile: Math.round(pricePercentile)
    };
  } else if (trendPct > 10 && pricePercentile > 30) {
    return {
      action: 'HOLD',
      confidence: 'MEDIUM',
      reason: 'Strong upward trend. Prices may rise further. Hold for better rates.',
      reason_hi: 'मजबूत ऊपर की प्रवृत्ति। मूल्य और बढ़ सकते हैं। प्रतीक्षा करें।',
      trend_pct: Math.round(trendPct * 10) / 10,
      volatility: Math.round(volatility * 10) / 10,
      price_percentile: Math.round(pricePercentile)
    };
  } else if (volatility > 25) {
    return {
      action: 'HOLD',
      confidence: 'MEDIUM',
      reason: 'Market highly volatile. Wait for stabilization before selling.',
      reason_hi: 'बाजार अत्यधिक अस्थिर। बेचने से पहले स्थिरता की प्रतीक्षा करें।',
      trend_pct: Math.round(trendPct * 10) / 10,
      volatility: Math.round(volatility * 10) / 10,
      price_percentile: Math.round(pricePercentile)
    };
  } else if (pricePercentile < 30) {
    return {
      action: 'HOLD',
      confidence: 'HIGH',
      reason: 'Price well below recent average. Hold for better opportunities.',
      reason_hi: 'मूल्य हाल के औसत से काफी नीचे। बेहतर अवसरों की प्रतीक्षा करें।',
      trend_pct: Math.round(trendPct * 10) / 10,
      volatility: Math.round(volatility * 10) / 10,
      price_percentile: Math.round(pricePercentile)
    };
  } else {
    return {
      action: 'HOLD',
      confidence: 'MEDIUM',
      reason: 'Market conditions neutral. Monitor prices before deciding.',
      reason_hi: 'बाजार की स्थिति तटस्थ। निर्णय लेने से पहले मूल्यों की निगरानी करें।',
      trend_pct: Math.round(trendPct * 10) / 10,
      volatility: Math.round(volatility * 10) / 10,
      price_percentile: Math.round(pricePercentile)
    };
  }
}

export async function POST(request: NextRequest) {
  try {
    const data: RecommendationRequest = await request.json();
    
    const recommendation = calculateRecommendation(
      data.commodity,
      data.state,
      data.district,
      data.modal_price,
      data.min_price,
      data.max_price
    );
    
    return NextResponse.json(recommendation);
  } catch (error: any) {
    return NextResponse.json(
      { error: 'Error calculating recommendation', message: error.message },
      { status: 500 }
    );
  }
}
