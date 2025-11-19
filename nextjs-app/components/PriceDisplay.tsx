'use client';

import { useEffect } from 'react';
import { useStore } from '@/lib/store';
import translations from '@/data/translations.json';
import axios from 'axios';

interface PriceCardProps {
  commodity: string;
  minPrice: number;
  maxPrice: number;
  modalPrice: number;
  market: string;
  category: string;
}

function PriceCard({ commodity, minPrice, maxPrice, modalPrice, market, category }: PriceCardProps) {
  const getCategoryEmoji = (cat: string) => {
    switch (cat) {
      case 'vegetables': return '🥬';
      case 'fruits': return '🍎';
      case 'grains': return '🌾';
      case 'pulses': return '🫘';
      default: return '🌱';
    }
  };

  const volatility = ((maxPrice - minPrice) / modalPrice * 100).toFixed(1);
  const priceRange = maxPrice - minPrice;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-4xl">{getCategoryEmoji(category)}</span>
          <div>
            <h3 className="text-xl font-bold text-gray-800">{commodity}</h3>
            <p className="text-sm text-gray-500">{market}</p>
          </div>
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

      <div className="flex justify-between text-sm text-gray-600">
        <span>Range: ₹{priceRange}</span>
        <span className={`font-semibold ${parseFloat(volatility) > 20 ? 'text-red-500' : 'text-green-500'}`}>
          {volatility}% volatility
        </span>
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
    loading,
    error,
    setPriceData, 
    setSelectedCategory,
    setLoading,
    setError,
    reset
  } = useStore();
  
  const t = translations[language];

  useEffect(() => {
    if (selectedState && selectedDistrict) {
      fetchPrices();
    }
  }, [selectedState, selectedDistrict]);

  const fetchPrices = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/scrape-prices', {
        params: {
          state: selectedState,
          district: selectedDistrict
        }
      });
      
      setPriceData(response.data.data || []);
    } catch (err: any) {
      setError(err.message || 'Error loading data');
      console.error('Error fetching prices:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredData = selectedCategory === 'all' 
    ? priceData 
    : priceData.filter(item => item.category === selectedCategory);

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
                <span className="font-bold text-2xl text-emerald-600">{filteredData.length}</span> commodities found
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredData.map((item, index) => (
                <PriceCard
                  key={index}
                  commodity={item.commodity_en}
                  minPrice={item.min_price}
                  maxPrice={item.max_price}
                  modalPrice={item.modal_price}
                  market={item.market}
                  category={item.category}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
