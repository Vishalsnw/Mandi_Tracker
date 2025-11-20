'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

interface CommodityDetailProps {
  commodity: {
    commodity_en: string;
    commodity_hi: string;
    min_price: number;
    max_price: number;
    modal_price: number;
    category: string;
    market: string;
    state: string;
    district: string;
  };
  language: 'en' | 'hi';
  onClose: () => void;
}

interface Recommendation {
  action: string;
  confidence: string;
  reason: string;
  reason_hi: string;
  trend_pct?: number;
  volatility?: number;
  price_percentile?: number;
}

export default function CommodityDetail({ commodity, language, onClose }: CommodityDetailProps) {
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [priceHistory, setPriceHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecommendation();
    fetchPriceHistory();
    savePriceRecord();
  }, []);

  const savePriceRecord = async () => {
    try {
      await axios.post('http://localhost:3000/api/save-price', {
        commodity: commodity.commodity_en,
        state: commodity.state,
        district: commodity.district,
        modal_price: commodity.modal_price,
        min_price: commodity.min_price,
        max_price: commodity.max_price
      });
    } catch (err) {
      console.error('Error saving price:', err);
    }
  };

  const fetchRecommendation = async () => {
    try {
      const response = await axios.post('http://localhost:3000/api/recommend', {
        commodity: commodity.commodity_en,
        state: commodity.state,
        district: commodity.district,
        modal_price: commodity.modal_price,
        min_price: commodity.min_price,
        max_price: commodity.max_price
      });
      setRecommendation(response.data);
    } catch (err) {
      console.error('Error fetching recommendation:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPriceHistory = async () => {
    try {
      const response = await axios.get('http://localhost:3000/api/price-history', {
        params: {
          commodity: commodity.commodity_en,
          state: commodity.state,
          district: commodity.district,
          days: 30
        }
      });
      setPriceHistory(response.data);
    } catch (err) {
      console.error('Error fetching price history:', err);
    }
  };

  const getRecommendationColor = (action: string) => {
    return action === 'SELL' ? 'bg-green-100 border-green-500 text-green-800' : 'bg-yellow-100 border-yellow-500 text-yellow-800';
  };

  const getRecommendationIcon = (action: string) => {
    return action === 'SELL' ? '✅' : '⏳';
  };

  const volatility = commodity.modal_price > 0 ? ((commodity.max_price - commodity.min_price) / commodity.modal_price * 100).toFixed(1) : '0.0';

  const chartData = priceHistory.map(record => ({
    date: new Date(record.timestamp).toLocaleDateString('en-GB'),
    modal: record.modal_price,
    min: record.min_price,
    max: record.max_price
  }));

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-emerald-600 to-emerald-700 text-white p-6 rounded-t-3xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold">
                {language === 'hi' ? commodity.commodity_hi : commodity.commodity_en}
              </h2>
              <p className="text-emerald-100 mt-1">{commodity.market}</p>
            </div>
            <button
              onClick={onClose}
              className="bg-white/20 hover:bg-white/30 p-3 rounded-full transition-all"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Price Cards */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-emerald-50 rounded-2xl p-4 text-center border-2 border-emerald-200">
              <p className="text-sm text-gray-600 mb-1">{language === 'hi' ? 'न्यूनतम' : 'Min'}</p>
              <p className="text-2xl font-bold text-emerald-700">₹{commodity.min_price}</p>
            </div>
            <div className="bg-gray-50 rounded-2xl p-4 text-center border-2 border-gray-300">
              <p className="text-sm text-gray-600 mb-1">{language === 'hi' ? 'मॉडल' : 'Modal'}</p>
              <p className="text-3xl font-extrabold text-gray-800">₹{commodity.modal_price}</p>
            </div>
            <div className="bg-orange-50 rounded-2xl p-4 text-center border-2 border-orange-200">
              <p className="text-sm text-gray-600 mb-1">{language === 'hi' ? 'अधिकतम' : 'Max'}</p>
              <p className="text-2xl font-bold text-orange-700">₹{commodity.max_price}</p>
            </div>
          </div>

          {/* Recommendation */}
          {loading && (
            <div className="bg-gray-50 rounded-2xl p-6 text-center mb-6">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-emerald-600 border-t-transparent"></div>
              <p className="mt-2 text-gray-600">{language === 'hi' ? 'सिफारिश लोड हो रही है...' : 'Loading recommendation...'}</p>
            </div>
          )}

          {!loading && recommendation && (
            <div className={`rounded-2xl p-6 mb-6 border-2 ${getRecommendationColor(recommendation.action)}`}>
              <div className="flex items-start gap-4">
                <div className="text-4xl">{getRecommendationIcon(recommendation.action)}</div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-2">
                    {language === 'hi' ? 'सिफारिश' : 'Recommendation'}: {recommendation.action}
                  </h3>
                  <p className="text-lg mb-2">
                    {language === 'hi' ? recommendation.reason_hi : recommendation.reason}
                  </p>
                  <div className="flex gap-4 text-sm mt-3">
                    <span className="bg-white/50 px-3 py-1 rounded-full">
                      {language === 'hi' ? 'विश्वास' : 'Confidence'}: {recommendation.confidence}
                    </span>
                    {recommendation.volatility !== undefined && (
                      <span className="bg-white/50 px-3 py-1 rounded-full">
                        {language === 'hi' ? 'अस्थिरता' : 'Volatility'}: {recommendation.volatility}%
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Market Stats */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-50 rounded-2xl p-4 border-2 border-gray-200">
              <p className="text-sm text-gray-600 mb-1">{language === 'hi' ? 'मूल्य सीमा' : 'Price Range'}</p>
              <p className="text-xl font-bold text-gray-800">₹{commodity.max_price - commodity.min_price}</p>
            </div>
            <div className="bg-gray-50 rounded-2xl p-4 border-2 border-gray-200">
              <p className="text-sm text-gray-600 mb-1">{language === 'hi' ? 'अस्थिरता' : 'Volatility'}</p>
              <p className={`text-xl font-bold ${parseFloat(volatility) > 20 ? 'text-red-600' : 'text-green-600'}`}>
                {volatility}%
              </p>
            </div>
          </div>

          {/* Price History Chart */}
          {chartData.length > 0 && (
            <div className="mb-6">
              <h3 className="text-xl font-bold mb-4">
                {language === 'hi' ? '📈 मूल्य इतिहास (30 दिन)' : '📈 Price History (30 Days)'}
              </h3>
              <div className="bg-gray-50 rounded-2xl p-4 border-2 border-gray-200">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="modal" 
                      stroke="#059669" 
                      strokeWidth={3}
                      name={language === 'hi' ? 'मॉडल मूल्य' : 'Modal Price'}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="max" 
                      stroke="#f97316" 
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      name={language === 'hi' ? 'अधिकतम मूल्य' : 'Max Price'}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="min" 
                      stroke="#10b981" 
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      name={language === 'hi' ? 'न्यूनतम मूल्य' : 'Min Price'}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {chartData.length === 0 && (
            <div className="bg-blue-50 rounded-2xl p-6 border-2 border-blue-200 mb-6">
              <p className="text-blue-800">
                {language === 'hi' 
                  ? '📊 मूल्य इतिहास एकत्र किया जा रहा है। ट्रेंड चार्ट देखने के लिए बाद में वापस आएं।'
                  : '📊 Price history is being collected. Come back later to see trend charts.'}
              </p>
            </div>
          )}

          {/* Additional Info */}
          <div className="bg-gray-50 rounded-2xl p-4 border-2 border-gray-200">
            <h4 className="font-bold mb-2">{language === 'hi' ? '📍 स्थान जानकारी' : '📍 Location Info'}</h4>
            <p className="text-gray-700">
              <strong>{language === 'hi' ? 'राज्य' : 'State'}:</strong> {commodity.state}<br/>
              <strong>{language === 'hi' ? 'जिला' : 'District'}:</strong> {commodity.district}<br/>
              <strong>{language === 'hi' ? 'श्रेणी' : 'Category'}:</strong> {commodity.category}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
