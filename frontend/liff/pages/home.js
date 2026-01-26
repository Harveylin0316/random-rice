// 首頁：今天吃什麼（餐廳推薦功能）
// 這個文件包含餐廳推薦頁面的所有邏輯

import { 
    FRONTEND_CUISINE_CATEGORIES, 
    FRONTEND_TYPE_CATEGORIES,
    cuisineIcons,
    typeIcons
} from '../shared/constants.js';
import { 
    loadFilterOptions as apiLoadFilterOptions,
    loadLocationOptions as apiLoadLocationOptions,
    fetchRecommendations
} from '../shared/api.js';
import { filterGeneralTags, initImageCarousels } from '../shared/utils.js';

// 頁面狀態
let filterOptions = {
    cuisine_style: [],
    type: [],
    budget: []
};

let locationOptions = {
    cities: [],
    districts: {}
};

let userLocation = null;
let displayedRestaurants = [];
let locationRequestInProgress = false;

// 初始化首頁
export async function initHomePage() {
    console.log('初始化首頁：今天吃什麼');
    
    try {
        await loadFilterOptions();
        await loadLocationOptions();
        renderForm();
        setupLocationModeHandlers();
        
        // 初始化顯示「附近餐廳」選項
        const areaOptions = document.getElementById('areaOptions');
        const nearbyOptions = document.getElementById('nearbyOptions');
        if (areaOptions) areaOptions.style.display = 'none';
        if (nearbyOptions) nearbyOptions.style.display = 'block';
        
        // 自動獲取用戶位置
        autoGetUserLocation();
        
        // 設置表單提交事件
        setupFormSubmit();
        
        // 設置重新選擇按鈕
        setupResetButton();
        
    } catch (err) {
        console.error('初始化首頁錯誤:', err);
        throw err;
    }
}

// 載入篩選選項
async function loadFilterOptions() {
    try {
        const options = await apiLoadFilterOptions();
        filterOptions = options;
        filterOptions.cuisine_style = filterOptions.cuisine_style.filter(
            cuisine => FRONTEND_CUISINE_CATEGORIES.includes(cuisine)
        );
        if (filterOptions.cuisine_style.length !== FRONTEND_CUISINE_CATEGORIES.length) {
            filterOptions.cuisine_style = [...FRONTEND_CUISINE_CATEGORIES];
        }
        filterOptions.type = filterOptions.type.filter(
            type => FRONTEND_TYPE_CATEGORIES.includes(type)
        );
        if (filterOptions.type.length !== FRONTEND_TYPE_CATEGORIES.length) {
            filterOptions.type = [...FRONTEND_TYPE_CATEGORIES];
        }
    } catch (err) {
        console.error('載入篩選選項錯誤:', err);
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
    const citySelect = document.getElementById('citySelect');
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
    const districtSelect = document.getElementById('districtSelect');
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
    const locationModeRadios = document.querySelectorAll('input[name="locationMode"]');
    const nearbyOptions = document.getElementById('nearbyOptions');
    const areaOptions = document.getElementById('areaOptions');
    const citySelect = document.getElementById('citySelect');
    const districtSelect = document.getElementById('districtSelect');
    const getLocationBtn = document.getElementById('getLocationBtn');
    const locationStatus = document.getElementById('locationStatus');
    
    locationModeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            const mode = radio.value;
            
            if (nearbyOptions) nearbyOptions.style.display = 'none';
            if (areaOptions) areaOptions.style.display = 'none';
            
            if (mode === 'nearby' && nearbyOptions) {
                nearbyOptions.style.display = 'block';
                if (areaOptions) areaOptions.style.display = 'none';
            } else if (mode === 'area' && areaOptions) {
                areaOptions.style.display = 'block';
                if (nearbyOptions) nearbyOptions.style.display = 'none';
            }
            
            if (mode !== 'nearby') {
                userLocation = null;
                if (getLocationBtn) {
                    getLocationBtn.textContent = '📍 使用我的位置';
                    getLocationBtn.style.background = '';
                }
                if (locationStatus) {
                    locationStatus.style.display = 'none';
                }
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
    
    if (citySelect) {
        citySelect.addEventListener('change', (e) => {
            renderDistrictOptions(e.target.value);
        });
    }
}

// 渲染表單
function renderForm() {
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

// 設置表單提交
function setupFormSubmit() {
    const form = document.getElementById('recommendationForm');
    const submitBtn = document.getElementById('submitBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        hideError();
        hideResults();
        
        const locationModeRadio = document.querySelector('input[name="locationMode"]:checked');
        if (!locationModeRadio) {
            showError('請選擇搜尋方式（附近餐廳或選擇地區）');
            return;
        }
        
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
        
        if (locationModeRadio.value === 'area') {
            const citySelect = document.getElementById('citySelect');
            if (!citySelect || !citySelect.value) {
                showError('請選擇縣市');
                return;
            }
        }
        
        showLoading();
        if (submitBtn) submitBtn.disabled = true;
        
        try {
            const formData = collectFormData();
            console.log('表單資料:', formData);
            
            const restaurants = await fetchRecommendations(formData, []);
            console.log('API 返回的餐廳數量:', restaurants.length);
            
            displayedRestaurants = restaurants.map(r => r.name);
            displayResults(restaurants);
            
        } catch (err) {
            showError(err.message || '獲取推薦餐廳失敗，請稍後再試');
            console.error('推薦餐廳錯誤:', err);
        } finally {
            hideLoading();
            if (submitBtn) submitBtn.disabled = false;
        }
    });
    
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
    
    function hideResults() {
        if (results) results.style.display = 'none';
    }
}

// 收集表單資料
function collectFormData() {
    const form = document.getElementById('recommendationForm');
    const formData = {
        cuisine_style: [],
        type: [],
        budget: null,
        userLocation: null,
        transportMode: null,
        maxDistance: null,
        limit: 5
    };
    
    const cuisineRadio = form.querySelector('input[name="cuisine_style"]:checked');
    if (cuisineRadio && cuisineRadio.value !== 'none') {
        formData.cuisine_style.push(cuisineRadio.value);
    }
    
    const typeRadio = form.querySelector('input[name="type"]:checked');
    if (typeRadio && typeRadio.value !== 'none') {
        formData.type.push(typeRadio.value);
    }
    
    const budgetRadio = form.querySelector('input[name="budget"]:checked');
    if (budgetRadio && budgetRadio.value !== 'all') {
        formData.budget = budgetRadio.value;
    }
    
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
        const citySelect = document.getElementById('citySelect');
        const city = citySelect ? citySelect.value : '';
        if (!city) {
            throw new Error('請選擇縣市');
        }
        
        formData.city = city;
        const districtSelect = document.getElementById('districtSelect');
        const district = districtSelect ? districtSelect.value : '';
        if (district) {
            formData.district = district;
        }
    }
    
    return formData;
}

// 顯示結果
function displayResults(restaurants) {
    const resultCount = document.getElementById('resultCount');
    const restaurantList = document.getElementById('restaurantList');
    const results = document.getElementById('results');
    
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
    
    initImageCarousels();
    
    if (results) {
        results.style.display = 'block';
        results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const error = document.getElementById('error');
    if (errorMessage) errorMessage.textContent = message;
    if (error) {
        error.style.display = 'block';
        error.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// 設置重新選擇按鈕
function setupResetButton() {
    const resetBtn = document.getElementById('resetBtn');
    const loading = document.getElementById('loading');
    const submitBtn = document.getElementById('submitBtn');
    
    if (!resetBtn) return;
    
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
    
    function hideError() {
        const error = document.getElementById('error');
        if (error) error.style.display = 'none';
    }
    
    function showLoading() {
        const loading = document.getElementById('loading');
        const form = document.getElementById('recommendationForm');
        if (loading) loading.style.display = 'block';
        if (form) {
            form.style.opacity = '0.5';
            form.style.pointerEvents = 'none';
        }
    }
    
    function hideLoading() {
        const loading = document.getElementById('loading');
        const form = document.getElementById('recommendationForm');
        if (loading) loading.style.display = 'none';
        if (form) {
            form.style.opacity = '1';
            form.style.pointerEvents = 'auto';
        }
    }
}

// 獲取用戶位置
function getUserLocation() {
    if (locationRequestInProgress) return;
    
    if (!navigator.geolocation) {
        showLocationStatus('您的瀏覽器不支援地理位置功能', 'error');
        return;
    }
    
    locationRequestInProgress = true;
    const getLocationBtn = document.getElementById('getLocationBtn');
    
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

// 設置位置按鈕事件
function setupLocationButton() {
    const getLocationBtn = document.getElementById('getLocationBtn');
    if (getLocationBtn) {
        getLocationBtn.addEventListener('click', getUserLocation);
    }
}

// 初始化位置按鈕（需要在頁面載入後調用）
setupLocationButton();

function showLocationStatus(message, type) {
    const locationStatus = document.getElementById('locationStatus');
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

