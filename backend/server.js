const express = require('express');
const cors = require('cors');
const path = require('path');
const restaurantRoutes = require('./routes/restaurants');

const app = express();
const PORT = process.env.PORT || 3000;

// 中間件
app.use(cors()); // 允許跨域請求
app.use(express.json()); // 解析 JSON 請求體
app.use(express.urlencoded({ extended: true })); // 解析 URL 編碼請求體

// API 路由（必須在靜態文件之前）
app.use('/api/restaurants', restaurantRoutes);

// API 文檔路由
app.get('/api', (req, res) => {
  res.json({
    message: '今天吃什麼 - 餐廳推薦 API',
    version: '1.0.0',
    endpoints: {
      'GET /api/restaurants/recommend': '推薦餐廳',
      'GET /api/restaurants/filter-options': '獲取篩選選項',
      'GET /api/restaurants/all': '獲取所有餐廳'
    }
  });
});

// 提供靜態文件（前端頁面）- 放在最後，作為 fallback
app.use(express.static(path.join(__dirname, '../frontend')));

// 404 處理
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: '找不到指定的路由'
  });
});

// 錯誤處理
app.use((err, req, res, next) => {
  console.error('伺服器錯誤:', err);
  res.status(500).json({
    success: false,
    error: '伺服器內部錯誤',
    message: err.message
  });
});

// 啟動伺服器
app.listen(PORT, () => {
  console.log(`🚀 伺服器運行在 http://localhost:${PORT}`);
  console.log(`📋 API 文檔: http://localhost:${PORT}/`);
  console.log(`\n可用端點:`);
  console.log(`  GET /api/restaurants/recommend - 推薦餐廳`);
  console.log(`  GET /api/restaurants/filter-options - 獲取篩選選項`);
  console.log(`  GET /api/restaurants/all - 獲取所有餐廳`);
});
