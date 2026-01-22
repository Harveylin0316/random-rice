// API 基礎 URL
const API_BASE_URL = 'http://localhost:3000/api';

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

// 使用者位置和交通方式
let userLocation = null;

// 篩選選項資料
let filterOptions = {
    cuisine_style: [],
    type: [],
    budget: []
};

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadFilterOptions();
        renderForm();
    } catch (err) {
        showError('載入篩選選項失敗，請重新整理頁面');
        console.error('載入篩選選項錯誤:', err);
    }
});

// 載入篩選選項
async function loadFilterOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/restaurants/filter-options`);
        if (!response.ok) {
            throw new Error('無法載入篩選選項');
        }
        const data = await response.json();
        if (data.success) {
            filterOptions = data.options;
        } else {
            throw new Error('篩選選項資料格式錯誤');
        }
    } catch (err) {
        console.error('載入篩選選項錯誤:', err);
        throw err;
    }
}

// 料理風格圖示映射
const cuisineIcons = {
    '中式': '🥢',
    '台式': '🍜',
    '日式': '🍱',
    '韓式': '🥘',
    '美式': '🍔',
    '義式': '🍝',
    '法式': '🥖',
    '泰式': '🍲',
    '印度': '🍛',
    '素食': '🥗',
    '其他': '🍽️'
};

// 餐廳類型圖示映射
const typeIcons = {
    '燒肉': '🥩',
    '火鍋': '🍲',
    '吃到飽': '🍱',
    '餐酒館': '🍷',
    '酒吧': '🍷',
    '鐵板燒': '🔥',
    '牛排': '🥩',
    '定食': '🍱',
    '其他': '🍴'
};

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
        ${filterOptions.budget.map(budget => `
            <label class="radio-label">
                <input type="radio" name="budget" value="${budget}">
                <span>${budget} 元</span>
            </label>
        `).join('')}
    `;
}

// 表單提交處理
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // 隱藏錯誤和結果
    hideError();
    hideResults();
    
    // 檢查距離篩選：如果選擇了距離選項但沒有位置，提示用戶
    const transportRadio = document.querySelector('input[name="transport"]:checked');
    if (transportRadio && transportRadio.value !== 'none' && !userLocation) {
        showError('請先點擊「📍 使用我的位置」按鈕獲取您的位置，才能使用距離篩選功能');
        showLocationStatus('請先獲取位置才能使用距離篩選', 'error');
        return;
    }
    
    // 顯示載入中
    showLoading();
    submitBtn.disabled = true;
    
    try {
        // 收集表單資料
        const formData = collectFormData();
        
        // 發送 API 請求
        const restaurants = await fetchRecommendations(formData);
        
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
    
    // 收集交通方式和距離（如果有選擇且有用戶位置）
    const transportRadio = document.querySelector('input[name="transport"]:checked');
    if (transportRadio && transportRadio.value !== 'none' && userLocation) {
        formData.userLocation = userLocation;
        formData.transportMode = transportRadio.value;
        
        // 根據交通方式設定最大距離（公里）
        // 走路10分鐘：假設每小時5公里，10分鐘約0.83公里，設為1公里
        // 開車10分鐘：假設市區平均時速30公里，10分鐘約5公里，設為6公里（考慮路況）
        if (transportRadio.value === 'walking') {
            formData.maxDistance = 1.0; // 走路10分鐘約1公里
        } else if (transportRadio.value === 'driving') {
            formData.maxDistance = 6.0; // 開車10分鐘約6公里
        }
    }
    
    return formData;
}

// 獲取推薦餐廳
async function fetchRecommendations(formData) {
    // 建立查詢參數
    const params = new URLSearchParams();
    
    if (formData.cuisine_style.length > 0) {
        params.append('cuisine_style', formData.cuisine_style.join(','));
    }
    
    if (formData.type.length > 0) {
        params.append('type', formData.type.join(','));
    }
    
    if (formData.budget) {
        params.append('budget', formData.budget);
    }
    
    // 距離篩選參數
    if (formData.userLocation && formData.maxDistance) {
        params.append('userLat', formData.userLocation.lat);
        params.append('userLng', formData.userLocation.lng);
        params.append('maxDistance', formData.maxDistance);
    }
    
    params.append('limit', formData.limit);
    
    // 發送請求
    const response = await fetch(`${API_BASE_URL}/restaurants/recommend?${params.toString()}`);
    
    if (!response.ok) {
        throw new Error(`API 請求失敗: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error || '獲取推薦餐廳失敗');
    }
    
    return data.restaurants;
}

// 顯示結果
function displayResults(restaurants) {
    if (restaurants.length === 0) {
        showError('沒有找到符合條件的餐廳，請調整篩選條件');
        return;
    }
    
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
                        restaurant.cuisine_style.map(cuisine => 
                            `<span class="tag cuisine">${cuisine}</span>`
                        ).join('') : ''
                    }
                    ${restaurant.type && restaurant.type.length > 0 ? 
                        restaurant.type.map(type => 
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

// 重置按鈕
resetBtn.addEventListener('click', () => {
    form.reset();
    hideResults();
    hideError();
    
    // 重置料理風格為「隨機」
    const cuisineRandom = form.querySelector('input[name="cuisine_style"][value="random"]');
    if (cuisineRandom) {
        cuisineRandom.checked = true;
    }
    
    // 重置餐廳類型為「隨機」
    const typeRandom = form.querySelector('input[name="type"][value="random"]');
    if (typeRandom) {
        typeRandom.checked = true;
    }
    
    // 重置料理風格為「不限」
    const cuisineNone = form.querySelector('input[name="cuisine_style"][value="none"]');
    if (cuisineNone) {
        cuisineNone.checked = true;
    }
    
    // 重置餐廳類型為「不限」
    const typeNone = form.querySelector('input[name="type"][value="none"]');
    if (typeNone) {
        typeNone.checked = true;
    }
    
    // 重置交通方式為「不限」
    const transportNone = document.querySelector('input[name="transport"][value="none"]');
    if (transportNone) {
        transportNone.checked = true;
    }
    
    // 重置位置相關狀態
    userLocation = null;
    if (getLocationBtn) {
        getLocationBtn.textContent = '📍 使用我的位置';
        getLocationBtn.style.background = '';
        getLocationBtn.disabled = false;
    }
    if (locationStatus) {
        locationStatus.style.display = 'none';
    }
    
    // 重置預算為「不限」
    const allRadio = form.querySelector('input[name="budget"][value="all"]');
    if (allRadio) {
        allRadio.checked = true;
    }
    
    // 滾動到頂部
    window.scrollTo({ top: 0, behavior: 'smooth' });
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

// 獲取使用者位置
if (getLocationBtn) {
    getLocationBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
            showLocationStatus('您的瀏覽器不支援地理位置功能', 'error');
            return;
        }
        
        getLocationBtn.disabled = true;
        getLocationBtn.textContent = '📍 定位中...';
        showLocationStatus('正在獲取您的位置...', 'loading');
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                getLocationBtn.disabled = false;
                getLocationBtn.textContent = '✅ 位置已獲取';
                getLocationBtn.style.background = '#4caf50';
                showLocationStatus(`✅ 已獲取位置 (${userLocation.lat.toFixed(4)}, ${userLocation.lng.toFixed(4)})`, 'success');
            },
            (error) => {
                getLocationBtn.disabled = false;
                getLocationBtn.textContent = '📍 使用我的位置';
                let errorMsg = '無法獲取位置';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg = '位置權限被拒絕，請允許瀏覽器存取您的位置';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg = '無法取得位置資訊';
                        break;
                    case error.TIMEOUT:
                        errorMsg = '定位請求逾時';
                        break;
                }
                showLocationStatus(errorMsg, 'error');
            }
        );
    });
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
