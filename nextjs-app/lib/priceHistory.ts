import fs from 'fs';
import path from 'path';
import { getPool } from './db';

interface PriceHistoryRecord {
  date: string;
  min_price: number;
  max_price: number;
  modal_price: number;
}

const HISTORY_DIR = path.join(process.cwd(), 'data', 'price-history');

function getFileName(state: string, district: string, commodity: string): string {
  const sanitized = `${state}_${district}_${commodity}`
    .toLowerCase()
    .replace(/[^a-z0-9_]/g, '_')
    .replace(/_+/g, '_');
  return `${sanitized}.json`;
}

async function savePriceRecordToDatabase(
  state: string,
  district: string,
  commodity: string,
  minPrice: number,
  maxPrice: number,
  modalPrice: number
): Promise<boolean> {
  const pool = getPool();
  if (!pool) return false;
  
  try {
    const today = new Date().toISOString().split('T')[0];
    
    await pool.query(
      `INSERT INTO price_history (state, district, commodity, date, min_price, max_price, modal_price)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       ON CONFLICT (state, district, commodity, date)
       DO UPDATE SET 
         min_price = EXCLUDED.min_price,
         max_price = EXCLUDED.max_price,
         modal_price = EXCLUDED.modal_price`,
      [state, district, commodity, today, minPrice, maxPrice, modalPrice]
    );
    
    return true;
  } catch (error) {
    console.error('Database save error:', error);
    return false;
  }
}

function savePriceRecordToFile(
  state: string,
  district: string,
  commodity: string,
  minPrice: number,
  maxPrice: number,
  modalPrice: number
): void {
  try {
    if (!fs.existsSync(HISTORY_DIR)) {
      fs.mkdirSync(HISTORY_DIR, { recursive: true });
    }
    
    const fileName = getFileName(state, district, commodity);
    const filePath = path.join(HISTORY_DIR, fileName);
    
    let history: PriceHistoryRecord[] = [];
    if (fs.existsSync(filePath)) {
      try {
        const content = fs.readFileSync(filePath, 'utf-8');
        history = JSON.parse(content);
      } catch (error) {
        history = [];
      }
    }
    
    const today = new Date().toISOString().split('T')[0];
    const existingIndex = history.findIndex(record => record.date === today);
    
    const newRecord: PriceHistoryRecord = {
      date: today,
      min_price: minPrice,
      max_price: maxPrice,
      modal_price: modalPrice,
    };
    
    if (existingIndex >= 0) {
      history[existingIndex] = newRecord;
    } else {
      history.push(newRecord);
    }
    
    history.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    history = history.slice(0, 90);
    
    fs.writeFileSync(filePath, JSON.stringify(history, null, 2));
  } catch (error) {
    console.warn('Unable to save price history to file:', error);
  }
}

export async function savePriceRecord(
  state: string,
  district: string,
  commodity: string,
  minPrice: number,
  maxPrice: number,
  modalPrice: number
): Promise<void> {
  const dbSuccess = await savePriceRecordToDatabase(state, district, commodity, minPrice, maxPrice, modalPrice);
  
  if (!dbSuccess) {
    savePriceRecordToFile(state, district, commodity, minPrice, maxPrice, modalPrice);
  }
}

async function getPriceHistoryFromDatabase(
  commodity: string,
  state: string,
  district: string,
  days: number = 30
): Promise<PriceHistoryRecord[] | null> {
  const pool = getPool();
  if (!pool) return null;
  
  try {
    const result = await pool.query(
      `SELECT date::text, min_price, max_price, modal_price
       FROM price_history
       WHERE state = $1 AND district = $2 AND commodity = $3
       ORDER BY date DESC
       LIMIT $4`,
      [state, district, commodity, days]
    );
    
    return result.rows.map((row: any) => ({
      date: row.date,
      min_price: parseFloat(row.min_price),
      max_price: parseFloat(row.max_price),
      modal_price: parseFloat(row.modal_price),
    }));
  } catch (error) {
    console.error('Database query error:', error);
    return null;
  }
}

function getPriceHistoryFromFile(
  commodity: string,
  state: string,
  district: string,
  days: number = 30
): PriceHistoryRecord[] {
  try {
    const fileName = getFileName(state, district, commodity);
    const filePath = path.join(HISTORY_DIR, fileName);
    
    if (!fs.existsSync(filePath)) {
      return [];
    }
    
    const content = fs.readFileSync(filePath, 'utf-8');
    const history: PriceHistoryRecord[] = JSON.parse(content);
    
    history.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    
    return history.slice(0, days);
  } catch (error) {
    return [];
  }
}

export async function getPriceHistory(
  commodity: string,
  state: string,
  district: string,
  days: number = 30
): Promise<PriceHistoryRecord[]> {
  const dbHistory = await getPriceHistoryFromDatabase(commodity, state, district, days);
  
  if (dbHistory !== null) {
    return dbHistory;
  }
  
  return getPriceHistoryFromFile(commodity, state, district, days);
}
