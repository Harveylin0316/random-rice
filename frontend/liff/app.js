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
// 暫時使用環境變數或配置，實際部署時需要設置
const LIFF_ID = window.LIFF_ID || 'YOUR_LIFF_ID_HERE';

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
