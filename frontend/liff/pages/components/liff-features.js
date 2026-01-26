// LINE LIFF 特定功能模組
// 包含分享、關閉、打開外部瀏覽器等 LINE 特定功能

import { getLiff } from '../../app.js';

/**
 * 初始化 LINE 特定功能
 */
export function initLiffFeatures() {
    const liff = getLiff();
    if (!liff) {
        console.warn('LIFF 未初始化，無法使用 LINE 特定功能');
        return;
    }
    
    // 添加分享按鈕（如果支援）
    if (liff.isApiAvailable('shareTargetPicker')) {
        addShareButton();
    }
    
    // 添加關閉按鈕（如果在 LINE 內）
    if (liff.isInClient()) {
        addCloseButton();
    }
    
    // 優化外部連結處理
    setupExternalLinks();
}

/**
 * 添加分享按鈕
 */
function addShareButton() {
    const header = document.querySelector('.header');
    if (!header) return;
    
    // 檢查是否已經有分享按鈕
    if (document.getElementById('liffShareBtn')) return;
    
    const shareBtn = document.createElement('button');
    shareBtn.id = 'liffShareBtn';
    shareBtn.className = 'liff-share-btn';
    shareBtn.innerHTML = '📤 分享';
    shareBtn.title = '分享給好友';
    
    shareBtn.addEventListener('click', async () => {
        try {
            const liff = getLiff();
            if (!liff || !liff.isApiAvailable('shareTargetPicker')) {
                alert('此功能僅在 LINE 內可用');
                return;
            }
            
            const shareResult = await liff.shareTargetPicker([
                {
                    type: 'text',
                    text: '🍽️ 今天吃什麼？\n\n告訴我你的喜好，我來推薦餐廳給你！\n\n快來試試看吧！'
                }
            ]);
            
            if (shareResult && shareResult.status === 'success') {
                console.log('分享成功');
            }
        } catch (error) {
            console.error('分享失敗:', error);
            if (error.message !== 'User canceled') {
                alert('分享失敗，請稍後再試');
            }
        }
    });
    
    // 將分享按鈕添加到標題區域
    header.style.position = 'relative';
    shareBtn.style.position = 'absolute';
    shareBtn.style.top = '10px';
    shareBtn.style.right = '10px';
    header.appendChild(shareBtn);
}

/**
 * 添加關閉按鈕
 */
function addCloseButton() {
    const header = document.querySelector('.header');
    if (!header) return;
    
    // 檢查是否已經有關閉按鈕
    if (document.getElementById('liffCloseBtn')) return;
    
    const closeBtn = document.createElement('button');
    closeBtn.id = 'liffCloseBtn';
    closeBtn.className = 'liff-close-btn';
    closeBtn.innerHTML = '✕';
    closeBtn.title = '關閉';
    
    closeBtn.addEventListener('click', () => {
        try {
            const liff = getLiff();
            if (liff && liff.isInClient()) {
                liff.closeWindow();
            } else {
                // 如果不在 LINE 內，使用 window.close()
                window.close();
            }
        } catch (error) {
            console.error('關閉失敗:', error);
            // 如果無法關閉，至少可以返回上一頁
            if (window.history.length > 1) {
                window.history.back();
            }
        }
    });
    
    // 將關閉按鈕添加到標題區域
    header.style.position = 'relative';
    closeBtn.style.position = 'absolute';
    closeBtn.style.top = '10px';
    closeBtn.style.left = '10px';
    header.appendChild(closeBtn);
}

/**
 * 設置外部連結處理
 * 在 LINE 內打開外部連結時，使用 liff.openWindow()
 */
function setupExternalLinks() {
    const liff = getLiff();
    if (!liff || !liff.isInClient()) return;
    
    // 監聽所有外部連結點擊
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a[href^="http"]');
        if (!link) return;
        
        const href = link.getAttribute('href');
        if (!href) return;
        
        // 如果是當前域名，不需要特殊處理
        try {
            const url = new URL(href);
            if (url.hostname === window.location.hostname) {
                return;
            }
        } catch (error) {
            return;
        }
        
        // 阻止默認行為
        e.preventDefault();
        
        // 使用 liff.openWindow() 打開外部連結
        try {
            liff.openWindow({
                url: href,
                external: true
            });
        } catch (error) {
            console.error('打開外部連結失敗:', error);
            // 如果失敗，使用 window.open() 作為備用
            window.open(href, '_blank');
        }
    }, true);
}

/**
 * 獲取用戶資料（如果已登入）
 */
export async function getLiffUserProfile() {
    const liff = getLiff();
    if (!liff || !liff.isLoggedIn()) {
        return null;
    }
    
    try {
        return await liff.getProfile();
    } catch (error) {
        console.error('獲取用戶資料失敗:', error);
        return null;
    }
}

/**
 * 發送訊息給用戶（需要 Messaging API）
 */
export async function sendMessage(message) {
    const liff = getLiff();
    if (!liff) {
        console.warn('LIFF 未初始化');
        return false;
    }
    
    // 注意：這個功能需要 Messaging API Channel，並且需要用戶已經加入官方帳號
    // 這裡只是提供一個接口，實際實現需要後端支持
    try {
        // 這裡應該調用後端 API 來發送訊息
        // 暫時只記錄日誌
        console.log('發送訊息:', message);
        return true;
    } catch (error) {
        console.error('發送訊息失敗:', error);
        return false;
    }
}
