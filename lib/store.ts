import { create } from 'zustand';

export interface PriceRecord {
  commodity_en: string;
  commodity_hi: string;
  category: string;
  state: string;
  district: string;
  market: string;
  modal_price: number;
  min_price: number;
  max_price: number;
  price_date: string;
}

interface AppState {
  language: 'hi' | 'en';
  selectedState: string;
  selectedDistrict: string;
  onboardingComplete: boolean;
  selectedCategory: string;
  searchQuery: string;
  priceData: PriceRecord[];
  
  setLanguage: (lang: 'hi' | 'en') => void;
  setSelectedState: (state: string) => void;
  setSelectedDistrict: (district: string) => void;
  setOnboardingComplete: (complete: boolean) => void;
  setSelectedCategory: (category: string) => void;
  setSearchQuery: (query: string) => void;
  setPriceData: (data: PriceRecord[]) => void;
  reset: () => void;
}

export const useStore = create<AppState>((set) => ({
  language: 'hi',
  selectedState: '',
  selectedDistrict: '',
  onboardingComplete: false,
  selectedCategory: 'all',
  searchQuery: '',
  priceData: [],
  
  setLanguage: (language) => set({ language }),
  setSelectedState: (selectedState) => set({ selectedState }),
  setSelectedDistrict: (selectedDistrict) => set({ selectedDistrict }),
  setOnboardingComplete: (onboardingComplete) => set({ onboardingComplete }),
  setSelectedCategory: (selectedCategory) => set({ selectedCategory }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setPriceData: (priceData) => set({ priceData }),
  reset: () => set({
    selectedState: '',
    selectedDistrict: '',
    onboardingComplete: false,
    selectedCategory: 'all',
    searchQuery: '',
    priceData: []
  })
}));
