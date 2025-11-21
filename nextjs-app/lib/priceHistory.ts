import fs from 'fs';
import path from 'path';

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

export function savePriceRecord(
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
    console.warn('Unable to save price history (read-only filesystem):', error);
  }
}

export function getPriceHistory(
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
