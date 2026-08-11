'use client';

import { useState } from 'react';
import { useStore } from '@/lib/store';
import translations from '@/data/translations.json';

export default function PriceDisplay() {
  const { language, selectedState, selectedDistrict, priceData, reset } = useStore();
  const [searchQuery, setSearchQuery] = useState('');
  const t = translations[language];

  const tDict = t as Record<string, string>;

  const filteredData = priceData.filter(item => {
    const nameEn = (item.commodity_en || '').toLowerCase();
    const nameHi = (item.commodity_hi || '').toLowerCase();
    const q = searchQuery.toLowerCase();
    return nameEn.includes(q) || nameHi.includes(q);
  });

  return (
    <div className="min-h-screen p-4 max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl p-6 shadow-md mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-emerald-700">{tDict.app_title || 'Mandi Mitra'}</h1>
          <p className="text-gray-600 text-sm">📍 {selectedState}, {selectedDistrict}</p>
        </div>
        <button
          onClick={reset}
          className="bg-emerald-100 text-emerald-800 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-emerald-200"
        >
          {tDict.change_location || 'Change Location'}
        </button>
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder={tDict.search_placeholder || 'Search commodity...'}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full p-4 rounded-xl border-2 border-emerald-200 focus:border-emerald-500 focus:outline-none bg-white shadow-sm"
        />
      </div>

      {filteredData.length === 0 ? (
        <div className="bg-white p-8 rounded-2xl text-center text-gray-500 shadow-sm">
          {tDict.no_data || 'No prices found.'}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredData.map((item, idx) => (
            <div key={idx} className="bg-white p-5 rounded-2xl shadow-sm border border-emerald-100">
              <h3 className="font-bold text-lg text-gray-800">
                {language === 'hi' ? item.commodity_hi || item.commodity_en : item.commodity_en}
              </h3>
              <p className="text-sm text-gray-500">{item.market}</p>
              <div className="mt-3 flex justify-between items-end">
                <div>
                  <span className="text-xs text-gray-400 block">{tDict.modal_price || 'Modal Price'}</span>
                  <span className="text-xl font-extrabold text-emerald-600">₹{item.modal_price}/q</span>
                </div>
                <div className="text-right text-xs text-gray-500">
                  <span>Min: ₹{item.min_price}</span> | <span>Max: ₹{item.max_price}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
