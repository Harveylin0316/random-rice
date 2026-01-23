// Netlify Function for restaurant API
const fs = require('fs');
const path = require('path');
const { recommendRestaurants, getFilterOptions, getLocationOptions } = require('../../backend/utils/recommendation');

// 覆蓋 loadRestaurantDatabase 函數以使用正確的路徑
// 在 Netlify Functions 環境中，需要從函數文件位置計算相對路徑
function loadRestaurantDatabase() {
  // 在 Netlify Functions 中，__dirname 指向函數文件所在目錄
  // 需要向上兩級到達項目根目錄
  const dbPath = path.join(__dirname, '../../../restaurants_database.json');
  
  // 如果找不到，嘗試其他可能的路徑
  if (!fs.existsSync(dbPath)) {
    // 嘗試從當前目錄向上查找
    const altPath = path.join(process.cwd(), 'restaurants_database.json');
    if (fs.existsSync(altPath)) {
      const data = fs.readFileSync(altPath, 'utf-8');
      return JSON.parse(data);
    }
    throw new Error(`Database file not found. Tried: ${dbPath}, ${altPath}`);
  }
  
  const data = fs.readFileSync(dbPath, 'utf-8');
  return JSON.parse(data);
}

exports.handler = async (event, context) => {
  // 設置 CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json'
  };

  // 處理 OPTIONS 請求（CORS preflight）
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  // 只處理 GET 請求
  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ success: false, error: 'Method not allowed' })
    };
  }

  try {
    // 從 event.path 提取路徑，處理不同的路徑格式
    let apiPath = event.path || '';
    
    // 移除 Netlify Functions 前綴和查詢參數
    if (apiPath.includes('/.netlify/functions/restaurants')) {
      apiPath = apiPath.replace('/.netlify/functions/restaurants', '');
    } else if (apiPath.includes('/api/restaurants')) {
      apiPath = apiPath.replace('/api/restaurants', '');
    }
    
    // 移除查詢參數部分
    if (apiPath.includes('?')) {
      apiPath = apiPath.split('?')[0];
    }
    
    // 如果路徑為空，檢查是否有查詢參數來判斷是推薦請求
    // 或者默認使用 /recommend
    if (!apiPath || apiPath === '/') {
      // 如果有查詢參數，可能是推薦請求
      const queryParams = event.queryStringParameters || {};
      if (Object.keys(queryParams).length > 0) {
        apiPath = '/recommend';
      } else {
        // 根據原始請求路徑判斷
        const rawPath = event.path || '';
        if (rawPath.includes('filter-options')) {
          apiPath = '/filter-options';
        } else if (rawPath.includes('location-options')) {
          apiPath = '/location-options';
        } else if (rawPath.includes('/all')) {
          apiPath = '/all';
        } else {
          apiPath = '/recommend';
        }
      }
    }
    
    const queryParams = event.queryStringParameters || {};

    // 路由處理
    if (apiPath === '/recommend' || apiPath === '') {
      // 推薦餐廳
      const filters = {};
      
      if (queryParams.cuisine_style) {
        filters.cuisine_style = queryParams.cuisine_style.split(',').map(s => s.trim());
      }
      
      if (queryParams.type) {
        filters.type = queryParams.type.split(',').map(s => s.trim());
      }
      
      if (queryParams.budget) {
        filters.budget = queryParams.budget;
      }
      
      if (queryParams.userLat && queryParams.userLng && queryParams.maxDistance) {
        filters.userLocation = {
          lat: parseFloat(queryParams.userLat),
          lng: parseFloat(queryParams.userLng)
        };
        filters.maxDistance = parseFloat(queryParams.maxDistance);
      }
      
      if (queryParams.city) {
        filters.city = queryParams.city;
        if (queryParams.district) {
          filters.district = queryParams.district;
        }
      }
      
      if (queryParams.exclude) {
        filters.exclude = queryParams.exclude.split(',').map(s => s.trim());
      }
      
      const limit = parseInt(queryParams.limit) || 5;
      const recommendations = recommendRestaurants(filters, limit);
      
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          count: recommendations.length,
          filters: filters,
          restaurants: recommendations
        })
      };
    } else if (apiPath === '/filter-options') {
      // 獲取篩選選項
      const options = getFilterOptions();
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          options: options
        })
      };
    } else if (apiPath === '/location-options') {
      // 獲取地區選項
      const options = getLocationOptions();
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          options: options
        })
      };
    } else if (apiPath === '/all') {
      // 獲取所有餐廳
      const data = loadRestaurantDatabase();
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          count: data.restaurants.length,
          restaurants: data.restaurants
        })
      };
    } else {
      return {
        statusCode: 404,
        headers,
        body: JSON.stringify({
          success: false,
          error: 'Not found'
        })
      };
    }
  } catch (error) {
    console.error('Function error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: 'Internal server error',
        message: error.message
      })
    };
  }
};
