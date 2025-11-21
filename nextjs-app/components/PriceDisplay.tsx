'use client';

import { useEffect, useState } from 'react';
import { useStore } from '@/lib/store';
import translations from '@/data/translations.json';
import axios from 'axios';
import CommodityDetail from './CommodityDetail';

interface PriceCardProps {
  commodity: string;
  minPrice: number;
  maxPrice: number;
  modalPrice: number;
  market: string;
  category: string;
}

function PriceCard({ commodity, commodityHi, minPrice, maxPrice, modalPrice, market, category, language, onClick }: PriceCardProps & { commodityHi: string; language: 'en' | 'hi'; onClick: () => void }) {
  const getCategoryEmoji = (cat: string) => {
    switch (cat) {
      case 'vegetables': return '🥬';
      case 'fruits': return '🍎';
      case 'grains': return '🌾';
      case 'pulses': return '🫘';
      default: return '🌱';
    }
  };

  const volatility = modalPrice > 0 ? ((maxPrice - minPrice) / modalPrice * 100).toFixed(1) : '0.0';
  const priceRange = maxPrice - minPrice;

  // Simple trend indicator based on price position in range
  const getPriceTrend = () => {
    const position = ((modalPrice - minPrice) / (maxPrice - minPrice)) * 100;
    if (position > 70) return { icon: '📈', color: 'text-red-500', label: language === 'hi' ? 'उच्च' : 'High' };
    if (position < 30) return { icon: '📉', color: 'text-green-500', label: language === 'hi' ? 'कम' : 'Low' };
    return { icon: '➡️', color: 'text-yellow-500', label: language === 'hi' ? 'सामान्य' : 'Normal' };
  };

  const trend = getPriceTrend();

  return (
    <div 
      className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all cursor-pointer hover:scale-105"
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-4xl">{getCategoryEmoji(category)}</span>
          <div>
            <h3 className="text-xl font-bold text-gray-800">{language === 'hi' ? commodityHi : commodity}</h3>
            <p className="text-sm text-gray-500">{market}</p>
          </div>
        </div>
        <div className="text-right">
          <div className={`text-2xl ${trend.color}`}>{trend.icon}</div>
          <span className={`text-xs font-semibold ${trend.color}`}>{trend.label}</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">Min</p>
          <p className="text-lg font-bold text-emerald-600">₹{minPrice}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">Modal</p>
          <p className="text-xl font-extrabold text-gray-800">₹{modalPrice}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">Max</p>
          <p className="text-lg font-bold text-orange-600">₹{maxPrice}</p>
        </div>
      </div>

      <div className="flex justify-between text-sm text-gray-600 mb-3">
        <span>Range: ₹{priceRange}</span>
        <span className={`font-semibold ${parseFloat(volatility) > 20 ? 'text-red-500' : 'text-green-500'}`}>
          {volatility}% volatility
        </span>
      </div>
      
      <div className="text-center pt-3 border-t border-gray-200">
        <p className="text-emerald-600 font-semibold text-sm flex items-center justify-center gap-1">
          <span>👉</span>
          {language === 'hi' ? 'विवरण देखने के लिए टैप करें' : 'Tap to view details'}
          <span>📊</span>
        </p>
      </div>
    </div>
  );
}

export default function PriceDisplay() {
  const { 
    language, 
    selectedState, 
    selectedDistrict, 
    priceData, 
    selectedCategory,
    searchQuery,
    loading,
    error,
    setPriceData, 
    setSelectedCategory,
    setSearchQuery,
    setLoading,
    setError,
    reset
  } = useStore();
  
  const [selectedCommodity, setSelectedCommodity] = useState<any>(null);
  const [isFallbackData, setIsFallbackData] = useState(false);
  const [requestedDistrict, setRequestedDistrict] = useState('');
  const [isListening, setIsListening] = useState(false);
  
  const t = translations[language];

  const startVoiceSearch = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Voice search not supported in this browser');
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
    recognition.continuous = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setSearchQuery(transcript);
    };

    recognition.start();
  };

  useEffect(() => {
    if (selectedState && selectedDistrict) {
      fetchPrices();
    }
  }, [selectedState, selectedDistrict]);

  const fetchPrices = async () => {
    setLoading(true);
    setError(null);
    setIsFallbackData(false);
    
    try {
      const response = await axios.get('/api/scrape-prices', {
        params: {
          state: selectedState,
          district: selectedDistrict
        }
      });
      
      setPriceData(response.data.data || []);
      setIsFallbackData(response.data.isFallback || false);
      setRequestedDistrict(response.data.requestedDistrict || selectedDistrict);
    } catch (err: any) {
      setError(err.message || 'Error loading data');
      console.error('Error fetching prices:', err);
    } finally {
      setLoading(false);
    }
  };

  let filteredData = selectedCategory === 'all' 
    ? priceData 
    : priceData.filter(item => item.category === selectedCategory);
  
  if (searchQuery.trim()) {
    const query = searchQuery.toLowerCase();
    filteredData = filteredData.filter(item => 
      item.commodity_en.toLowerCase().includes(query) ||
      item.commodity_hi.toLowerCase().includes(query)
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 text-white p-4 shadow-lg sticky top-0 z-10">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <span className="text-4xl">🌾</span>
              <div>
                <h1 className="text-2xl font-bold">{t.app_title}</h1>
                <p className="text-sm opacity-90">{selectedState} - {selectedDistrict}</p>
              </div>
            </div>
            <button
              onClick={reset}
              className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg font-semibold transition-all"
            >
              Change Location
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 max-w-6xl mx-auto w-full p-4">
        <div className="mb-4 relative">
          <input
            type="text"
            placeholder="🔍 Search commodity / वस्तु खोजें"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 pr-14 border-2 border-gray-300 rounded-xl text-lg focus:border-emerald-500 focus:outline-none"
          />
          <button
            onClick={startVoiceSearch}
            className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all ${
              isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-emerald-500 text-white hover:bg-emerald-600'
            }`}
            title={language === 'hi' ? 'आवाज से खोजें' : 'Voice search'}
          >
            {isListening ? '🔴' : '🎤'}
          </button>
        </div>

        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {['all', 'vegetables', 'fruits', 'grains', 'pulses'].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-lg font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-emerald-600 text-white shadow-md'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {t[cat as keyof typeof t] || cat}
            </button>
          ))}
        </div>

        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-emerald-600 border-t-transparent"></div>
            <p className="mt-4 text-gray-600 font-semibold">{t.loading}</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-6 text-center">
            <p className="text-red-700 font-semibold">{error}</p>
            <button
              onClick={fetchPrices}
              className="mt-4 bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-all"
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && filteredData.length === 0 && (
          <div className="bg-yellow-50 border-2 border-yellow-300 rounded-2xl p-6 text-center">
            <p className="text-yellow-800 font-semibold">{t.no_data}</p>
          </div>
        )}

        {!loading && filteredData.length > 0 && (
          <>
            <div className="bg-white rounded-2xl p-4 mb-6 shadow-md">
              <p className="text-gray-700">
                <span className="font-bold text-2xl text-emerald-600">{filteredData.length}</span> {language === 'hi' ? 'वस्तुएं मिलीं' : 'commodities found'}
              </p>
              
              {isFallbackData && (
                <div className="mt-3 p-3 bg-amber-50 rounded-lg border border-amber-300">
                  <p className="text-sm text-amber-900 font-semibold">
                    {language === 'hi' 
                      ? `📍 ${requestedDistrict} में कोई डेटा नहीं मिला। ${selectedState} राज्य के सभी बाजारों से मूल्य दिखा रहे हैं।`
                      : `📍 No data found for ${requestedDistrict}. Showing prices from all markets in ${selectedState} state.`}
                  </p>
                </div>
              )}
              
              {!isFallbackData && priceData.length <= 5 && (
                <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-800">
                    {language === 'hi' 
                      ? '💡 सूचना: कुछ क्षेत्रों में सीमित डेटा उपलब्ध है क्योंकि यह सरकारी APMC डेटाबेस से आता है। अधिक डेटा के लिए अन्य बड़े जिले (जैसे पुणे, मुंबई) आज़माएं।'
                      : '💡 Note: Limited data available for this location from the government APMC database. Try larger districts (like Pune, Mumbai) for more commodity data.'}
                  </p>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredData.map((item, index) => (
                <PriceCard
                  key={index}
                  commodity={item.commodity_en}
                  commodityHi={item.commodity_hi}
                  minPrice={item.min_price}
                  maxPrice={item.max_price}
                  modalPrice={item.modal_price}
                  market={item.market}
                  category={item.category}
                  language={language}
                  onClick={() => setSelectedCommodity(item)}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {selectedCommodity && (
        <CommodityDetail
          commodity={selectedCommodity}
          language={language}
          onClose={() => setSelectedCommodity(null)}
        />
      )}
    </div>
  );
}
