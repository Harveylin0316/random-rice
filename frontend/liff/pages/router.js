// 路由管理器
// 負責根據 URL 參數切換不同的頁面

import { initHomePage } from './home.js';

// 頁面路由映射
const routes = {
    'home': initHomePage,
    // 未來可以添加更多頁面：
    // 'favorites': initFavoritesPage,
    // 'history': initHistoryPage,
    // 'settings': initSettingsPage,
};

// 當前頁面
let currentPage = null;

/**
 * 初始化路由系統
 */
export function initRouter() {
    console.log('初始化路由系統');
    
    // 獲取當前頁面參數
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page') || 'home';
    
    console.log('當前頁面:', page);
    
    // 載入對應的頁面
    loadPage(page);
}

/**
 * 載入指定頁面
 * @param {string} pageName - 頁面名稱
 */
async function loadPage(pageName) {
    // 如果頁面不存在，使用首頁
    if (!routes[pageName]) {
        console.warn(`頁面 "${pageName}" 不存在，使用首頁`);
        pageName = 'home';
    }
    
    // 如果已經載入相同頁面，不需要重新載入
    if (currentPage === pageName) {
        console.log(`頁面 "${pageName}" 已經載入`);
        return;
    }
    
    console.log(`載入頁面: ${pageName}`);
    
    try {
        // 調用對應頁面的初始化函數
        const initFunction = routes[pageName];
        if (typeof initFunction === 'function') {
            await initFunction();
            currentPage = pageName;
            console.log(`頁面 "${pageName}" 載入成功`);
        } else {
            throw new Error(`頁面 "${pageName}" 的初始化函數無效`);
        }
    } catch (error) {
        console.error(`載入頁面 "${pageName}" 失敗:`, error);
        // 如果載入失敗，嘗試載入首頁
        if (pageName !== 'home') {
            console.log('嘗試載入首頁作為備用');
            await loadPage('home');
        }
    }
}

/**
 * 導航到指定頁面
 * @param {string} pageName - 頁面名稱
 */
export function navigateTo(pageName) {
    if (!routes[pageName]) {
        console.warn(`頁面 "${pageName}" 不存在`);
        return;
    }
    
    // 更新 URL（不刷新頁面）
    const newUrl = new URL(window.location);
    newUrl.searchParams.set('page', pageName);
    window.history.pushState({ page: pageName }, '', newUrl);
    
    // 載入新頁面
    loadPage(pageName);
}

/**
 * 獲取當前頁面名稱
 */
export function getCurrentPage() {
    return currentPage || 'home';
}

// 監聽瀏覽器前進/後退按鈕
window.addEventListener('popstate', (event) => {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page') || 'home';
    loadPage(page);
});
