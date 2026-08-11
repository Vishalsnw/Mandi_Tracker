'use client';

import { useStore } from '@/lib/store';
import OnboardingScreen from '@/components/OnboardingScreen';
import PriceDisplay from '@/components/PriceDisplay';

export default function Home() {
  const { onboardingComplete } = useStore();

  return (
    <main>
      {!onboardingComplete ? <OnboardingScreen /> : <PriceDisplay />}
    </main>
  );
}
