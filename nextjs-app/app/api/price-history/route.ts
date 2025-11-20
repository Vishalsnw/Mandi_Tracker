import { NextRequest, NextResponse } from 'next/server';
import { getPriceHistory, analyzePriceTrend } from '@/lib/priceHistory';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const state = searchParams.get('state');
  const district = searchParams.get('district');
  const commodity = searchParams.get('commodity');
  const days = parseInt(searchParams.get('days') || '30');

  if (!state || !district || !commodity) {
    return NextResponse.json(
      { error: 'Missing required parameters: state, district, commodity' },
      { status: 400 }
    );
  }

  try {
    const history = getPriceHistory(state, district, commodity, days);
    const analysis = history.length > 0 ? analyzePriceTrend(history) : null;

    return NextResponse.json({
      success: true,
      history,
      analysis,
      count: history.length
    });
  } catch (error: any) {
    console.error('Error fetching price history:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error.message },
      { status: 500 }
    );
  }
}
