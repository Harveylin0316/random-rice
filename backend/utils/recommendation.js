const fs = require('fs');
const path = require('path');

/**
 * 載入餐廳資料庫
 */
function loadRestaurantDatabase() {
  const dbPath = path.join(__dirname, '../../restaurants_database.json');
  const data = fs.readFileSync(dbPath, 'utf-8');
  return JSON.parse(data);
}

/**
 * 計算兩點之間的距離（使用 Haversine 公式）
 * @param {number} lat1 - 起點緯度
 * @param {number} lng1 - 起點經度
 * @param {number} lat2 - 終點緯度
 * @param {number} lng2 - 終點經度
 * @returns {number} 距離（公里）
 */
function calculateDistance(lat1, lng1, lat2, lng2) {
  const R = 6371; // 地球半徑（公里）
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * 解析預算區間字串為數字範圍
 * @param {string} budgetStr - 預算字串，例如 "500-800", "2000以上"
 * @returns {Object} { min: number, max: number } 或 null
 */
function parseBudgetRange(budgetStr) {
  if (!budgetStr) return null;
  
  // 處理 "XXX-XXX" 格式
  const rangeMatch = budgetStr.match(/(\d+)-(\d+)/);
  if (rangeMatch) {
    return {
      min: parseInt(rangeMatch[1]),
      max: parseInt(rangeMatch[2])
    };
  }
  
  // 處理 "XXX以上" 格式
  const aboveMatch = budgetStr.match(/(\d+)以上/);
  if (aboveMatch) {
    return {
      min: parseInt(aboveMatch[1]),
      max: Infinity
    };
  }
  
  // 處理 "XXX以下" 格式
  const belowMatch = budgetStr.match(/(\d+)以下/);
  if (belowMatch) {
    return {
      min: 0,
      max: parseInt(belowMatch[1])
    };
  }
  
  return null;
}

/**
 * 檢查餐廳是否符合預算條件
 * @param {Object} restaurant - 餐廳物件
 * @param {string} userBudget - 使用者選擇的預算區間
 * @returns {boolean}
 */
function matchesBudget(restaurant, userBudget) {
  const restaurantBudget = restaurant.budget;
  
  // 如果餐廳沒有預算資料，跳過預算篩選
  if (!restaurantBudget) return true;
  
  // 如果使用者沒有選擇預算，不篩選
  if (!userBudget || userBudget === 'all') return true;
  
  const restaurantRange = parseBudgetRange(restaurantBudget);
  const userRange = parseBudgetRange(userBudget);
  
  if (!restaurantRange || !userRange) return true;
  
  // 檢查兩個範圍是否有重疊
  return restaurantRange.min <= userRange.max && restaurantRange.max >= userRange.min;
}

/**
 * 檢查餐廳是否符合料理風格條件
 * @param {Object} restaurant - 餐廳物件
 * @param {Array<string>} userCuisines - 使用者選擇的料理風格陣列
 * @returns {boolean}
 */
function matchesCuisineStyle(restaurant, userCuisines) {
  if (!userCuisines || userCuisines.length === 0) return true;
  
  const restaurantCuisines = restaurant.cuisine_style || [];
  
  // 檢查是否有任何一個使用者選擇的料理風格符合
  return userCuisines.some(cuisine => restaurantCuisines.includes(cuisine));
}

/**
 * 檢查餐廳是否符合類型條件
 * @param {Object} restaurant - 餐廳物件
 * @param {Array<string>} userTypes - 使用者選擇的餐廳類型陣列
 * @returns {boolean}
 */
function matchesType(restaurant, userTypes) {
  if (!userTypes || userTypes.length === 0) return true;
  
  const restaurantTypes = restaurant.type || [];
  
  // 檢查是否有任何一個使用者選擇的類型符合
  return userTypes.some(type => restaurantTypes.includes(type));
}

/**
 * 推薦餐廳
 * @param {Object} filters - 篩選條件
 * @param {number} limit - 返回的餐廳數量上限（預設5）
 * @returns {Array} 推薦的餐廳陣列
 */
function recommendRestaurants(filters = {}, limit = 5) {
  const data = loadRestaurantDatabase();
  let restaurants = [...data.restaurants];
  
  // 篩選：料理風格
  if (filters.cuisine_style) {
    restaurants = restaurants.filter(r => matchesCuisineStyle(r, filters.cuisine_style));
  }
  
  // 篩選：餐廳類型
  if (filters.type) {
    restaurants = restaurants.filter(r => matchesType(r, filters.type));
  }
  
  // 篩選：預算
  if (filters.budget) {
    restaurants = restaurants.filter(r => matchesBudget(r, filters.budget));
  }
  
  // 距離篩選（需要座標資料）- 附近餐廳模式
  if (filters.userLocation && filters.maxDistance) {
    restaurants = restaurants.filter(r => {
      if (!r.coordinates || !r.coordinates.lat || !r.coordinates.lng) {
        return true; // 如果餐廳沒有座標，不進行距離篩選
      }
      const distance = calculateDistance(
        filters.userLocation.lat,
        filters.userLocation.lng,
        r.coordinates.lat,
        r.coordinates.lng
      );
      return distance <= filters.maxDistance;
    });
  }
  
  // 地區篩選（縣市和行政區）- 選擇地區模式
  if (filters.city) {
    restaurants = restaurants.filter(r => {
      const restaurantCity = r.city;
      const restaurantDistrict = r.district;
      
      // 如果餐廳沒有縣市資料，不匹配任何地區篩選
      if (!restaurantCity) return false;
      
      // 檢查縣市是否匹配
      if (restaurantCity !== filters.city) return false;
      
      // 如果指定了行政區，必須有行政區資料且匹配
      if (filters.district) {
        // 如果餐廳沒有行政區資料，不匹配
        if (!restaurantDistrict) return false;
        return restaurantDistrict === filters.district;
      }
      
      // 只指定縣市，匹配該縣市的所有餐廳（包括沒有行政區的）
      return true;
    });
  }
  
  // 排除已顯示的餐廳
  if (filters.exclude && filters.exclude.length > 0) {
    restaurants = restaurants.filter(r => !filters.exclude.includes(r.name));
  }
  
  // TODO: 用餐時段篩選（需要營業時間資料）
  // TODO: 線上訂位篩選（需要訂位資料）
  
  // 隨機排序並返回指定數量
  const shuffled = restaurants.sort(() => Math.random() - 0.5);
  return shuffled.slice(0, limit);
}

/**
 * 獲取所有可用的篩選選項（用於前端下拉選單）
 * @returns {Object} 包含所有可選項的物件
 */
function getFilterOptions() {
  const data = loadRestaurantDatabase();
  const cuisines = new Set();
  const types = new Set();
  const budgets = new Set();
  
  data.restaurants.forEach(restaurant => {
    (restaurant.cuisine_style || []).forEach(c => cuisines.add(c));
    (restaurant.type || []).forEach(t => types.add(t));
    if (restaurant.budget) budgets.add(restaurant.budget);
  });
  
  // 過濾掉「其他」選項，以及從料理風格中移除「火鍋」、「燒肉」、「酒吧」（這些應該在餐廳類型中）
  const excludedCuisines = ['其他', '火鍋', '燒肉', '酒吧'];
  const filteredCuisines = Array.from(cuisines).filter(c => !excludedCuisines.includes(c)).sort();
  // 過濾掉「其他」和「一般餐廳」選項
  const excludedTypes = ['其他', '一般餐廳'];
  const filteredTypes = Array.from(types).filter(t => !excludedTypes.includes(t)).sort();
  
  // 預算排序：按照價格從低到高
  const sortedBudgets = Array.from(budgets).sort((a, b) => {
    const rangeA = parseBudgetRange(a);
    const rangeB = parseBudgetRange(b);
    
    // 如果無法解析，放在最後
    if (!rangeA && !rangeB) return 0;
    if (!rangeA) return 1;
    if (!rangeB) return -1;
    
    // 按照最小值排序
    if (rangeA.min !== rangeB.min) {
      return rangeA.min - rangeB.min;
    }
    
    // 如果最小值相同，按照最大值排序
    // 處理 Infinity 的情況
    if (rangeA.max === Infinity && rangeB.max === Infinity) return 0;
    if (rangeA.max === Infinity) return 1; // Infinity 放在最後
    if (rangeB.max === Infinity) return -1;
    
    return rangeA.max - rangeB.max;
  });
  
  return {
    cuisine_style: filteredCuisines,
    type: filteredTypes,
    budget: sortedBudgets
  };
}

/**
 * 獲取所有可用的地區選項（縣市和行政區）
 * @returns {Object} 包含縣市列表和縣市-行政區對應關係的物件
 */
function getLocationOptions() {
  const data = loadRestaurantDatabase();
  const cities = new Set();
  const districtsByCity = {};
  
  data.restaurants.forEach(restaurant => {
    const city = restaurant.city;
    const district = restaurant.district;
    
    if (city) {
      cities.add(city);
      
      if (!districtsByCity[city]) {
        districtsByCity[city] = new Set();
      }
      
      if (district) {
        districtsByCity[city].add(district);
      }
    }
  });
  
  // 轉換為陣列並排序
  const citiesArray = Array.from(cities).sort();
  const districtsObject = {};
  
  citiesArray.forEach(city => {
    if (districtsByCity[city]) {
      districtsObject[city] = Array.from(districtsByCity[city]).sort();
    } else {
      districtsObject[city] = [];
    }
  });
  
  return {
    cities: citiesArray,
    districts: districtsObject
  };
}

module.exports = {
  recommendRestaurants,
  getFilterOptions,
  getLocationOptions,
  loadRestaurantDatabase
};
