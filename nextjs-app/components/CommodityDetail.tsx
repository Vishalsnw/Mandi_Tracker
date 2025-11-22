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
  const [showCalculator, setShowCalculator] = useState(false);
  const [inputCost, setInputCost] = useState('');
  const [quantity, setQuantity] = useState('');

  useEffect(() => {
    fetchRecommendation();
    fetchPriceHistory();
    savePriceRecord();
    saveUserHistory();
  }, []);

  const saveUserHistory = async () => {
    try {
      await axios.post('/api/user-history', {
        commodity: commodity.commodity_en,
        commodity_hi: commodity.commodity_hi,
        state: commodity.state,
        district: commodity.district,
        market: commodity.market,
        modal_price: commodity.modal_price,
        min_price: commodity.min_price,
        max_price: commodity.max_price
      });
    } catch (err) {
      console.error('Error saving user history:', err);
    }
  };

  const savePriceRecord = async () => {
    try {
      await axios.post('/api/price-history', {
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
      const response = await axios.post('/api/recommend', {
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
      const response = await axios.get('/api/price-history', {
        params: {
          commodity: commodity.commodity_en,
          state: commodity.state,
          district: commodity.district,
          days: 30
        }
      });
      
      // Only set history if data is available
      if (response.data && response.data.history && response.data.history.length > 0) {
        setPriceHistory(response.data.history);
      }
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
    date: new Date(record.date).toLocaleDateString('en-GB'),
    modal: record.modal_price,
    min: record.min_price,
    max: record.max_price
  }));

  const handleShare = async () => {
    const shareText = `${commodity.commodity_en} Price in ${commodity.district}, ${commodity.state}\n\nModal Price: ₹${commodity.modal_price}\nMin: ₹${commodity.min_price}\nMax: ₹${commodity.max_price}\n\nCheck MandiMitra for real-time prices!`;
    
    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(shareText)}`;
    window.open(whatsappUrl, '_blank');
  };

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
            <div className="flex gap-2">
              <button
                onClick={handleShare}
                className="bg-white/20 hover:bg-white/30 p-3 rounded-full transition-all flex items-center justify-center"
                title={language === 'hi' ? 'व्हाट्सएप पर शेयर करें' : 'Share on WhatsApp'}
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                </svg>
              </button>
              <button
                onClick={onClose}
                className="bg-white/20 hover:bg-white/30 p-3 rounded-full transition-all"
              >
                ✕
              </button>
            </div>
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

          {/* Profit Calculator */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border-2 border-blue-200 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-blue-800">
                💰 {language === 'hi' ? 'लाभ कैलकुलेटर' : 'Profit Calculator'}
              </h3>
              <button
                onClick={() => setShowCalculator(!showCalculator)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-all text-sm"
              >
                {showCalculator ? (language === 'hi' ? 'छिपाएं' : 'Hide') : (language === 'hi' ? 'खोलें' : 'Open')}
              </button>
            </div>
            
            {showCalculator && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    {language === 'hi' ? 'कुल लागत (₹)' : 'Total Input Cost (₹)'}
                  </label>
                  <input
                    type="number"
                    value={inputCost}
                    onChange={(e) => setInputCost(e.target.value)}
                    placeholder={language === 'hi' ? 'बीज, खाद, मजदूरी आदि' : 'Seeds, fertilizer, labor, etc'}
                    className="w-full p-3 border-2 border-blue-300 rounded-xl focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    {language === 'hi' ? 'मात्रा (क्विंटल)' : 'Quantity (Quintals)'}
                  </label>
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    placeholder={language === 'hi' ? 'उत्पादन मात्रा' : 'Production quantity'}
                    className="w-full p-3 border-2 border-blue-300 rounded-xl focus:border-blue-500 focus:outline-none"
                  />
                </div>
                {inputCost && quantity && parseFloat(quantity) > 0 && parseFloat(inputCost) > 0 && (
                  <div className="bg-white rounded-xl p-4 border-2 border-blue-300">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">{language === 'hi' ? 'कुल आय' : 'Total Revenue'}</p>
                        <p className="text-2xl font-bold text-green-600">₹{(parseFloat(quantity) * commodity.modal_price).toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">{language === 'hi' ? 'शुद्ध लाभ' : 'Net Profit'}</p>
                        <p className={`text-2xl font-bold ${(parseFloat(quantity) * commodity.modal_price - parseFloat(inputCost)) > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          ₹{((parseFloat(quantity) * commodity.modal_price) - parseFloat(inputCost)).toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">{language === 'hi' ? 'लाभ मार्जिन' : 'Profit Margin'}</p>
                        <p className="text-xl font-bold text-blue-600">
                          {(((parseFloat(quantity) * commodity.modal_price - parseFloat(inputCost)) / parseFloat(inputCost)) * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">{language === 'hi' ? 'प्रति क्विंटल लाभ' : 'Per Quintal Profit'}</p>
                        <p className="text-xl font-bold text-indigo-600">
                          ₹{((parseFloat(quantity) * commodity.modal_price - parseFloat(inputCost)) / parseFloat(quantity)).toFixed(0)}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
                {inputCost && quantity && (parseFloat(quantity) <= 0 || parseFloat(inputCost) <= 0) && (
                  <div className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-3">
                    <p className="text-yellow-800 text-sm">
                      {language === 'hi' ? '⚠️ कृपया वैध मात्रा और लागत दर्ज करें (0 से अधिक)' : '⚠️ Please enter valid quantity and cost (greater than 0)'}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

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
