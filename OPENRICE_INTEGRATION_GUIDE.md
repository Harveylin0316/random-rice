# OpenRice 會員資料庫整合指南

## 整合目標

將 LINE LIFF App 與 OpenRice 會員資料庫整合，實現：
- 用戶身份對應（LINE User ID ↔ OpenRice 會員 ID）
- 同步用戶偏好設定
- 同步收藏餐廳
- 同步搜尋歷史
- 個人化推薦

---

## 方案 A：使用 LINE User ID 作為主要識別碼（推薦）

### 架構設計

```
LINE LIFF App
    ↓ (取得 LINE User ID)
後端 API
    ↓ (查詢/建立對應關係)
OpenRice 會員資料庫
    ↓ (儲存/更新資料)
用戶資料同步
```

### 優點
- ✅ 簡單直接
- ✅ 不需要額外認證流程
- ✅ 用戶體驗流暢

### 缺點
- ⚠️ 需要建立 LINE User ID 與 OpenRice 會員的對應表
- ⚠️ 如果用戶沒有 OpenRice 帳號，需要引導註冊

---

## 方案 B：使用 OpenID Connect 整合

### 架構設計

```
LINE LIFF App
    ↓ (取得 OpenID Token)
後端 API
    ↓ (驗證 Token)
OpenRice 會員系統
    ↓ (對應會員資料)
用戶資料同步
```

### 優點
- ✅ 更安全的認證機制
- ✅ 可以取得更多用戶資訊
- ✅ 符合標準認證流程

### 缺點
- ⚠️ 需要設置 `openid` scope
- ⚠️ 實現較複雜

---

## 推薦方案：方案 A（簡化版）

### 步驟 1：建立用戶對應表

在 OpenRice 會員資料庫中新增欄位：

```sql
-- 在 OpenRice 會員表中新增欄位
ALTER TABLE openrice_members 
ADD COLUMN line_user_id VARCHAR(255) UNIQUE,
ADD INDEX idx_line_user_id (line_user_id);
```

或使用 NoSQL（如 MongoDB）：

```javascript
{
    openrice_member_id: "OR123456",
    line_user_id: "U1234567890abcdefghijklmnopqrstuvwxyz",
    display_name: "用戶名稱",
    email: "user@example.com",
    // ... 其他 OpenRice 會員資料
}
```

### 步驟 2：建立後端 API

#### 2.1 用戶對應 API

```javascript
// backend/routes/users.js

// 建立或更新 LINE User ID 與 OpenRice 會員的對應
POST /api/users/link
Body: {
    line_user_id: "U1234567890...",
    openrice_member_id: "OR123456",  // 可選，如果用戶已有 OpenRice 帳號
    email: "user@example.com"         // 可選，用於查找現有會員
}

// 取得用戶資料
GET /api/users/profile?line_user_id=U1234567890...
Response: {
    openrice_member_id: "OR123456",
    display_name: "用戶名稱",
    preferences: { ... },
    favorites: [ ... ],
    history: [ ... ]
}
```

#### 2.2 用戶偏好 API

```javascript
// 儲存用戶偏好
POST /api/users/preferences
Body: {
    line_user_id: "U1234567890...",
    favorite_cuisines: ["台式料理", "日式料理"],
    favorite_types: ["燒肉", "火鍋"],
    budget_range: "500-1000元"
}

// 取得用戶偏好
GET /api/users/preferences?line_user_id=U1234567890...
```

#### 2.3 收藏餐廳 API

```javascript
// 收藏餐廳
POST /api/users/favorites
Body: {
    line_user_id: "U1234567890...",
    restaurant_name: "餐廳名稱"
}

// 取得收藏列表
GET /api/users/favorites?line_user_id=U1234567890...

// 取消收藏
DELETE /api/users/favorites?line_user_id=U1234567890...&restaurant_name=餐廳名稱
```

#### 2.4 搜尋歷史 API

```javascript
// 儲存搜尋歷史
POST /api/users/history
Body: {
    line_user_id: "U1234567890...",
    search_params: {
        cuisine_style: ["台式料理"],
        type: ["燒肉"],
        budget: "500-1000元",
        location: "台北市"
    },
    results_count: 5
}

// 取得搜尋歷史
GET /api/users/history?line_user_id=U1234567890...
```

---

## 步驟 3：前端整合

### 3.1 在 LIFF App 中取得用戶資料

```javascript
// frontend/liff/pages/components/user-integration.js

import { getLiffProfile } from '../../app.js';
import { getApiBaseUrl } from '../../shared/constants.js';

const API_BASE_URL = getApiBaseUrl();

/**
 * 取得或建立用戶對應
 */
export async function linkUserAccount() {
    const profile = getLiffProfile();
    if (!profile || !profile.userId) {
        console.warn('無法取得 LINE User ID');
        return null;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/link`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                line_user_id: profile.userId,
                display_name: profile.displayName,
                picture_url: profile.pictureUrl
            })
        });
        
        if (!response.ok) {
            throw new Error('連結用戶帳號失敗');
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('連結用戶帳號錯誤:', error);
        return null;
    }
}

/**
 * 取得用戶偏好設定
 */
export async function getUserPreferences() {
    const profile = getLiffProfile();
    if (!profile || !profile.userId) {
        return null;
    }
    
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/users/preferences?line_user_id=${profile.userId}`
        );
        
        if (!response.ok) {
            return null; // 用戶可能還沒有偏好設定
        }
        
        return await response.json();
    } catch (error) {
        console.error('取得用戶偏好錯誤:', error);
        return null;
    }
}

/**
 * 儲存用戶偏好設定
 */
export async function saveUserPreferences(preferences) {
    const profile = getLiffProfile();
    if (!profile || !profile.userId) {
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/preferences`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                line_user_id: profile.userId,
                ...preferences
            })
        });
        
        return response.ok;
    } catch (error) {
        console.error('儲存用戶偏好錯誤:', error);
        return false;
    }
}

/**
 * 收藏餐廳
 */
export async function addFavorite(restaurantName) {
    const profile = getLiffProfile();
    if (!profile || !profile.userId) {
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/favorites`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                line_user_id: profile.userId,
                restaurant_name: restaurantName
            })
        });
        
        return response.ok;
    } catch (error) {
        console.error('收藏餐廳錯誤:', error);
        return false;
    }
}

/**
 * 取得收藏列表
 */
export async function getFavorites() {
    const profile = getLiffProfile();
    if (!profile || !profile.userId) {
        return [];
    }
    
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/users/favorites?line_user_id=${profile.userId}`
        );
        
        if (!response.ok) {
            return [];
        }
        
        const data = await response.json();
        return data.favorites || [];
    } catch (error) {
        console.error('取得收藏列表錯誤:', error);
        return [];
    }
}

/**
 * 儲存搜尋歷史
 */
export async function saveSearchHistory(searchParams, resultsCount) {
    const profile = getLiffProfile();
    if (!profile || !profile.userId) {
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/history`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                line_user_id: profile.userId,
                search_params: searchParams,
                results_count: resultsCount,
                timestamp: new Date().toISOString()
            })
        });
        
        return response.ok;
    } catch (error) {
        console.error('儲存搜尋歷史錯誤:', error);
        return false;
    }
}
```

### 3.2 在首頁初始化時連結用戶

```javascript
// frontend/liff/pages/home.js

import { linkUserAccount, getUserPreferences, saveSearchHistory } from './components/user-integration.js';

export async function initHomePage() {
    console.log('初始化首頁：今天吃什麼');
    
    // 連結用戶帳號（如果還沒連結）
    await linkUserAccount();
    
    // 載入用戶偏好設定（如果有）
    const preferences = await getUserPreferences();
    if (preferences) {
        // 應用用戶偏好到表單
        applyUserPreferences(preferences);
    }
    
    // 其他初始化...
}

// 在搜尋完成後儲存歷史
async function onSearchComplete(searchParams, results) {
    await saveSearchHistory(searchParams, results.length);
}
```

---

## 步驟 4：後端實現範例

### 4.1 用戶對應 API 實現

```javascript
// backend/routes/users.js

const express = require('express');
const router = express.Router();

// 假設你有一個資料庫連接
const db = require('../database'); // 你的資料庫連接

/**
 * 建立或更新用戶對應
 */
router.post('/link', async (req, res) => {
    try {
        const { line_user_id, openrice_member_id, email, display_name, picture_url } = req.body;
        
        if (!line_user_id) {
            return res.status(400).json({ error: 'LINE User ID 是必需的' });
        }
        
        // 查找是否已有對應
        let user = await db.query(
            'SELECT * FROM openrice_members WHERE line_user_id = ?',
            [line_user_id]
        );
        
        if (user.length > 0) {
            // 更新現有用戶
            await db.query(
                'UPDATE openrice_members SET display_name = ?, picture_url = ? WHERE line_user_id = ?',
                [display_name, picture_url, line_user_id]
            );
            return res.json({ 
                success: true, 
                message: '用戶資料已更新',
                openrice_member_id: user[0].openrice_member_id
            });
        }
        
        // 如果有提供 OpenRice 會員 ID 或 Email，嘗試查找現有會員
        if (openrice_member_id || email) {
            let existingMember = null;
            
            if (openrice_member_id) {
                existingMember = await db.query(
                    'SELECT * FROM openrice_members WHERE openrice_member_id = ?',
                    [openrice_member_id]
                );
            } else if (email) {
                existingMember = await db.query(
                    'SELECT * FROM openrice_members WHERE email = ?',
                    [email]
                );
            }
            
            if (existingMember && existingMember.length > 0) {
                // 連結到現有會員
                await db.query(
                    'UPDATE openrice_members SET line_user_id = ?, display_name = ?, picture_url = ? WHERE openrice_member_id = ?',
                    [line_user_id, display_name, picture_url, existingMember[0].openrice_member_id]
                );
                return res.json({ 
                    success: true, 
                    message: '已連結到現有 OpenRice 會員',
                    openrice_member_id: existingMember[0].openrice_member_id
                });
            }
        }
        
        // 建立新用戶（如果 OpenRice 允許自動註冊）
        // 或者返回需要註冊的訊息
        return res.json({ 
            success: true, 
            message: '新用戶已建立',
            requires_registration: true // 提示用戶需要註冊 OpenRice 帳號
        });
        
    } catch (error) {
        console.error('連結用戶帳號錯誤:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});

/**
 * 取得用戶資料
 */
router.get('/profile', async (req, res) => {
    try {
        const { line_user_id } = req.query;
        
        if (!line_user_id) {
            return res.status(400).json({ error: 'LINE User ID 是必需的' });
        }
        
        const user = await db.query(
            'SELECT * FROM openrice_members WHERE line_user_id = ?',
            [line_user_id]
        );
        
        if (user.length === 0) {
            return res.status(404).json({ error: '用戶不存在' });
        }
        
        res.json({
            openrice_member_id: user[0].openrice_member_id,
            display_name: user[0].display_name,
            email: user[0].email,
            // ... 其他資料
        });
        
    } catch (error) {
        console.error('取得用戶資料錯誤:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});

module.exports = router;
```

---

## 整合流程圖

```
用戶打開 LIFF App
    ↓
取得 LINE User ID
    ↓
呼叫 /api/users/link
    ↓
檢查是否已有對應
    ├─ 是 → 更新資料 → 返回會員資料
    └─ 否 → 檢查是否有 OpenRice 帳號
            ├─ 是 → 連結帳號 → 返回會員資料
            └─ 否 → 建立新用戶或提示註冊
    ↓
載入用戶偏好設定
    ↓
應用偏好到表單
    ↓
用戶使用功能
    ↓
儲存搜尋歷史、收藏等
```

---

## 資料同步策略

### 1. 即時同步（推薦）
- 每次操作立即同步到 OpenRice 資料庫
- 優點：資料最新
- 缺點：API 呼叫較多

### 2. 批次同步
- 累積操作後批次同步
- 優點：減少 API 呼叫
- 缺點：可能有延遲

### 3. 混合策略
- 重要操作（收藏、偏好）即時同步
- 次要操作（搜尋歷史）批次同步

---

## 安全性考量

### 1. 驗證 LINE User ID
- 確保 LINE User ID 來自合法的 LIFF App
- 可以驗證 LIFF ID Token

### 2. API 認證
- 使用 API Key 或 JWT Token
- 限制 API 呼叫頻率

### 3. 資料加密
- 敏感資料（如 Email）加密儲存
- 使用 HTTPS 傳輸

---

## 實施建議

### 階段 1：基礎整合（MVP）
1. ✅ 建立用戶對應 API
2. ✅ 儲存基本用戶資料
3. ✅ 儲存搜尋歷史

### 階段 2：個人化功能
1. ✅ 用戶偏好設定
2. ✅ 收藏餐廳功能
3. ✅ 個人化推薦

### 階段 3：進階功能
1. ✅ 與 OpenRice 會員系統深度整合
2. ✅ 訂位記錄同步
3. ✅ 評價記錄同步

---

## 需要協助的部分

如果你需要我幫你實現：

1. **後端 API**：我可以幫你建立用戶對應、偏好設定等 API
2. **前端整合**：我可以幫你在 LIFF App 中整合用戶功能
3. **資料庫設計**：我可以幫你設計用戶對應表的結構

告訴我你想從哪個部分開始！
