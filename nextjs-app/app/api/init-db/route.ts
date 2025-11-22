import { NextResponse } from 'next/server';
import { initializeDatabase } from '@/lib/db';

export async function GET() {
  try {
    const success = await initializeDatabase();
    
    if (success) {
      return NextResponse.json({
        success: true,
        message: 'Database initialized successfully'
      });
    } else {
      return NextResponse.json({
        success: false,
        message: 'No database connection available, using file system storage'
      });
    }
  } catch (error: any) {
    console.error('Error initializing database:', error);
    return NextResponse.json(
      { error: 'Error initializing database', message: error.message },
      { status: 500 }
    );
  }
}
