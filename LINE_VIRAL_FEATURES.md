# LINE 裂變行銷功能設計建議

## 核心目標

1. ✅ 讓用戶樂於分享
2. ✅ 吸引新用戶加入 LINE 官方好友
3. ✅ 增加用戶互動和參與度
4. ✅ 提升品牌曝光

---

## 功能建議

### 功能 1：好友一起選餐廳（推薦 ⭐⭐⭐⭐⭐）

#### 概念
讓用戶可以分享餐廳推薦給好友，好友可以投票或一起選擇餐廳。

#### 流程設計

```
用戶 A 使用「今天吃什麼」獲得推薦
    ↓
點擊「分享給好友一起選」
    ↓
生成分享連結（包含推薦的餐廳列表）
    ↓
分享到 LINE 群組或好友
    ↓
好友點擊連結打開 LIFF App（新頁面：?page=group-select）
    ↓
顯示餐廳列表，好友可以：
- 投票喜歡的餐廳
- 查看投票結果
- 加入官方帳號獲得更多功能
    ↓
投票結束後，顯示最受歡迎的餐廳
```

#### 實現細節

**分享連結格式：**
```
https://liff.line.me/2008944358-649rLhGj?page=group-select&session_id=abc123&restaurants=餐廳1,餐廳2,餐廳3
```

**功能頁面：** `frontend/liff/pages/group-select.js`

**核心功能：**
- 顯示分享的餐廳列表
- 好友投票功能
- 即時顯示投票結果
- 引導加入官方帳號（「加入官方帳號，解鎖更多功能」）

**裂變點：**
- ✅ 用戶會主動分享到群組
- ✅ 好友點擊連結會打開 LIFF App
- ✅ 在投票頁面引導加入官方帳號
- ✅ 可以追蹤分享來源（誰分享的）

---

### 功能 2：推薦碼系統（推薦 ⭐⭐⭐⭐）

#### 概念
用戶分享推薦碼，新用戶使用推薦碼加入官方帳號，雙方都獲得獎勵。

#### 流程設計

```
用戶 A 在 LIFF App 中取得專屬推薦碼
    ↓
分享推薦碼給好友（透過 LINE 分享）
    ↓
好友 B 點擊連結，打開 LIFF App（?page=invite&code=ABC123）
    ↓
顯示「使用推薦碼加入官方帳號，獲得優惠券！」
    ↓
引導加入官方帳號
    ↓
加入成功後：
- 用戶 A 獲得推薦獎勵（優惠券/積分）
- 用戶 B 獲得新人獎勵（優惠券/積分）
```

#### 實現細節

**推薦碼格式：**
```
https://liff.line.me/2008944358-649rLhGj?page=invite&code=ABC123
```

**功能頁面：** `frontend/liff/pages/invite.js`

**核心功能：**
- 生成專屬推薦碼（基於 LINE User ID）
- 顯示推薦碼和分享按鈕
- 追蹤推薦關係
- 獎勵系統（優惠券/積分）

**裂變點：**
- ✅ 用戶有動機分享（獲得獎勵）
- ✅ 新用戶有動機加入（獲得優惠）
- ✅ 可以追蹤推薦鏈

---

### 功能 3：餐廳投票競賽（推薦 ⭐⭐⭐⭐）

#### 概念
定期舉辦「本週最想吃的餐廳」投票，用戶分享投票頁面，吸引更多人參與。

#### 流程設計

```
每週推出「本週最想吃的餐廳」投票
    ↓
用戶在 LIFF App 中投票（?page=vote&week=2024-W04）
    ↓
投票後顯示「分享給好友，一起投票！」
    ↓
分享到 LINE 群組或好友
    ↓
好友點擊連結參與投票
    ↓
顯示即時投票結果
    ↓
引導加入官方帳號查看完整結果和獲得優惠
```

#### 實現細節

**投票頁面：** `frontend/liff/pages/vote.js`

**核心功能：**
- 每週精選餐廳投票
- 即時顯示投票結果
- 分享投票頁面
- 投票後引導加入官方帳號

**裂變點：**
- ✅ 用戶會分享有趣的投票
- ✅ 好友會參與投票
- ✅ 可以追蹤投票參與度

---

### 功能 4：好友推薦餐廳（推薦 ⭐⭐⭐）

#### 概念
讓用戶可以推薦餐廳給好友，好友可以查看推薦並加入官方帳號獲得優惠。

#### 流程設計

```
用戶 A 找到喜歡的餐廳
    ↓
點擊「推薦給好友」
    ↓
選擇要推薦的好友或分享到群組
    ↓
生成推薦卡片（包含餐廳資訊和優惠）
    ↓
好友點擊連結，打開 LIFF App（?page=recommendation&restaurant=餐廳名稱）
    ↓
顯示推薦的餐廳資訊
    ↓
「加入官方帳號，獲得這間餐廳的專屬優惠！」
```

#### 實現細節

**推薦頁面：** `frontend/liff/pages/recommendation.js`

**核心功能：**
- 顯示推薦的餐廳資訊
- 顯示推薦人資訊
- 引導加入官方帳號
- 追蹤推薦效果

**裂變點：**
- ✅ 用戶會推薦喜歡的餐廳
- ✅ 好友會查看推薦
- ✅ 優惠吸引加入官方帳號

---

### 功能 5：挑戰任務系統（推薦 ⭐⭐⭐）

#### 概念
設計挑戰任務，完成任務後分享成果，吸引好友參與。

#### 流程設計

```
用戶完成挑戰任務：
- 「本週嘗試 3 種不同料理風格」
- 「推薦 5 間餐廳給好友」
- 「加入官方帳號獲得專屬挑戰」
    ↓
完成任務後顯示「分享你的成就！」
    ↓
生成成就卡片，分享到 LINE
    ↓
好友點擊連結，看到成就並被吸引參與
    ↓
引導加入官方帳號參與挑戰
```

#### 實現細節

**挑戰頁面：** `frontend/liff/pages/challenge.js`

**核心功能：**
- 顯示挑戰任務列表
- 追蹤任務進度
- 完成任務後分享成就
- 引導加入官方帳號

**裂變點：**
- ✅ 用戶會分享成就
- ✅ 好友會被吸引參與
- ✅ 增加用戶黏著度

---

## 推薦組合方案

### 方案 A：好友一起選餐廳 + 推薦碼系統（最推薦 ⭐⭐⭐⭐⭐）

**優點：**
- 實用性高（解決真實需求：一群人選餐廳）
- 裂變效果強（會分享到群組）
- 可以追蹤推薦關係
- 雙重引導加入官方帳號

**實現優先級：**
1. 先實現「好友一起選餐廳」
2. 再加入推薦碼系統

---

### 方案 B：餐廳投票競賽 + 推薦碼系統

**優點：**
- 趣味性高
- 定期活動，持續吸引用戶
- 可以追蹤參與度

---

## 技術實現建議

### 1. 路由設計

```javascript
// frontend/liff/pages/router.js

const routes = {
    'home': initHomePage,              // 今天吃什麼（已有）
    'group-select': initGroupSelectPage,  // 好友一起選餐廳
    'invite': initInvitePage,          // 推薦碼系統
    'vote': initVotePage,              // 餐廳投票競賽
    'recommendation': initRecommendationPage, // 好友推薦餐廳
    'challenge': initChallengePage     // 挑戰任務系統
};
```

### 2. 分享功能實現

```javascript
// frontend/liff/pages/components/sharing.js

/**
 * 分享到 LINE
 */
export async function shareToLine(shareData) {
    const liff = getLiff();
    
    if (!liff || !liff.isApiAvailable('shareTargetPicker')) {
        // 如果不在 LINE 內，使用 Deep Link
        const shareUrl = generateShareUrl(shareData);
        return shareUrl;
    }
    
    try {
        const shareResult = await liff.shareTargetPicker([
            {
                type: 'text',
                text: shareData.message
            },
            {
                type: 'text',
                text: shareData.url
            }
        ]);
        
        return shareResult;
    } catch (error) {
        console.error('分享失敗:', error);
        return null;
    }
}

/**
 * 生成分享連結
 */
function generateShareUrl(shareData) {
    const baseUrl = 'https://liff.line.me/2008944358-649rLhGj';
    const params = new URLSearchParams();
    
    if (shareData.page) {
        params.set('page', shareData.page);
    }
    if (shareData.sessionId) {
        params.set('session_id', shareData.sessionId);
    }
    if (shareData.code) {
        params.set('code', shareData.code);
    }
    if (shareData.restaurants) {
        params.set('restaurants', shareData.restaurants.join(','));
    }
    
    return `${baseUrl}?${params.toString()}`;
}
```

### 3. 追蹤分享來源

```javascript
// 追蹤分享來源
export function trackShare(sourceUserId, shareType, shareData) {
    fetch(`${API_BASE_URL}/api/analytics/track-share`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            source_user_id: sourceUserId,
            share_type: shareType, // 'group-select', 'invite', 'vote', etc.
            share_data: shareData,
            timestamp: new Date().toISOString()
        })
    });
}
```

---

## 引導加入官方帳號的策略

### 1. 時機點

- ✅ 分享後：顯示「加入官方帳號，獲得更多功能」
- ✅ 投票後：顯示「加入官方帳號，查看完整結果」
- ✅ 使用推薦碼：顯示「加入官方帳號，獲得優惠券」
- ✅ 查看推薦：顯示「加入官方帳號，獲得專屬優惠」

### 2. 誘因設計

- 🎁 **優惠券**：加入後獲得餐廳優惠券
- 🎁 **積分系統**：加入後獲得積分，可兌換優惠
- 🎁 **專屬功能**：加入後解鎖更多功能
- 🎁 **優先通知**：加入後優先收到新餐廳通知

### 3. UI 設計

```javascript
// 加入官方帳號的按鈕組件
function showJoinOfficialAccountPrompt(reason) {
    const prompt = `
        <div class="join-official-prompt">
            <h3>🎁 加入官方帳號，獲得更多好處！</h3>
            <p>${reason}</p>
            <ul>
                <li>✅ 獲得專屬優惠券</li>
                <li>✅ 優先收到新餐廳通知</li>
                <li>✅ 解鎖更多功能</li>
            </ul>
            <button onclick="joinOfficialAccount()">
                立即加入
            </button>
        </div>
    `;
    // 顯示提示
}

function joinOfficialAccount() {
    const liff = getLiff();
    if (liff && liff.isInClient()) {
        // 使用 LINE 官方帳號加入連結
        liff.openWindow({
            url: 'https://line.me/R/ti/p/@your-official-account-id',
            external: true
        });
    }
}
```

---

## 數據追蹤指標

### 1. 分享指標
- 分享次數
- 分享類型分布
- 分享轉換率（分享 → 點擊）

### 2. 裂變指標
- 新用戶來源（推薦碼/分享連結）
- 推薦鏈深度
- 每個用戶的平均推薦數

### 3. 官方帳號加入指標
- 從 LIFF App 加入官方帳號的數量
- 加入轉換率
- 加入來源分析

---

## 實施建議

### 階段 1：MVP（最小可行產品）
1. ✅ 實現「好友一起選餐廳」功能
2. ✅ 基本的分享功能
3. ✅ 引導加入官方帳號的提示

### 階段 2：增強功能
1. ✅ 推薦碼系統
2. ✅ 追蹤分享來源
3. ✅ 獎勵系統

### 階段 3：進階功能
1. ✅ 餐廳投票競賽
2. ✅ 挑戰任務系統
3. ✅ 完整的數據分析

---

## 總結

### 最推薦的功能組合

**方案：好友一起選餐廳 + 推薦碼系統**

**理由：**
1. ✅ 解決真實需求（一群人選餐廳）
2. ✅ 裂變效果強（會分享到群組）
3. ✅ 可以追蹤推薦關係
4. ✅ 雙重引導加入官方帳號
5. ✅ 實現難度適中

### 實施步驟

1. **第一步**：實現「好友一起選餐廳」功能
   - 創建 `group-select.js` 頁面
   - 實現分享功能
   - 實現投票功能
   - 引導加入官方帳號

2. **第二步**：加入推薦碼系統
   - 創建 `invite.js` 頁面
   - 實現推薦碼生成和追蹤
   - 實現獎勵系統

3. **第三步**：數據追蹤和分析
   - 追蹤分享來源
   - 分析裂變效果
   - 優化引導策略

需要我幫你開始實現「好友一起選餐廳」功能嗎？
