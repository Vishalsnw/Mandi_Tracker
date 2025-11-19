'use client';

import { useState } from 'react';
import { useStore } from '@/lib/store';
import statesData from '@/data/states.json';
import translations from '@/data/translations.json';

export default function OnboardingScreen() {
  const { language, setLanguage, setOnboardingComplete, setSelectedState, setSelectedDistrict } = useStore();
  const [selectedState, setLocalState] = useState<string>('');
  const [selectedDistrict, setLocalDistrict] = useState<string>('');
  
  const t = translations[language];
  const states = Object.keys(statesData);

  const getDistricts = (state: string) => {
    if (!state) return [];
    const stateData = statesData[state as keyof typeof statesData];
    if (!stateData) return [];
    
    if (Array.isArray(stateData.districts[0])) {
      return (stateData.districts as Array<{en: string, hi: string}>).map(d => d.en);
    }
    return stateData.districts as string[];
  };

  const handleContinue = () => {
    if (selectedState && selectedDistrict) {
      setSelectedState(selectedState);
      setSelectedDistrict(selectedDistrict);
      setOnboardingComplete(true);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 text-center py-6 rounded-b-3xl shadow-lg">
        <div className="text-6xl mb-3">🌾</div>
        <h1 className="text-white text-4xl font-extrabold mb-2 drop-shadow-lg">
          {t.app_title}
        </h1>
        <p className="text-white/95 text-lg font-semibold">{t.tagline}</p>
      </div>

      <div className="flex-1 px-4 py-6">
        <div className="max-w-md mx-auto bg-white rounded-2xl p-8 shadow-xl mb-6">
          <div className="text-6xl text-center mb-4">🌾</div>
          <h2 className="text-emerald-600 text-2xl font-bold text-center mb-2">
            {t.welcome_hi}
          </h2>
          <h3 className="text-gray-800 text-3xl font-extrabold text-center mb-3">
            {t.welcome}
          </h3>
          <p className="text-gray-600 text-center">{t.get_started}</p>
        </div>

        <div className="max-w-md mx-auto bg-white rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-4 pb-4 border-b-2 border-gray-200 mb-6">
            <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 p-3 rounded-2xl text-4xl">
              📍
            </div>
            <div>
              <h3 className="text-gray-800 text-2xl font-bold">
                {t.select_location}
              </h3>
              <p className="text-gray-600">{t.choose_state}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 font-bold mb-2 flex items-center gap-2">
                <span className="text-2xl">🗺️</span>
                {t.select_state}
              </label>
              <select
                value={selectedState}
                onChange={(e) => {
                  setLocalState(e.target.value);
                  setLocalDistrict('');
                }}
                className="w-full p-3 border-2 border-gray-300 rounded-xl text-lg focus:border-emerald-500 focus:outline-none"
              >
                <option value="">{t.select_state}</option>
                {states.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>

            {selectedState && (
              <div>
                <label className="block text-gray-700 font-bold mb-2 flex items-center gap-2">
                  <span className="text-2xl">📌</span>
                  {t.select_district}
                </label>
                <select
                  value={selectedDistrict}
                  onChange={(e) => setLocalDistrict(e.target.value)}
                  className="w-full p-3 border-2 border-gray-300 rounded-xl text-lg focus:border-emerald-500 focus:outline-none"
                >
                  <option value="">{t.select_district}</option>
                  {getDistricts(selectedState).map((district) => (
                    <option key={district} value={district}>
                      {district}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {selectedState && selectedDistrict && (
              <button
                onClick={handleContinue}
                className="w-full bg-gradient-to-r from-emerald-600 to-emerald-700 text-white py-4 rounded-xl text-xl font-bold shadow-lg hover:from-emerald-700 hover:to-emerald-800 transition-all"
              >
                {t.continue}
              </button>
            )}
          </div>
        </div>

        <div className="flex justify-center gap-4 mt-6">
          <button
            onClick={() => setLanguage('en')}
            className={`px-6 py-3 rounded-xl font-bold transition-all ${
              language === 'en'
                ? 'bg-emerald-600 text-white shadow-lg'
                : 'bg-white text-gray-700 border-2 border-gray-300'
            }`}
          >
            English
          </button>
          <button
            onClick={() => setLanguage('hi')}
            className={`px-6 py-3 rounded-xl font-bold transition-all ${
              language === 'hi'
                ? 'bg-emerald-600 text-white shadow-lg'
                : 'bg-white text-gray-700 border-2 border-gray-300'
            }`}
          >
            हिंदी
          </button>
        </div>
      </div>
    </div>
  );
}
