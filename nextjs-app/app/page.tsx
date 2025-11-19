'use client';

import { useStore } from '@/lib/store';
import OnboardingScreen from '@/components/OnboardingScreen';
import PriceDisplay from '@/components/PriceDisplay';

export default function Home() {
  const { onboardingComplete } = useStore();

  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
      {!onboardingComplete ? <OnboardingScreen /> : <PriceDisplay />}
    </main>
  );
}
