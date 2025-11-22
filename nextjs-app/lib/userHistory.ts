import fs from 'fs';
import path from 'path';
import { getPool } from './db';

export interface UserHistoryRecord {
  timestamp: string;
  commodity: string;
  commodity_hi?: string;
  state: string;
  district: string;
  market: string;
  modal_price: number;
  min_price: number;
  max_price: number;
}

const HISTORY_FILE = path.join(process.cwd(), 'data', 'user-commodity-history.json');

async function saveUserCommodityCheckToDatabase(record: Omit<UserHistoryRecord, 'timestamp'>): Promise<boolean> {
  const pool = getPool();
  if (!pool) return false;
  
  try {
    await pool.query(
      `INSERT INTO user_commodity_history (commodity, commodity_hi, state, district, market, modal_price, min_price, max_price)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
      [record.commodity, record.commodity_hi || null, record.state, record.district, record.market, record.modal_price, record.min_price, record.max_price]
    );
    
    return true;
  } catch (error) {
    console.error('Database save error:', error);
    return false;
  }
}

function saveUserCommodityCheckToFile(record: Omit<UserHistoryRecord, 'timestamp'>): void {
  try {
    const dataDir = path.join(process.cwd(), 'data');
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
    
    let history: UserHistoryRecord[] = [];
    if (fs.existsSync(HISTORY_FILE)) {
      try {
        const content = fs.readFileSync(HISTORY_FILE, 'utf-8');
        history = JSON.parse(content);
      } catch (error) {
        history = [];
      }
    }
    
    const newRecord: UserHistoryRecord = {
      timestamp: new Date().toISOString(),
      ...record
    };
    
    history.unshift(newRecord);
    
    history = history.slice(0, 500);
    
    fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));
  } catch (error) {
    console.warn('Unable to save user history to file:', error);
  }
}

export async function saveUserCommodityCheck(record: Omit<UserHistoryRecord, 'timestamp'>): Promise<void> {
  const dbSuccess = await saveUserCommodityCheckToDatabase(record);
  
  if (!dbSuccess) {
    saveUserCommodityCheckToFile(record);
  }
}

async function getUserHistoryFromDatabase(limit: number = 50): Promise<UserHistoryRecord[] | null> {
  const pool = getPool();
  if (!pool) return null;
  
  try {
    const result = await pool.query(
      `SELECT 
        checked_at::text as timestamp,
        commodity,
        commodity_hi,
        state,
        district,
        market,
        modal_price,
        min_price,
        max_price
       FROM user_commodity_history
       ORDER BY checked_at DESC
       LIMIT $1`,
      [limit]
    );
    
    return result.rows.map(row => ({
      timestamp: row.timestamp,
      commodity: row.commodity,
      commodity_hi: row.commodity_hi,
      state: row.state,
      district: row.district,
      market: row.market,
      modal_price: parseFloat(row.modal_price),
      min_price: parseFloat(row.min_price),
      max_price: parseFloat(row.max_price),
    }));
  } catch (error) {
    console.error('Database query error:', error);
    return null;
  }
}

function getUserHistoryFromFile(limit: number = 50): UserHistoryRecord[] {
  try {
    if (!fs.existsSync(HISTORY_FILE)) {
      return [];
    }
    
    const content = fs.readFileSync(HISTORY_FILE, 'utf-8');
    const history: UserHistoryRecord[] = JSON.parse(content);
    
    return history.slice(0, limit);
  } catch (error) {
    return [];
  }
}

export async function getUserHistory(limit: number = 50): Promise<UserHistoryRecord[]> {
  const dbHistory = await getUserHistoryFromDatabase(limit);
  
  if (dbHistory !== null) {
    return dbHistory;
  }
  
  return getUserHistoryFromFile(limit);
}

export async function getCommodityStats(): Promise<{ commodity: string; count: number }[]> {
  const pool = getPool();
  
  if (pool) {
    try {
      const result = await pool.query(
        `SELECT commodity, COUNT(*) as count
         FROM user_commodity_history
         GROUP BY commodity
         ORDER BY count DESC`
      );
      
      return result.rows.map(row => ({
        commodity: row.commodity,
        count: parseInt(row.count)
      }));
    } catch (error) {
      console.error('Database query error:', error);
    }
  }
  
  try {
    const history = await getUserHistory(500);
    
    const stats = history.reduce((acc, record) => {
      const key = record.commodity;
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return Object.entries(stats)
      .map(([commodity, count]) => ({ commodity, count }))
      .sort((a, b) => b.count - a.count);
  } catch (error) {
    return [];
  }
}
