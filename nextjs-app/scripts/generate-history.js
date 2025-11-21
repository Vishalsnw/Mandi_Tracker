const fs = require('fs');
const path = require('path');

const historyDir = path.join(__dirname, '..', 'data', 'price-history');

function generatePriceHistory(basePrice, days = 30) {
  const history = [];
  const today = new Date();
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    const variation = (Math.random() - 0.5) * 0.3;
    const trendFactor = (i / days) * 0.2;
    const modalPrice = Math.round(basePrice * (1 + variation + trendFactor));
    const minPrice = Math.round(modalPrice * (0.7 + Math.random() * 0.15));
    const maxPrice = Math.round(modalPrice * (1.15 + Math.random() * 0.15));
    
    history.push({
      date: date.toISOString().split('T')[0],
      min_price: minPrice,
      max_price: maxPrice,
      modal_price: modalPrice
    });
  }
  
  return history.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

const files = fs.readdirSync(historyDir);

files.forEach(file => {
  if (!file.endsWith('.json')) return;
  
  const filePath = path.join(historyDir, file);
  const content = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(content);
  
  if (data.length === 0) return;
  
  const basePrice = data[0].modal_price || 1000;
  const newHistory = generatePriceHistory(basePrice, 30);
  
  fs.writeFileSync(filePath, JSON.stringify(newHistory, null, 2));
  console.log(`Generated 30-day history for ${file}`);
});

console.log('Price history generation complete!');
