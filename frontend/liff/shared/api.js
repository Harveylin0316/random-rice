import { getApiBaseUrl } from './constants.js';

const API_BASE_URL = getApiBaseUrl();

/**
 * 載入篩選選項
 */
export async function loadFilterOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/restaurants/filter-options`);
        if (!response.ok) {
            throw new Error('無法載入篩選選項');
        }
        const data = await response.json();
        if (data.success) {
            return data.options;
        } else {
            throw new Error('篩選選項資料格式錯誤');
        }
    } catch (err) {
        console.error('載入篩選選項錯誤:', err);
        throw err;
    }
}

/**
 * 載入地區選項
 */
export async function loadLocationOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/restaurants/location-options`);
        if (!response.ok) {
            // 嘗試解析錯誤響應以獲取調試信息
            let errorData = null;
            try {
                errorData = await response.json();
            } catch (e) {
                // 如果無法解析 JSON，使用默認錯誤
            }
            
            console.error('載入地區選項錯誤 - 響應狀態:', response.status);
            console.error('載入地區選項錯誤 - 響應數據:', errorData);
            
            // 如果有調試信息，顯示它
            if (errorData && errorData.debug) {
                console.error('調試信息:', errorData.debug);
                console.error('__dirname:', errorData.debug.__dirname);
                console.error('process.cwd():', errorData.debug.processCwd);
                console.error('目錄文件:', errorData.debug.dirFiles);
                console.error('數據庫路徑:', errorData.debug.dbPath);
                console.error('數據庫存在?', errorData.debug.dbExists);
            }
            
            throw new Error('無法載入地區選項');
        }
        const data = await response.json();
        if (data.success) {
            return data.options;
        } else {
            throw new Error('地區選項資料格式錯誤');
        }
    } catch (err) {
        console.error('載入地區選項錯誤:', err);
        throw err;
    }
}

/**
 * 獲取推薦餐廳
 * @param {Object} formData - 表單數據
 * @param {Array<string>} excludeNames - 要排除的餐廳名稱列表
 * @returns {Promise<Array>} 推薦的餐廳列表
 */
export async function fetchRecommendations(formData, excludeNames = []) {
    // 建立查詢參數
    const params = new URLSearchParams();
    
    if (formData.cuisine_style && formData.cuisine_style.length > 0) {
        params.append('cuisine_style', formData.cuisine_style.join(','));
    }
    
    if (formData.type && formData.type.length > 0) {
        params.append('type', formData.type.join(','));
    }
    
    if (formData.budget) {
        params.append('budget', formData.budget);
    }
    
    // 用餐時段篩選參數（只有不是「不限」時才傳遞）
    if (formData.diningTime && formData.diningTime !== 'all') {
        params.append('diningTime', formData.diningTime);
    }
    
    // 距離篩選參數（附近餐廳模式）
    if (formData.userLocation && formData.maxDistance) {
        params.append('locationMode', 'nearby');
        params.append('userLat', formData.userLocation.lat);
        params.append('userLng', formData.userLocation.lng);
        params.append('maxDistance', formData.maxDistance);
    }
    
    // 地區篩選參數（選擇地區模式）
    if (formData.city) {
        params.append('locationMode', 'area');
        params.append('city', formData.city);
        if (formData.district) {
            params.append('district', formData.district);
        }
    }
    
    // 排除已顯示的餐廳
    if (excludeNames && excludeNames.length > 0) {
        params.append('exclude', excludeNames.join(','));
    }
    
    params.append('limit', formData.limit || 5);
    
    // 發送請求
    const url = `${API_BASE_URL}/restaurants/recommend?${params.toString()}`;
    console.log('API 請求 URL:', url);
    console.log('API 請求參數 - diningTime:', formData.diningTime);
    console.log('API 請求參數 - 完整 params:', params.toString());
    
    const response = await fetch(url);
    
    if (!response.ok) {
        throw new Error(`API 請求失敗: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('API 響應:', data);
    
    if (!data.success) {
        throw new Error(data.error || '獲取推薦餐廳失敗');
    }
    
    return data.restaurants || [];
}
