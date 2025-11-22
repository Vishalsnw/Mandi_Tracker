import { NextRequest, NextResponse } from 'next/server';
import { saveUserCommodityCheck, getUserHistory, getCommodityStats } from '@/lib/userHistory';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const type = searchParams.get('type') || 'history';
  const limit = parseInt(searchParams.get('limit') || '50');

  try {
    if (type === 'stats') {
      const stats = getCommodityStats();
      return NextResponse.json({
        success: true,
        stats
      });
    } else {
      const history = getUserHistory(limit);
      return NextResponse.json({
        success: true,
        history,
        count: history.length
      });
    }
  } catch (error: any) {
    console.error('Error fetching user history:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error.message },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    
    saveUserCommodityCheck({
      commodity: data.commodity,
      commodity_hi: data.commodity_hi,
      state: data.state,
      district: data.district,
      market: data.market,
      min_price: data.min_price,
      max_price: data.max_price,
      modal_price: data.modal_price
    });
    
    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json(
      { error: 'Error saving user history', message: error.message },
      { status: 500 }
    );
  }
}
