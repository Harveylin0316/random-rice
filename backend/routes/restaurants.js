const express = require('express');
const router = express.Router();
const { recommendRestaurants, getFilterOptions } = require('../utils/recommendation');

/**
 * GET /api/restaurants/recommend
 * 推薦餐廳
 * 
 * Query Parameters:
 * - cuisine_style: 料理風格（可多選，用逗號分隔）
 * - type: 餐廳類型（可多選，用逗號分隔）
 * - budget: 預算區間
 * - limit: 返回數量（預設5）
 * 
 * Example:
 * GET /api/restaurants/recommend?cuisine_style=韓式,日式&type=燒肉&budget=500-800&limit=5
 */
router.get('/recommend', (req, res) => {
  try {
    const filters = {};
    
    // 解析料理風格（可多選）
    if (req.query.cuisine_style) {
      filters.cuisine_style = req.query.cuisine_style.split(',').map(s => s.trim());
    }
    
    // 解析餐廳類型（可多選）
    if (req.query.type) {
      filters.type = req.query.type.split(',').map(s => s.trim());
    }
    
    // 預算
    if (req.query.budget) {
      filters.budget = req.query.budget;
    }
    
    // 距離篩選（需要使用者位置和最大距離）
    if (req.query.userLat && req.query.userLng && req.query.maxDistance) {
      filters.userLocation = {
        lat: parseFloat(req.query.userLat),
        lng: parseFloat(req.query.userLng)
      };
      filters.maxDistance = parseFloat(req.query.maxDistance);
    }
    
    // 返回數量
    const limit = parseInt(req.query.limit) || 5;
    
    // 獲取推薦餐廳
    const recommendations = recommendRestaurants(filters, limit);
    
    res.json({
      success: true,
      count: recommendations.length,
      filters: filters,
      restaurants: recommendations
    });
  } catch (error) {
    console.error('推薦餐廳時發生錯誤:', error);
    res.status(500).json({
      success: false,
      error: '獲取推薦餐廳時發生錯誤',
      message: error.message
    });
  }
});

/**
 * GET /api/restaurants/filter-options
 * 獲取所有可用的篩選選項
 */
router.get('/filter-options', (req, res) => {
  try {
    const options = getFilterOptions();
    res.json({
      success: true,
      options: options
    });
  } catch (error) {
    console.error('獲取篩選選項時發生錯誤:', error);
    res.status(500).json({
      success: false,
      error: '獲取篩選選項時發生錯誤',
      message: error.message
    });
  }
});

/**
 * GET /api/restaurants/all
 * 獲取所有餐廳（用於測試或管理）
 */
router.get('/all', (req, res) => {
  try {
    const { loadRestaurantDatabase } = require('../utils/recommendation');
    const data = loadRestaurantDatabase();
    
    res.json({
      success: true,
      count: data.restaurants.length,
      restaurants: data.restaurants
    });
  } catch (error) {
    console.error('獲取所有餐廳時發生錯誤:', error);
    res.status(500).json({
      success: false,
      error: '獲取餐廳資料時發生錯誤',
      message: error.message
    });
  }
});

module.exports = router;
