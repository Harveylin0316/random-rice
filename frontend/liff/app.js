// LINE LIFF App
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

// LINE LIFF ID（需要在 LINE Developers Console 獲取）
// 優先順序：1. URL 參數 2. 環境變數 3. 默認值
function getLiffId() {
    // 從 URL 參數獲取（方便測試）
    const urlParams = new URLSearchParams(window.location.search);
    const urlLiffId = urlParams.get('liffId');
    if (urlLiffId) {
        console.log('從 URL 參數獲取 LIFF ID:', urlLiffId);
        return urlLiffId;
    }
    
    // 從環境變數獲取（如果設置了）
    if (window.LIFF_ID) {
        console.log('從環境變數獲取 LIFF ID');
        return window.LIFF_ID;
    }
    
    // 默認值（需要替換為實際的 LIFF ID）
    const defaultLiffId = 'YOUR_LIFF_ID_HERE';
    if (defaultLiffId === 'YOUR_LIFF_ID_HERE') {
        console.warn('⚠️ 請設置 LIFF ID！');
        console.warn('方式 1: 在 URL 中添加 ?liffId=你的LIFF_ID');
        console.warn('方式 2: 在 LINE Developers Console 創建 LIFF App 後，將 LIFF ID 設置到這裡');
    }
    
    return defaultLiffId;
}

const LIFF_ID = getLiffId();

// API 基礎 URL
const API_BASE_URL = getApiBaseUrl();

// LINE LIFF 實例
let liff = null;
let liffProfile = null;

// DOM 元素
const liffLoading = document.getElementById('liffLoading');
const mainContent = document.getElementById('mainContent');
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

// 初始化 LIFF
async function initLiff() {
    try {
        console.log('正在初始化 LINE LIFF...');
        
        // 初始化 LIFF SDK
        liff = window.liff;
        await liff.init({ liffId: LIFF_ID });
        
        console.log('LIFF 初始化成功');
        console.log('LIFF 環境:', {
            isInClient: liff.isInClient(),
            isLoggedIn: liff.isLoggedIn(),
            os: liff.getOS(),
            version: liff.getVersion(),
            language: liff.getLanguage()
        });
        
        // 檢查是否在 LINE 內
        if (!liff.isInClient()) {
            console.warn('不在 LINE 內，某些功能可能無法使用');
            // 可以選擇提示用戶在 LINE 內打開
        }
        
        // 如果已登入，獲取用戶資料
        if (liff.isLoggedIn()) {
            liffProfile = await liff.getProfile();
            console.log('用戶資料:', liffProfile);
        } else {
            // 如果未登入，可以選擇登入（如果需要）
            // liff.login();
            console.log('用戶未登入');
        }
        
        // 隱藏載入畫面，顯示主要內容
        liffLoading.style.display = 'none';
        mainContent.style.display = 'block';
        
        // 初始化應用
        await initApp();
        
    } catch (error) {
        console.error('LIFF 初始化失敗:', error);
        showError('初始化失敗，請重新整理頁面');
        liffLoading.innerHTML = `
            <div class="error">
                <p>初始化失敗</p>
                <p>${error.message}</p>
                <button onclick="location.reload()">重新載入</button>
            </div>
        `;
    }
}

// 初始化應用
async function initApp() {
    try {
        await loadFilterOptions();
        await loadLocationOptions();
        renderForm();
        setupLocationModeHandlers();
        
        // 初始化顯示「附近餐廳」選項（預設選項）
        if (areaOptions) areaOptions.style.display = 'none';
        if (nearbyOptions) nearbyOptions.style.display = 'block';
        
        // 自動獲取用戶位置
        autoGetUserLocation();
    } catch (err) {
        showError('載入篩選選項失敗，請重新整理頁面');
        console.error('載入篩選選項錯誤:', err);
    }
}

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

// 渲染表單
function renderForm() {
    // 渲染料理風格選項（預設選擇「不限」）
    const cuisineContainer = document.getElementById('cuisineStyleOptions');
    if (cuisineContainer) {
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
    }

    // 渲染餐廳類型選項（預設選擇「不限」）
    const typeContainer = document.getElementById('restaurantTypeOptions');
    if (typeContainer) {
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
    }

    // 渲染預算選項
    const budgetContainer = document.getElementById('budgetOptions');
    if (budgetContainer) {
        budgetContainer.innerHTML = `
            <label class="radio-label">
                <input type="radio" name="budget" value="all" checked>
                <span>不限</span>
            </label>
            ${filterOptions.budget.map(budget => `
                <label class="radio-label">
                    <input type="radio" name="budget" value="${budget}">
                    <span>${budget} 元</span>
                </label>
            `).join('')}
        `;
    }
}

// 顯示/隱藏錯誤
function showError(message) {
    if (errorMessage) errorMessage.textContent = message;
    if (error) {
        error.style.display = 'block';
        error.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function hideError() {
    if (error) error.style.display = 'none';
}

// 顯示/隱藏載入中
function showLoading() {
    if (loading) loading.style.display = 'block';
    if (form) {
        form.style.opacity = '0.5';
        form.style.pointerEvents = 'none';
    }
}

function hideLoading() {
    if (loading) loading.style.display = 'none';
    if (form) {
        form.style.opacity = '1';
        form.style.pointerEvents = 'auto';
    }
}

// 顯示/隱藏結果
function hideResults() {
    if (results) results.style.display = 'none';
}

// 表單提交處理
if (form) {
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
        
        // 檢查距離篩選
        if (locationModeRadio.value === 'nearby') {
            const transportRadio = document.querySelector('input[name="transport"]:checked');
            if (!transportRadio) {
                showError('請選擇交通方式（走路或開車）');
                return;
            }
            if (!userLocation) {
                showError('請先點擊「📍 使用我的位置」按鈕獲取您的位置');
                showLocationStatus('請先獲取位置才能使用距離篩選', 'error');
                return;
            }
        }
        
        // 檢查地區選擇
        if (locationModeRadio.value === 'area') {
            if (!citySelect || !citySelect.value) {
                showError('請選擇縣市');
                return;
            }
        }
        
        // 顯示載入中
        showLoading();
        if (submitBtn) submitBtn.disabled = true;
        
        try {
            // 收集表單資料
            const formData = collectFormData();
            console.log('表單資料:', formData);
            
            // 發送 API 請求
            const restaurants = await fetchRecommendations(formData, []);
            console.log('API 返回的餐廳數量:', restaurants.length);
            
            // 記錄已顯示的餐廳名稱
            displayedRestaurants = restaurants.map(r => r.name);
            
            // 顯示結果
            displayResults(restaurants);
            
        } catch (err) {
            showError(err.message || '獲取推薦餐廳失敗，請稍後再試');
            console.error('推薦餐廳錯誤:', err);
        } finally {
            hideLoading();
            if (submitBtn) submitBtn.disabled = false;
        }
    });
}

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
    
    // 收集料理風格
    const cuisineRadio = form.querySelector('input[name="cuisine_style"]:checked');
    if (cuisineRadio && cuisineRadio.value !== 'none') {
        formData.cuisine_style.push(cuisineRadio.value);
    }
    
    // 收集餐廳類型
    const typeRadio = form.querySelector('input[name="type"]:checked');
    if (typeRadio && typeRadio.value !== 'none') {
        formData.type.push(typeRadio.value);
    }
    
    // 收集預算
    const budgetRadio = form.querySelector('input[name="budget"]:checked');
    if (budgetRadio && budgetRadio.value !== 'all') {
        formData.budget = budgetRadio.value;
    }
    
    // 收集地區模式
    const locationModeRadio = document.querySelector('input[name="locationMode"]:checked');
    if (!locationModeRadio) {
        throw new Error('請選擇搜尋方式（附近餐廳或選擇地區）');
    }
    
    const locationMode = locationModeRadio.value;
    
    if (locationMode === 'nearby') {
        const transportRadio = document.querySelector('input[name="transport"]:checked');
        if (!transportRadio) {
            throw new Error('請選擇交通方式（走路或開車）');
        }
        if (!userLocation) {
            throw new Error('請先點擊「📍 使用我的位置」按鈕獲取您的位置');
        }
        
        formData.userLocation = userLocation;
        formData.transportMode = transportRadio.value;
        
        if (transportRadio.value === 'walking') {
            formData.maxDistance = 0.5;
        } else if (transportRadio.value === 'driving') {
            formData.maxDistance = 3.0;
        }
    } else if (locationMode === 'area') {
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

// 顯示結果
function displayResults(restaurants) {
    console.log('displayResults 被調用，餐廳數量:', restaurants.length);
    
    if (restaurants.length === 0) {
        showError('沒有找到符合條件的餐廳，請調整篩選條件');
        return;
    }
    
    if (resultCount) resultCount.textContent = `${restaurants.length} 間餐廳`;
    
    if (restaurantList) {
        restaurantList.innerHTML = restaurants.map((restaurant, cardIndex) => {
            const images = (restaurant.images || []).slice(0, 8);
            const hasImages = images.length > 0;
            const canSlide = images.length > 1;
            
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
                                <button class="carousel-btn carousel-prev" data-carousel="${cardIndex}">
                                    <span>‹</span>
                                </button>
                                <button class="carousel-btn carousel-next" data-carousel="${cardIndex}">
                                    <span>›</span>
                                </button>
                            </div>
                            <div class="carousel-indicators" data-carousel="${cardIndex}">
                                ${images.map((_, imgIndex) => `
                                    <span class="indicator ${imgIndex === 0 ? 'active' : ''}" data-slide="${imgIndex}"></span>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                ` : `
                    <div class="restaurant-image-placeholder">
                        <span class="placeholder-icon">🍽️</span>
                        <span>無照片</span>
                    </div>
                `}
                <div class="restaurant-info">
                    <h3 class="restaurant-name">${restaurant.name}</h3>
                    <p class="restaurant-address">📍 ${restaurant.address}</p>
                    <div class="restaurant-tags">
                        ${restaurant.cuisine_style && restaurant.cuisine_style.length > 0 ? 
                            filterGeneralTags(restaurant.cuisine_style)
                                .map(cuisine => `<span class="tag cuisine">${cuisine}</span>`).join('') : ''
                        }
                        ${restaurant.type && restaurant.type.length > 0 ? 
                            filterGeneralTags(restaurant.type)
                                .map(type => `<span class="tag type">${type}</span>`).join('') : ''
                        }
                        ${restaurant.budget ? 
                            `<span class="tag budget">${restaurant.budget} 元</span>` : 
                            '<span class="tag">預算未標示</span>'
                        }
                    </div>
                    <div class="restaurant-actions">
                        ${restaurant.url ? 
                            `<a href="${restaurant.url}" target="_blank" class="restaurant-btn booking-btn">📅 訂位</a>` : ''
                        }
                        ${restaurant.coordinates && restaurant.coordinates.lat && restaurant.coordinates.lng ? 
                            `<a href="https://www.google.com/maps/dir/?api=1&destination=${restaurant.coordinates.lat},${restaurant.coordinates.lng}" 
                               target="_blank" class="restaurant-btn navigation-btn">🗺️ 導航</a>` : 
                            restaurant.address ? 
                            `<a href="https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(restaurant.address)}" 
                               target="_blank" class="restaurant-btn navigation-btn">🗺️ 導航</a>` : ''
                        }
                    </div>
                </div>
            </div>
        `;
        }).join('');
    }
    
    // 初始化照片輪播功能
    initImageCarousels();
    
    if (results) {
        results.style.display = 'block';
        results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// 重新選擇按鈕
if (resetBtn) {
    resetBtn.addEventListener('click', async () => {
        if (displayedRestaurants.length === 0) return;
        
        hideError();
        showLoading();
        resetBtn.disabled = true;
        
        try {
            const formData = collectFormData();
            const restaurants = await fetchRecommendations(formData, []);
            
            if (restaurants.length === 0) {
                showError('沒有找到符合條件的餐廳，請調整篩選條件');
                return;
            }
            
            displayedRestaurants = restaurants.map(r => r.name);
            displayResults(restaurants);
            
        } catch (err) {
            showError(err.message || '獲取推薦餐廳失敗，請稍後再試');
            console.error('推薦餐廳錯誤:', err);
        } finally {
            hideLoading();
            resetBtn.disabled = false;
        }
    });
}

// 獲取用戶位置
let locationRequestInProgress = false;

function getUserLocation() {
    if (locationRequestInProgress) return;
    
    if (!navigator.geolocation) {
        showLocationStatus('您的瀏覽器不支援地理位置功能', 'error');
        return;
    }
    
    locationRequestInProgress = true;
    
    if (getLocationBtn) {
        getLocationBtn.disabled = true;
        getLocationBtn.textContent = '📍 定位中...';
    }
    showLocationStatus('正在獲取您的位置...', 'loading');
    
    const options = {
        enableHighAccuracy: false,
        timeout: 10000,
        maximumAge: 300000
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
            showLocationStatus(`已獲取位置`, 'success');
            console.log('位置獲取成功:', userLocation);
        },
        (error) => {
            locationRequestInProgress = false;
            
            if (getLocationBtn) {
                getLocationBtn.disabled = false;
                getLocationBtn.textContent = '📍 使用我的位置';
            }
            
            let errorMsg = '無法獲取位置';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg = '位置權限被拒絕，請允許存取位置，或選擇「選擇地區」模式';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg = '無法取得位置資訊，請確認定位服務已開啟，或選擇「選擇地區」模式';
                    break;
                case error.TIMEOUT:
                    errorMsg = '定位請求逾時，請重試或選擇「選擇地區」模式';
                    break;
                default:
                    errorMsg = `定位失敗，請重試或選擇「選擇地區」模式`;
                    break;
            }
            showLocationStatus(errorMsg, 'error');
        },
        options
    );
}

// 自動獲取用戶位置
function autoGetUserLocation() {
    if (userLocation || locationRequestInProgress) return;
    
    const locationModeRadio = document.querySelector('input[name="locationMode"]:checked');
    if (locationModeRadio && locationModeRadio.value === 'nearby') {
        setTimeout(() => {
            if (!userLocation && !locationRequestInProgress) {
                getUserLocation();
            }
        }, 500);
    }
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
    
    if (type === 'success') {
        setTimeout(() => {
            locationStatus.style.display = 'none';
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
        
        function showSlide(index) {
            if (index < 0) {
                currentSlide = 0;
                return;
            } else if (index >= totalSlides) {
                currentSlide = totalSlides - 1;
                return;
            } else {
                currentSlide = index;
            }
            
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === currentSlide);
            });
            
            indicators.forEach((indicator, i) => {
                indicator.classList.toggle('active', i === currentSlide);
            });
            
            if (prevBtn) {
                prevBtn.style.opacity = currentSlide === 0 ? '0.5' : '1';
                prevBtn.style.pointerEvents = currentSlide === 0 ? 'none' : 'all';
            }
            if (nextBtn) {
                nextBtn.style.opacity = currentSlide === totalSlides - 1 ? '0.5' : '1';
                nextBtn.style.pointerEvents = currentSlide === totalSlides - 1 ? 'none' : 'all';
            }
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => showSlide(currentSlide - 1));
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => showSlide(currentSlide + 1));
        }
        
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => showSlide(index));
        });
        
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
            const diff = touchStartX - touchEndX;
            const swipeThreshold = 50;
            
            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0 && currentSlide < totalSlides - 1) {
                    showSlide(currentSlide + 1);
                } else if (diff < 0 && currentSlide > 0) {
                    showSlide(currentSlide - 1);
                }
            }
        }, { passive: true });
    });
}

// 頁面載入時初始化 LIFF
document.addEventListener('DOMContentLoaded', () => {
    // 檢查 LIFF SDK 是否已載入
    if (window.liff) {
        initLiff();
    } else {
        console.error('LINE LIFF SDK 未載入');
        showError('LINE LIFF SDK 載入失敗，請檢查網路連線');
    }
});
