import { Pool } from 'pg';

let pool: Pool | null = null;

export function getPool(): Pool | null {
  if (pool) {
    return pool;
  }

  const databaseUrl = process.env.DATABASE_URL || process.env.POSTGRES_URL;
  
  if (!databaseUrl) {
    return null;
  }

  try {
    const isProduction = process.env.VERCEL || process.env.NODE_ENV === 'production';
    
    pool = new Pool({
      connectionString: databaseUrl,
      max: isProduction ? 1 : 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 10000,
      ssl: isProduction ? { rejectUnauthorized: false } : undefined,
    });

    pool.on('error', (err) => {
      console.error('Unexpected database pool error:', err);
    });

    return pool;
  } catch (error) {
    console.error('Failed to create database pool:', error);
    return null;
  }
}

export async function initializeDatabase(): Promise<boolean> {
  const pool = getPool();
  
  if (!pool) {
    console.log('No database connection available');
    return false;
  }

  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS price_history (
        id SERIAL PRIMARY KEY,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        commodity TEXT NOT NULL,
        date DATE NOT NULL,
        min_price NUMERIC(10, 2) NOT NULL,
        max_price NUMERIC(10, 2) NOT NULL,
        modal_price NUMERIC(10, 2) NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(state, district, commodity, date)
      )
    `);

    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_price_history_lookup 
      ON price_history(state, district, commodity, date DESC)
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS user_commodity_history (
        id SERIAL PRIMARY KEY,
        commodity TEXT NOT NULL,
        commodity_hi TEXT,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        market TEXT NOT NULL,
        modal_price NUMERIC(10, 2) NOT NULL,
        min_price NUMERIC(10, 2) NOT NULL,
        max_price NUMERIC(10, 2) NOT NULL,
        checked_at TIMESTAMP DEFAULT NOW()
      )
    `);

    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_user_history_commodity 
      ON user_commodity_history(commodity)
    `);

    await pool.query(`
      CREATE INDEX IF NOT EXISTS idx_user_history_checked_at 
      ON user_commodity_history(checked_at DESC)
    `);

    console.log('Database tables initialized successfully');
    return true;
  } catch (error) {
    console.error('Error initializing database:', error);
    throw error;
  }
}
