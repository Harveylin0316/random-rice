// 導入共享模組
import { 
    FRONTEND_CUISINE_CATEGORIES, 
    FRONTEND_TYPE_CATEGORIES,
    cuisineIcons,
    typeIcons,
    getApiBaseUrl
} from './shared/constants.js';
import { 
    loadFilterOptions as apiLoadFilterOptions,
    loadLocationOptions as apiLoadLocationOptions,
    fetchRecommendations
} from './shared/api.js';
import { filterGeneralTags } from './shared/utils.js';

// API 基礎 URL
const API_BASE_URL = getApiBaseUrl();

// DOM 元素
const form = document.getElementById('recommendationForm');
const submitBtn = document.getElementById('submitBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const restaurantList = document.getElementById('restaurantList');
const resultCount = document.getElementById('resultCount');
const resetBtn = document.getElementById('resetBtn');
const getLocationBtn = document.getElementById('getLocationBtn');
const locationStatus = document.getElementById('locationStatus');
const citySelect = document.getElementById('citySelect');
const districtSelect = document.getElementById('districtSelect');
const nearbyOptions = document.getElementById('nearbyOptions');
const areaOptions = document.getElementById('areaOptions');

// 使用者位置和交通方式
let userLocation = null;

// 記錄已顯示的餐廳名稱（用於排除重複）
let displayedRestaurants = [];

// 篩選選項資料
let filterOptions = {
    cuisine_style: [],
    type: [],
    budget: []
};

// 地區選項資料
let locationOptions = {
    cities: [],
    districts: {}  // { city: [districts] }
};

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadFilterOptions();
        await loadLocationOptions();
        renderForm();
        setupLocationModeHandlers();
        
        // 初始化顯示「選擇地區」選項（預設選項，避免自動獲取位置導致的錯誤）
        const areaOptions = document.getElementById('areaOptions');
        const nearbyOptions = document.getElementById('nearbyOptions');
        if (areaOptions) areaOptions.style.display = 'block';
        if (nearbyOptions) nearbyOptions.style.display = 'none';
        
        // 不再自動獲取用戶位置，讓用戶主動選擇
        // 這樣可以避免間歇性的地理位置錯誤，提升用戶體驗
        // autoGetUserLocation(); // 已移除自動獲取
    } catch (err) {
        showError('載入篩選選項失敗，請重新整理頁面');
        console.error('載入篩選選項錯誤:', err);
    }
});

// 載入篩選選項
async function loadFilterOptions() {
    try {
        const options = await apiLoadFilterOptions();
        filterOptions = options;
        // 確保料理風格只包含前端定義的7個分類
        filterOptions.cuisine_style = filterOptions.cuisine_style.filter(
            cuisine => FRONTEND_CUISINE_CATEGORIES.includes(cuisine)
        );
        // 如果API返回的分類不完整，使用前端定義的完整列表
        if (filterOptions.cuisine_style.length !== FRONTEND_CUISINE_CATEGORIES.length) {
            filterOptions.cuisine_style = [...FRONTEND_CUISINE_CATEGORIES];
        }
        // 確保餐廳類型只包含前端定義的5個分類
        filterOptions.type = filterOptions.type.filter(
            type => FRONTEND_TYPE_CATEGORIES.includes(type)
        );
        // 如果API返回的分類不完整，使用前端定義的完整列表
        if (filterOptions.type.length !== FRONTEND_TYPE_CATEGORIES.length) {
            filterOptions.type = [...FRONTEND_TYPE_CATEGORIES];
        }
    } catch (err) {
        console.error('載入篩選選項錯誤:', err);
        // 如果API載入失敗，使用前端定義的分類
        filterOptions.cuisine_style = [...FRONTEND_CUISINE_CATEGORIES];
        filterOptions.type = [...FRONTEND_TYPE_CATEGORIES];
        throw err;
    }
}

// 載入地區選項
async function loadLocationOptions() {
    try {
        locationOptions = await apiLoadLocationOptions();
        renderCityOptions();
    } catch (err) {
        console.error('載入地區選項錯誤:', err);
        throw err;
    }
}

// 渲染縣市選項
function renderCityOptions() {
    if (!citySelect) return;
    
    citySelect.innerHTML = '<option value="">不限</option>';
    locationOptions.cities.forEach(city => {
        const option = document.createElement('option');
        option.value = city;
        option.textContent = city;
        citySelect.appendChild(option);
    });
}

// 渲染行政區選項
function renderDistrictOptions(city) {
    if (!districtSelect) return;
    
    districtSelect.innerHTML = '<option value="">不限</option>';
    
    if (!city || !locationOptions.districts[city]) {
        districtSelect.disabled = true;
        return;
    }
    
    districtSelect.disabled = false;
    locationOptions.districts[city].forEach(district => {
        const option = document.createElement('option');
        option.value = district;
        option.textContent = district;
        districtSelect.appendChild(option);
    });
}

// 設置地區模式處理器
function setupLocationModeHandlers() {
    // 地區模式選擇
    const locationModeRadios = document.querySelectorAll('input[name="locationMode"]');
    locationModeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            const mode = radio.value;
            
            // 隱藏所有選項
            if (nearbyOptions) nearbyOptions.style.display = 'none';
            if (areaOptions) areaOptions.style.display = 'none';
            
            // 顯示對應選項
            if (mode === 'nearby' && nearbyOptions) {
                nearbyOptions.style.display = 'block';
                if (areaOptions) areaOptions.style.display = 'none';
                
                // 用戶選擇「附近餐廳」時，自動請求位置權限
                // 如果還沒有位置，自動獲取
                if (!userLocation && !locationRequestInProgress) {
                    getUserLocation();
                }
            } else if (mode === 'area' && areaOptions) {
                areaOptions.style.display = 'block';
                if (nearbyOptions) nearbyOptions.style.display = 'none';
            }
            
            // 重置相關狀態
            if (mode !== 'nearby') {
                userLocation = null;
                if (getLocationBtn) {
                    getLocationBtn.textContent = '📍 使用我的位置';
                    getLocationBtn.style.background = '';
                }
                if (locationStatus) {
                    locationStatus.style.display = 'none';
                }
                // 取消選擇交通方式
                const transportRadios = document.querySelectorAll('input[name="transport"]');
                transportRadios.forEach(r => r.checked = false);
            }
            
            if (mode !== 'area') {
                if (citySelect) citySelect.value = '';
                if (districtSelect) {
                    districtSelect.value = '';
                    districtSelect.disabled = true;
                }
            }
        });
    });
    
    // 縣市選擇改變時更新行政區選項
    if (citySelect) {
        citySelect.addEventListener('change', (e) => {
            renderDistrictOptions(e.target.value);
        });
    }
}

// 圖示映射已從共享模組導入

// 渲染表單
function renderForm() {
    // 渲染料理風格選項（預設選擇「不限」）
    const cuisineContainer = document.getElementById('cuisineStyleOptions');
    cuisineContainer.innerHTML = `
        <label class="radio-label">
            <input type="radio" name="cuisine_style" value="none" checked>
            <span class="option-text">
                <span class="option-icon">🎲</span>
                <span>不限</span>
            </span>
        </label>
        ${filterOptions.cuisine_style.map(cuisine => `
            <label class="radio-label">
                <input type="radio" name="cuisine_style" value="${cuisine}">
                <span class="option-text">
                    <span class="option-icon">${cuisineIcons[cuisine] || '🍽️'}</span>
                    <span>${cuisine}</span>
                </span>
            </label>
        `).join('')}
    `;

    // 渲染餐廳類型選項（預設選擇「不限」）
    const typeContainer = document.getElementById('restaurantTypeOptions');
    typeContainer.innerHTML = `
        <label class="radio-label">
            <input type="radio" name="type" value="none" checked>
            <span class="option-text">
                <span class="option-icon">🎲</span>
                <span>不限</span>
            </span>
        </label>
        ${filterOptions.type.map(type => `
            <label class="radio-label">
                <input type="radio" name="type" value="${type}">
                <span class="option-text">
                    <span class="option-icon">${typeIcons[type] || '🍴'}</span>
                    <span>${type}</span>
                </span>
            </label>
        `).join('')}
    `;

    // 渲染預算選項
    const budgetContainer = document.getElementById('budgetOptions');
    budgetContainer.innerHTML = `
        <label class="radio-label">
            <input type="radio" name="budget" value="all" checked>
            <span>不限</span>
        </label>
            ${filterOptions.budget.map(budget => {
                // 如果預算選項已經包含「元」，就不再加「元」
                const displayText = budget.includes('元') ? budget : `${budget} 元`;
                return `
                <label class="radio-label">
                    <input type="radio" name="budget" value="${budget}">
                    <span>${displayText}</span>
                </label>
            `;
            }).join('')}
    `;
}

// 表單提交處理
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // 隱藏錯誤和結果
    hideError();
    hideResults();
    
    // 檢查地區模式選擇
    const locationModeRadio = document.querySelector('input[name="locationMode"]:checked');
    if (!locationModeRadio) {
        showError('請選擇搜尋方式（附近餐廳或選擇地區）');
        return;
    }
    
    // 檢查距離篩選：如果選擇了附近餐廳但沒有位置或交通方式，提示用戶
        if (locationModeRadio.value === 'nearby') {
            const transportRadio = document.querySelector('input[name="transport"]:checked');
            if (!transportRadio) {
                showError('請選擇交通方式（走路或開車）');
                return;
            }
            if (!userLocation) {
                if (locationRequestInProgress) {
                    showError('正在獲取位置資訊，請稍候...');
                    showLocationStatus('正在獲取位置，請稍候', 'info');
                } else {
                    showError('無法取得位置資訊。請點擊「📍 使用我的位置」重試，或選擇「選擇地區」模式');
                    showLocationStatus('請獲取位置才能使用距離篩選', 'error');
                }
                return;
            }
        }
    
    // 檢查地區選擇：如果選擇了選擇地區但沒有選擇縣市，提示用戶
    if (locationModeRadio.value === 'area') {
        const citySelect = document.getElementById('citySelect');
        if (!citySelect || !citySelect.value) {
            showError('請選擇縣市');
            return;
        }
    }
    
    // 顯示載入中
    showLoading();
    submitBtn.disabled = true;
    
    try {
        // 收集表單資料
        const formData = collectFormData();
        console.log('表單資料:', formData);
        
        // 發送 API 請求（不排除任何餐廳，因為這是新的搜尋）
        const restaurants = await fetchRecommendations(formData, []);
        console.log('API 返回的餐廳數量:', restaurants.length);
        console.log('API 返回的餐廳:', restaurants);
        
        // 記錄已顯示的餐廳名稱（重置列表，因為這是新的搜尋）
        displayedRestaurants = restaurants.map(r => r.name);
        
        // 顯示結果
        displayResults(restaurants);
        
    } catch (err) {
        showError(err.message || '獲取推薦餐廳失敗，請稍後再試');
        console.error('推薦餐廳錯誤:', err);
    } finally {
        hideLoading();
        submitBtn.disabled = false;
    }
});

// 收集表單資料
function collectFormData() {
    const formData = {
        cuisine_style: [],
        type: [],
        budget: null,
        userLocation: null,
        transportMode: null,
        maxDistance: null,
        limit: 5
    };
    
    // 收集料理風格（單選，如果是「不限」則不加入）
    const cuisineRadio = form.querySelector('input[name="cuisine_style"]:checked');
    if (cuisineRadio && cuisineRadio.value !== 'none') {
        formData.cuisine_style.push(cuisineRadio.value);
    }
    
    // 收集餐廳類型（單選，如果是「不限」則不加入）
    const typeRadio = form.querySelector('input[name="type"]:checked');
    if (typeRadio && typeRadio.value !== 'none') {
        formData.type.push(typeRadio.value);
    }
    
    // 收集預算（單選）
    const budgetRadio = form.querySelector('input[name="budget"]:checked');
    if (budgetRadio && budgetRadio.value !== 'all') {
        formData.budget = budgetRadio.value;
    }
    
    // 收集地區模式（必須選擇）
    const locationModeRadio = document.querySelector('input[name="locationMode"]:checked');
    if (!locationModeRadio) {
        throw new Error('請選擇搜尋方式（附近餐廳或選擇地區）');
    }
    
    const locationMode = locationModeRadio.value;
    
    if (locationMode === 'nearby') {
        // 附近餐廳模式：需要位置和交通方式
        const transportRadio = document.querySelector('input[name="transport"]:checked');
        if (!transportRadio) {
            throw new Error('請選擇交通方式（走路或開車）');
        }
        if (!userLocation) {
            throw new Error('請先點擊「📍 使用我的位置」按鈕獲取您的位置');
        }
        
        formData.userLocation = userLocation;
        formData.transportMode = transportRadio.value;
        
        // 根據交通方式設定最大距離（公里）
        if (transportRadio.value === 'walking') {
            formData.maxDistance = 0.5; // 走路10分鐘：直線距離 <= 500公尺
        } else if (transportRadio.value === 'driving') {
            formData.maxDistance = 3.0; // 開車10分鐘：直線距離 <= 3公里（原6公里減半）
        }
    } else if (locationMode === 'area') {
        // 選擇地區模式：必須選擇縣市
        const city = citySelect ? citySelect.value : '';
        if (!city) {
            throw new Error('請選擇縣市');
        }
        
        formData.city = city;
        const district = districtSelect ? districtSelect.value : '';
        if (district) {
            formData.district = district;
        }
    }
    
    return formData;
}

// fetchRecommendations 已從共享模組導入

// 顯示結果
function displayResults(restaurants) {
    console.log('displayResults 被調用，餐廳數量:', restaurants.length);
    
    if (restaurants.length === 0) {
        console.warn('沒有找到餐廳，顯示錯誤訊息');
        showError('沒有找到符合條件的餐廳，請調整篩選條件（例如：擴大距離範圍或選擇「選擇地區」模式）');
        return;
    }
    
    console.log('準備顯示餐廳列表');
    
    resultCount.textContent = `${restaurants.length} 間餐廳`;
    
    restaurantList.innerHTML = restaurants.map((restaurant, cardIndex) => {
        // 處理照片（最多8張）
        const images = (restaurant.images || []).slice(0, 8);
        const hasImages = images.length > 0;
        const canSlide = images.length > 1; // 只有1張時不能滑動
        
        return `
        <div class="restaurant-card">
            ${hasImages ? `
                <div class="restaurant-image-container" data-card-index="${cardIndex}">
                    <div class="image-carousel" data-carousel="${cardIndex}">
                        ${images.map((img, imgIndex) => `
                            <div class="carousel-slide ${imgIndex === 0 ? 'active' : ''}" data-slide="${imgIndex}">
                                <img src="${img}" alt="${restaurant.name}" class="carousel-image"
                                     onerror="this.style.display='none';">
                            </div>
                        `).join('')}
                    </div>
                    ${canSlide ? `
                        <div class="carousel-controls">
                            <button class="carousel-btn carousel-prev" data-carousel="${cardIndex}" aria-label="上一張">
                                <span>‹</span>
                            </button>
                            <button class="carousel-btn carousel-next" data-carousel="${cardIndex}" aria-label="下一張">
                                <span>›</span>
                            </button>
                        </div>
                        <div class="carousel-indicators" data-carousel="${cardIndex}">
                            ${images.map((_, imgIndex) => `
                                <span class="indicator ${imgIndex === 0 ? 'active' : ''}" data-slide="${imgIndex}"></span>
                            `).join('')}
                        </div>
                    ` : ''}
                    ${images.length > 1 ? `
                        <div class="image-thumbnails">
                            ${images.map((img, imgIndex) => `
                                <img src="${img}" alt="${restaurant.name}" class="thumbnail ${imgIndex === 0 ? 'active' : ''}" 
                                     data-thumbnail="${cardIndex}-${imgIndex}" data-slide="${imgIndex}"
                                     onerror="this.style.display='none';">
                            `).join('')}
                        </div>
                    ` : ''}
                    <div class="restaurant-image-placeholder" style="display: none;">
                        <span class="placeholder-icon">🍽️</span>
                        <span>無照片</span>
                    </div>
                </div>
            ` : `
                <div class="restaurant-image-placeholder">
                    <span class="placeholder-icon">🍽️</span>
                    <span>無照片</span>
                </div>
            `}
            <div class="restaurant-info">
                <h3 class="restaurant-name">${restaurant.name}</h3>
                <p class="restaurant-address">
                    📍 ${restaurant.address}
                </p>
                <div class="restaurant-tags">
                    ${restaurant.cuisine_style && restaurant.cuisine_style.length > 0 ? 
                        filterGeneralTags(restaurant.cuisine_style)
                            .map(cuisine => 
                                `<span class="tag cuisine">${cuisine}</span>`
                            ).join('') : ''
                    }
                    ${restaurant.type && restaurant.type.length > 0 ? 
                        filterGeneralTags(restaurant.type)
                            .map(type => 
                                `<span class="tag type">${type}</span>`
                            ).join('') : ''
                    }
                    ${restaurant.budget ? 
                        `<span class="tag budget">${restaurant.budget} 元</span>` : 
                        '<span class="tag">預算未標示</span>'
                    }
                </div>
                <div class="restaurant-actions">
                    ${restaurant.url ? 
                        `<a href="${restaurant.url}" target="_blank" class="restaurant-btn booking-btn">
                            📅 訂位
                        </a>` : ''
                    }
                    ${restaurant.coordinates && restaurant.coordinates.lat && restaurant.coordinates.lng ? 
                        `<a href="https://www.google.com/maps/dir/?api=1&destination=${restaurant.coordinates.lat},${restaurant.coordinates.lng}" 
                           target="_blank" class="restaurant-btn navigation-btn">
                            🗺️ 導航
                        </a>` : 
                        restaurant.address ? 
                        `<a href="https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(restaurant.address)}" 
                           target="_blank" class="restaurant-btn navigation-btn">
                            🗺️ 導航
                        </a>` : ''
                    }
                </div>
            </div>
        </div>
    `;
    }).join('');
    
    // 初始化照片輪播功能
    initImageCarousels();
    
    results.style.display = 'block';
    
    // 滾動到結果區域
    results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 重新選擇按鈕（使用相同條件重新獲取不同餐廳）
resetBtn.addEventListener('click', async () => {
    // 如果沒有已顯示的餐廳，說明還沒有搜尋過，不執行任何操作
    if (displayedRestaurants.length === 0) {
        return;
    }
    
    // 隱藏錯誤
    hideError();
    
    // 顯示載入中
    showLoading();
    resetBtn.disabled = true;
    
    try {
        // 收集當前表單資料（使用相同條件）
        const formData = collectFormData();
        
        // 發送 API 請求（不排除任何餐廳，允許重複）
        const restaurants = await fetchRecommendations(formData, []);
        
        if (restaurants.length === 0) {
            showError('沒有找到符合條件的餐廳，請調整篩選條件');
            return;
        }
        
        // 更新已顯示的餐廳列表（重置為新的餐廳，因為允許重複）
        displayedRestaurants = restaurants.map(r => r.name);
        
        // 顯示結果
        displayResults(restaurants);
        
    } catch (err) {
        showError(err.message || '獲取推薦餐廳失敗，請稍後再試');
        console.error('推薦餐廳錯誤:', err);
    } finally {
        hideLoading();
        resetBtn.disabled = false;
    }
});

// 顯示/隱藏載入中
function showLoading() {
    loading.style.display = 'block';
    form.style.opacity = '0.5';
    form.style.pointerEvents = 'none';
}

function hideLoading() {
    loading.style.display = 'none';
    form.style.opacity = '1';
    form.style.pointerEvents = 'auto';
}

// 顯示/隱藏錯誤
function showError(message) {
    errorMessage.textContent = message;
    error.style.display = 'block';
    error.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
    error.style.display = 'none';
}

// 顯示/隱藏結果
function hideResults() {
    results.style.display = 'none';
}

// 獲取用戶位置的函數
let locationRequestInProgress = false;

function getUserLocation() {
    // 防止重複調用
    if (locationRequestInProgress) {
        console.log('定位請求進行中，跳過重複調用');
        return;
    }
    
    if (!navigator.geolocation) {
        showLocationStatus('您的瀏覽器不支援地理位置功能', 'error');
        console.error('瀏覽器不支援 navigator.geolocation');
        return;
    }
    
    // 檢查是否在安全環境下（HTTPS 或 localhost）
    const isSecure = window.location.protocol === 'https:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (!isSecure) {
        console.warn('地理位置 API 建議在 HTTPS 環境下使用');
    }
    
    console.log('開始獲取位置...', {
        protocol: window.location.protocol,
        hostname: window.location.hostname,
        isSecure: isSecure
    });
    
    locationRequestInProgress = true;
    
    if (getLocationBtn) {
        getLocationBtn.disabled = true;
        getLocationBtn.textContent = '📍 定位中...';
    }
    showLocationStatus('正在獲取您的位置...', 'loading');
    
    // 添加定位選項以提高成功率
    const options = {
        enableHighAccuracy: false,
        timeout: 10000,
        maximumAge: 300000  // 允許使用5分鐘內的緩存位置
    };
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            locationRequestInProgress = false;
            userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            if (getLocationBtn) {
                getLocationBtn.disabled = false;
                getLocationBtn.textContent = '✅ 位置已獲取';
                getLocationBtn.style.background = '#4caf50';
            }
            showLocationStatus(`已獲取位置 (${userLocation.lat.toFixed(4)}, ${userLocation.lng.toFixed(4)})`, 'success');
            console.log('位置獲取成功:', userLocation);
        },
        (error) => {
            locationRequestInProgress = false;
            
            if (getLocationBtn) {
                getLocationBtn.disabled = false;
                getLocationBtn.textContent = '📍 使用我的位置';
            }
            
            // 詳細的錯誤日誌
            console.error('地理位置錯誤詳情:', {
                code: error.code,
                message: error.message,
                PERMISSION_DENIED: error.PERMISSION_DENIED,
                POSITION_UNAVAILABLE: error.POSITION_UNAVAILABLE,
                TIMEOUT: error.TIMEOUT,
                errorCode: error.code,
                errorMessage: error.message
            });
            
            // 特別處理 POSITION_UNAVAILABLE 錯誤
            if (error.code === error.POSITION_UNAVAILABLE) {
                console.warn('位置資訊不可用，可能的原因：');
                console.warn('1. macOS 定位服務未開啟');
                console.warn('2. 瀏覽器沒有位置權限');
                console.warn('3. GPS 信號弱或無法取得');
                console.warn('4. 網路連線問題');
                console.warn('請檢查：系統設定 > 隱私權與安全性 > 定位服務');
            }
            
            let errorMsg = '無法獲取位置';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg = '位置權限被拒絕，請在瀏覽器設定中允許存取位置，或選擇「選擇地區」模式';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg = '無法取得位置資訊。請確認：\n1. 裝置定位服務已開啟\n2. 瀏覽器有位置權限\n3. 網路連線正常\n或選擇「選擇地區」模式';
                    break;
                case error.TIMEOUT:
                    errorMsg = '定位請求逾時，請重試或選擇「選擇地區」模式';
                    break;
                default:
                    errorMsg = `定位失敗 (錯誤代碼: ${error.code})，請重試或選擇「選擇地區」模式`;
                    break;
            }
            showLocationStatus(errorMsg, 'error');
        },
        options
    );
}

// 自動獲取用戶位置（已停用）
// 為了避免間歇性的地理位置錯誤影響用戶體驗，已移除自動獲取功能
// 用戶需要主動點擊「使用我的位置」按鈕才會獲取位置
function autoGetUserLocation() {
    // 已停用自動獲取，避免間歇性錯誤
    // 用戶可以主動選擇「附近餐廳」模式並點擊「使用我的位置」按鈕
    return;
}

// 按鈕點擊事件
if (getLocationBtn) {
    getLocationBtn.addEventListener('click', getUserLocation);
}

function showLocationStatus(message, type) {
    if (!locationStatus) return;
    locationStatus.textContent = message;
    locationStatus.style.display = 'block';
    locationStatus.className = `location-status ${type}`;
    
    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            if (type === 'success') {
                locationStatus.style.display = 'none';
            }
        }, 5000);
    }
}

// 初始化照片輪播功能
function initImageCarousels() {
    const carousels = document.querySelectorAll('.image-carousel');
    
    carousels.forEach(carousel => {
        const carouselId = carousel.getAttribute('data-carousel');
        const slides = carousel.querySelectorAll('.carousel-slide');
        const prevBtn = document.querySelector(`.carousel-prev[data-carousel="${carouselId}"]`);
        const nextBtn = document.querySelector(`.carousel-next[data-carousel="${carouselId}"]`);
        const indicators = document.querySelectorAll(`.carousel-indicators[data-carousel="${carouselId}"] .indicator`);
        
        if (slides.length === 0) return;
        
        let currentSlide = 0;
        const totalSlides = slides.length;
        
        // 顯示指定幻燈片（不循環）
        function showSlide(index) {
            // 確保索引在範圍內（不循環）
            if (index < 0) {
                currentSlide = 0; // 第一張，不循環到最後
                return;
            } else if (index >= totalSlides) {
                currentSlide = totalSlides - 1; // 最後一張，不循環到第一張
                return;
            } else {
                currentSlide = index;
            }
            
            // 更新幻燈片
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === currentSlide);
            });
            
            // 更新指示器
            indicators.forEach((indicator, i) => {
                indicator.classList.toggle('active', i === currentSlide);
            });
            
            // 更新縮圖
            const thumbnails = document.querySelectorAll(`.thumbnail[data-thumbnail^="${carouselId}-"]`);
            thumbnails.forEach((thumb, i) => {
                thumb.classList.toggle('active', i === currentSlide);
            });
            
            // 更新按鈕狀態
            if (prevBtn) {
                prevBtn.style.opacity = currentSlide === 0 ? '0.5' : '1';
                prevBtn.style.pointerEvents = currentSlide === 0 ? 'none' : 'all';
            }
            if (nextBtn) {
                nextBtn.style.opacity = currentSlide === totalSlides - 1 ? '0.5' : '1';
                nextBtn.style.pointerEvents = currentSlide === totalSlides - 1 ? 'none' : 'all';
            }
        }
        
        // 上一張
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                showSlide(currentSlide - 1);
            });
        }
        
        // 下一張
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                showSlide(currentSlide + 1);
            });
        }
        
        // 點擊指示器
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                showSlide(index);
            });
        });
        
        // 點擊縮圖
        const thumbnails = document.querySelectorAll(`.thumbnail[data-thumbnail^="${carouselId}-"]`);
        thumbnails.forEach((thumb) => {
            const slideIndex = parseInt(thumb.getAttribute('data-slide'));
            if (!isNaN(slideIndex)) {
                thumb.addEventListener('click', () => {
                    showSlide(slideIndex);
                });
            }
        });
        
        // 初始化按鈕狀態（第一張時上一張按鈕禁用）
        if (prevBtn && totalSlides > 1) {
            prevBtn.style.opacity = '0.5';
            prevBtn.style.pointerEvents = 'none';
        }
        
        // 觸摸滑動支持
        let touchStartX = 0;
        let touchEndX = 0;
        
        carousel.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        carousel.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });
        
        function handleSwipe() {
            const swipeThreshold = 50; // 最小滑動距離
            const diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    // 向左滑動，下一張（不循環）
                    if (currentSlide < totalSlides - 1) {
                        showSlide(currentSlide + 1);
                    }
                } else {
                    // 向右滑動，上一張（不循環）
                    if (currentSlide > 0) {
                        showSlide(currentSlide - 1);
                    }
                }
            }
        }
    });
}
