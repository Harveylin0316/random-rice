# LINE 官方帳號加入功能實作指南

## 方法 1：使用 LINE 官方帳號加入連結（推薦 ⭐⭐⭐⭐⭐）

### 實作方式

#### 1.1 取得官方帳號 ID

在 LINE Developers Console 中：
1. 選擇你的 **Messaging API Channel**（官方帳號）
2. 在「Basic settings」中找到 **Channel ID** 或 **Official Account ID**
3. 格式通常是：`@your-official-account-id` 或數字 ID

#### 1.2 在 LIFF App 中使用

```javascript
// frontend/liff/pages/components/official-account.js

import { getLiff } from '../../app.js';

/**
 * 引導用戶加入 LINE 官方帳號
 */
export function joinOfficialAccount() {
    const liff = getLiff();
    
    // 官方帳號加入連結格式
    const officialAccountId = '@your-official-account-id'; // 替換為你的官方帳號 ID
    const joinUrl = `https://line.me/R/ti/p/${officialAccountId}`;
    
    if (liff && liff.isInClient()) {
        // 在 LINE 內，使用 liff.openWindow() 打開
        try {
            liff.openWindow({
                url: joinUrl,
                external: false  // 在 LINE 內打開，不是外部瀏覽器
            });
        } catch (error) {
            console.error('打開官方帳號失敗:', error);
            // 備用方案：使用 window.open()
            window.open(joinUrl, '_blank');
        }
    } else {
        // 不在 LINE 內，使用 window.open()
        window.open(joinUrl, '_blank');
    }
}
```

#### 1.3 使用範例

```javascript
// 在投票頁面中使用
function showVoteResults() {
    // 顯示投票結果
    displayVoteResults();
    
    // 顯示加入官方帳號的提示
    showJoinPrompt('加入官方帳號，查看完整投票結果和獲得專屬優惠！');
}

function showJoinPrompt(message) {
    const prompt = `
        <div class="join-official-prompt">
            <h3>🎁 ${message}</h3>
            <ul>
                <li>✅ 查看完整投票結果</li>
                <li>✅ 獲得專屬優惠券</li>
                <li>✅ 優先收到新餐廳通知</li>
            </ul>
            <button onclick="joinOfficialAccount()" class="join-btn">
                立即加入官方帳號
            </button>
        </div>
    `;
    // 顯示提示
}
```

---

## 方法 2：使用 LINE Messaging API（需要官方帳號）

### 實作方式

如果你有 Messaging API Channel，可以使用以下方式：

#### 2.1 檢查是否已加入官方帳號

```javascript
/**
 * 檢查用戶是否已加入官方帳號
 */
export async function checkOfficialAccountFriendship() {
    const liff = getLiff();
    
    if (!liff) {
        return false;
    }
    
    try {
        // 需要設置 'friends' scope
        if (liff.isApiAvailable('friendship')) {
            const friendship = await liff.getFriendship();
            return friendship.friendFlag; // true = 已加入, false = 未加入
        }
    } catch (error) {
        console.error('檢查好友關係失敗:', error);
        return false;
    }
    
    return false;
}
```

**注意**：
- 需要設置 `friends` scope（在 LIFF App 設定中）
- 需要用戶已經加入官方帳號為好友才能使用
- 如果用戶還沒加入，無法使用這個 API

#### 2.2 使用方式

```javascript
// 在投票頁面中
async function initVotePage() {
    // 檢查是否已加入官方帳號
    const isFriend = await checkOfficialAccountFriendship();
    
    if (!isFriend) {
        // 顯示加入提示
        showJoinPrompt('加入官方帳號，解鎖完整功能！');
    } else {
        // 已加入，顯示完整功能
        showFullFeatures();
    }
}
```

---

## 方法 3：使用 QR Code（適合線下推廣）

### 實作方式

#### 3.1 生成官方帳號 QR Code

```javascript
/**
 * 生成官方帳號 QR Code
 */
export function generateOfficialAccountQRCode() {
    const officialAccountId = '@your-official-account-id';
    const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=https://line.me/R/ti/p/${officialAccountId}`;
    
    return qrCodeUrl;
}

// 顯示 QR Code
function showQRCodeModal() {
    const qrCodeUrl = generateOfficialAccountQRCode();
    const modal = `
        <div class="qr-code-modal">
            <h3>掃描 QR Code 加入官方帳號</h3>
            <img src="${qrCodeUrl}" alt="官方帳號 QR Code">
            <p>使用 LINE 掃描 QR Code 即可加入</p>
        </div>
    `;
    // 顯示模態框
}
```

---

## 完整實作範例：投票競賽功能

### 投票頁面實現

```javascript
// frontend/liff/pages/vote.js

import { getLiff, getLiffProfile } from '../app.js';
import { checkOfficialAccountFriendship, joinOfficialAccount } from './components/official-account.js';

let currentVote = null;
let hasJoinedOfficialAccount = false;

/**
 * 初始化投票頁面
 */
export async function initVotePage() {
    console.log('初始化投票頁面');
    
    // 檢查 URL 參數
    const urlParams = new URLSearchParams(window.location.search);
    const week = urlParams.get('week') || getCurrentWeek();
    const voteId = urlParams.get('vote_id');
    
    // 載入投票資料
    await loadVoteData(week, voteId);
    
    // 檢查是否已加入官方帳號
    hasJoinedOfficialAccount = await checkOfficialAccountFriendship();
    
    // 渲染投票頁面
    renderVotePage();
    
    // 如果未加入，顯示加入提示
    if (!hasJoinedOfficialAccount) {
        showJoinPrompt();
    }
}

/**
 * 載入投票資料
 */
async function loadVoteData(week, voteId) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/votes?week=${week}&vote_id=${voteId}`
        );
        currentVote = await response.json();
    } catch (error) {
        console.error('載入投票資料錯誤:', error);
    }
}

/**
 * 渲染投票頁面
 */
function renderVotePage() {
    const container = document.getElementById('mainContent');
    
    container.innerHTML = `
        <div class="vote-page">
            <h2>${currentVote.title}</h2>
            <p class="vote-description">${currentVote.description}</p>
            
            <div class="vote-options">
                ${currentVote.restaurants.map((restaurant, index) => `
                    <div class="vote-option" data-restaurant-id="${restaurant.id}">
                        <div class="restaurant-info">
                            <h3>${restaurant.name}</h3>
                            <p>${restaurant.address}</p>
                        </div>
                        <button class="vote-btn" onclick="voteForRestaurant(${restaurant.id})">
                            投票
                        </button>
                        <div class="vote-count" id="vote-count-${restaurant.id}">
                            ${restaurant.voteCount || 0} 票
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <div class="vote-actions">
                <button class="share-btn" onclick="shareVote()">
                    📤 分享給好友一起投票
                </button>
            </div>
            
            ${!hasJoinedOfficialAccount ? `
                <div id="joinPrompt" class="join-prompt">
                    <!-- 加入提示會動態顯示 -->
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * 投票
 */
async function voteForRestaurant(restaurantId) {
    const profile = getLiffProfile();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/votes/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vote_id: currentVote.id,
                restaurant_id: restaurantId,
                line_user_id: profile?.userId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 更新投票數
            updateVoteCount(restaurantId, result.newCount);
            
            // 如果未加入官方帳號，顯示加入提示
            if (!hasJoinedOfficialAccount) {
                showJoinPromptAfterVote();
            } else {
                // 已加入，顯示完整結果
                showFullResults();
            }
        }
    } catch (error) {
        console.error('投票錯誤:', error);
    }
}

/**
 * 投票後顯示加入提示
 */
function showJoinPromptAfterVote() {
    const prompt = document.getElementById('joinPrompt');
    if (!prompt) return;
    
    prompt.innerHTML = `
        <div class="join-official-prompt">
            <h3>🎁 加入官方帳號，解鎖更多功能！</h3>
            <p>您已投票成功！加入官方帳號可以：</p>
            <ul>
                <li>✅ 查看完整投票結果和排名</li>
                <li>✅ 獲得投票餐廳的專屬優惠券</li>
                <li>✅ 優先收到新投票活動通知</li>
                <li>✅ 參與更多專屬活動</li>
            </ul>
            <button class="join-btn" onclick="joinOfficialAccount()">
                立即加入官方帳號
            </button>
            <button class="skip-btn" onclick="hideJoinPrompt()">
                稍後再說
            </button>
        </div>
    `;
    
    prompt.style.display = 'block';
}

/**
 * 分享投票
 */
async function shareVote() {
    const liff = getLiff();
    const profile = getLiffProfile();
    
    const shareUrl = generateVoteShareUrl(currentVote.id);
    const shareMessage = `🍽️ 本週最想吃的餐廳投票！\n\n快來投票選出你最想吃的餐廳！\n\n${shareUrl}`;
    
    if (liff && liff.isApiAvailable('shareTargetPicker')) {
        try {
            await liff.shareTargetPicker([
                {
                    type: 'text',
                    text: shareMessage
                }
            ]);
            
            // 追蹤分享
            trackShare(profile?.userId, 'vote', {
                vote_id: currentVote.id,
                week: currentVote.week
            });
        } catch (error) {
            console.error('分享失敗:', error);
        }
    } else {
        // 備用方案：複製連結
        navigator.clipboard.writeText(shareUrl);
        alert('連結已複製到剪貼簿！');
    }
}

/**
 * 生成投票分享連結
 */
function generateVoteShareUrl(voteId) {
    const baseUrl = 'https://liff.line.me/2008944358-649rLhGj';
    return `${baseUrl}?page=vote&vote_id=${voteId}`;
}
```

---

## 官方帳號加入連結格式

### 格式 1：使用官方帳號 ID（推薦）

```
https://line.me/R/ti/p/@your-official-account-id
```

**取得方式：**
1. 在 LINE Developers Console 選擇 Messaging API Channel
2. 在「Basic settings」中找到 **Channel ID**
3. 如果是 `@` 開頭，直接使用
4. 如果是數字，格式為：`https://line.me/R/ti/p/@數字`

### 格式 2：使用數字 ID

```
https://line.me/R/ti/p/@1234567890
```

### 格式 3：使用 LINE ID（如果設置了）

```
https://line.me/R/ti/p/@your-line-id
```

---

## 最佳實踐

### 1. 時機點選擇

**推薦時機：**
- ✅ 投票後：顯示「加入官方帳號，查看完整結果」
- ✅ 分享前：顯示「加入官方帳號，獲得更多好處」
- ✅ 查看結果時：顯示「加入官方帳號，解鎖完整功能」

**不推薦：**
- ❌ 一進入就強制要求加入
- ❌ 每次操作都彈出提示

### 2. 誘因設計

**有效誘因：**
- 🎁 專屬優惠券
- 🎁 完整功能解鎖
- 🎁 優先通知
- 🎁 積分獎勵

### 3. UI 設計

**推薦設計：**
- 使用明顯但不打擾的提示
- 提供「稍後再說」選項
- 說明加入的好處
- 使用視覺吸引的按鈕

---

## 注意事項

### 1. Scope 設定

如果要使用 `liff.getFriendship()` 檢查好友關係：
- 需要在 LIFF App 設定中勾選 `friends` scope
- 但這個 API 只能在用戶已加入官方帳號後使用
- 如果用戶還沒加入，無法使用這個 API 檢查

### 2. 推薦方案

**最推薦：使用加入連結 + 追蹤**

1. 使用 `liff.openWindow()` 打開官方帳號加入連結
2. 追蹤點擊加入按鈕的用戶
3. 通過後端 API 檢查用戶是否已加入（使用 Messaging API）

### 3. 追蹤加入狀態

```javascript
// 後端 API 檢查用戶是否已加入官方帳號
// 使用 LINE Messaging API 的 Get profile API
async function checkUserJoinedOfficialAccount(lineUserId) {
    // 使用 Messaging API 的 Channel Access Token
    const response = await fetch(
        `https://api.line.me/v2/bot/profile/${lineUserId}`,
        {
            headers: {
                'Authorization': `Bearer ${CHANNEL_ACCESS_TOKEN}`
            }
        }
    );
    
    if (response.ok) {
        return true; // 已加入
    } else if (response.status === 404) {
        return false; // 未加入
    }
    
    return null; // 無法判斷
}
```

---

## 總結

### 最推薦的實作方式

**使用官方帳號加入連結：**

```javascript
function joinOfficialAccount() {
    const officialAccountId = '@your-official-account-id';
    const joinUrl = `https://line.me/R/ti/p/${officialAccountId}`;
    
    const liff = getLiff();
    if (liff && liff.isInClient()) {
        liff.openWindow({
            url: joinUrl,
            external: false
        });
    } else {
        window.open(joinUrl, '_blank');
    }
}
```

### 實施步驟

1. **取得官方帳號 ID**
   - 在 LINE Developers Console 中找到 Channel ID

2. **在投票頁面中實現**
   - 投票後顯示加入提示
   - 點擊按鈕打開加入連結

3. **追蹤加入狀態**
   - 使用 Messaging API 檢查用戶是否已加入
   - 記錄加入轉換率

4. **優化引導策略**
   - 根據數據調整提示時機和內容

需要我提供更詳細的實現範例嗎？
