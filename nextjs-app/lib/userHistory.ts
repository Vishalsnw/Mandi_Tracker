import fs from 'fs';
import path from 'path';

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

export function saveUserCommodityCheck(record: Omit<UserHistoryRecord, 'timestamp'>): void {
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
    console.warn('Unable to save user history (read-only filesystem):', error);
  }
}

export function getUserHistory(limit: number = 50): UserHistoryRecord[] {
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

export function getCommodityStats(): { commodity: string; count: number }[] {
  try {
    const history = getUserHistory(500);
    
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
