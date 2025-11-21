import { create } from 'zustand';

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

interface StoreState {
  language: 'en' | 'hi';
  onboardingComplete: boolean;
  selectedState: string;
  selectedDistrict: string;
  priceData: PriceRecord[];
  selectedCategory: string;
  searchQuery: string;
  loading: boolean;
  error: string | null;
  setLanguage: (language: 'en' | 'hi') => void;
  setOnboardingComplete: (complete: boolean) => void;
  setSelectedState: (state: string) => void;
  setSelectedDistrict: (district: string) => void;
  setPriceData: (data: PriceRecord[]) => void;
  setSelectedCategory: (category: string) => void;
  setSearchQuery: (query: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useStore = create<StoreState>((set) => ({
  language: 'en',
  onboardingComplete: false,
  selectedState: '',
  selectedDistrict: '',
  priceData: [],
  selectedCategory: 'all',
  searchQuery: '',
  loading: false,
  error: null,
  setLanguage: (language) => set({ language }),
  setOnboardingComplete: (complete) => set({ onboardingComplete: complete }),
  setSelectedState: (state) => set({ selectedState: state }),
  setSelectedDistrict: (district) => set({ selectedDistrict: district }),
  setPriceData: (data) => set({ priceData: data }),
  setSelectedCategory: (category) => set({ selectedCategory: category }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  reset: () => set({
    onboardingComplete: false,
    selectedState: '',
    selectedDistrict: '',
    priceData: [],
    selectedCategory: 'all',
    searchQuery: '',
    loading: false,
    error: null,
  }),
}));
