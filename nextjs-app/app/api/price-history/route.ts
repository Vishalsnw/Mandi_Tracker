import { NextRequest, NextResponse } from 'next/server';
import { getPriceHistory, savePriceRecord } from '@/lib/priceHistory';

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
    const history = await getPriceHistory(commodity, state, district, days);

    return NextResponse.json({
      success: true,
      history,
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

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    
    await savePriceRecord(
      data.state,
      data.district,
      data.commodity,
      data.min_price,
      data.max_price,
      data.modal_price
    );
    
    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json(
      { error: 'Error saving price record', message: error.message },
      { status: 500 }
    );
  }
}
