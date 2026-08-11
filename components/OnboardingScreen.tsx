'use client';

import { useState } from 'react';
import { useStore } from '@/lib/store';
import statesData from '@/data/states.json';
import translations from '@/data/translations.json';

export default function OnboardingScreen() {
  const { language, setLanguage, setSelectedState, setSelectedDistrict, setOnboardingComplete } = useStore();
  const [tempState, setTempState] = useState('');
  const [tempDistrict, setTempDistrict] = useState('');

  const t = translations[language];
  const states = Object.keys(statesData);
  const districts = tempState ? (statesData as Record<string, string[]>)[tempState] || [] : [];

  const handleStart = () => {
    if (!tempState || !tempDistrict) return;
    setSelectedState(tempState);
    setSelectedDistrict(tempDistrict);
    setOnboardingComplete(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-600 to-teal-800 text-white flex flex-col justify-center items-center p-4">
      <div className="max-w-md w-full bg-white text-gray-800 rounded-3xl p-6 md:p-8 shadow-2xl">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-extrabold text-emerald-700">{t.app_title}</h1>
          <p className="text-sm text-gray-500 mt-1">{t.tagline}</p>
        </div>

        <div className="flex justify-center gap-2 mb-6 bg-slate-100 p-1.5 rounded-xl">
          <button
            onClick={() => setLanguage('hi')}
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
              language === 'hi' ? 'bg-emerald-600 text-white shadow' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            हिंदी
          </button>
          <button
            onClick={() => setLanguage('en')}
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
              language === 'en' ? 'bg-emerald-600 text-white shadow' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            English
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">{t.choose_state}</label>
            <select
              value={tempState}
              onChange={(e) => {
                setTempState(e.target.value);
                setTempDistrict('');
              }}
              className="w-full p-3 border rounded-xl bg-gray-50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="">{t.select_state}</option>
              {states.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">जिला चुनें</label>
            <select
              value={tempDistrict}
              onChange={(e) => setTempDistrict(e.target.value)}
              disabled={!tempState}
              className="w-full p-3 border rounded-xl bg-gray-50 text-gray-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-50"
            >
              <option value="">{t.select_district}</option>
              {districts.map((dist) => (
                <option key={dist} value={dist}>
                  {dist}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleStart}
            disabled={!tempState || !tempDistrict}
            className="w-full mt-4 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 text-white py-3.5 rounded-xl font-bold transition shadow-lg"
          >
            {t.get_started}
          </button>
        </div>
      </div>
    </div>
  );
}
