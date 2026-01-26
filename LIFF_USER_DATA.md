# LINE LIFF 可取得的用戶資料

## 當前已獲取的資料

根據 `frontend/liff/app.js`，目前我們已經獲取了：

```javascript
if (liff.isLoggedIn()) {
    liffProfile = await liff.getProfile();
    console.log('用戶資料:', liffProfile);
}
```

## LIFF getProfile() 可取得的資料

### 基本資料（需要 `profile` scope）

當用戶授權 `profile` scope 後，可以取得：

```javascript
{
    userId: "U1234567890abcdefghijklmnopqrstuvwxyz",  // LINE User ID
    displayName: "用戶名稱",                           // 顯示名稱
    pictureUrl: "https://profile.line-scdn.net/...",  // 大頭貼 URL
    statusMessage: "我的狀態訊息"                      // 狀態訊息（可能為空）
}
```

### 詳細說明

#### 1. **userId** (LINE User ID)
- **類型**: String
- **說明**: 用戶的 LINE User ID，這是唯一識別碼
- **用途**: 
  - 識別用戶身份
  - 儲存用戶偏好設定
  - 追蹤用戶行為
- **注意**: 這個 ID 是固定的，不會改變

#### 2. **displayName** (顯示名稱)
- **類型**: String
- **說明**: 用戶在 LINE 中設定的顯示名稱
- **用途**: 
  - 個人化體驗（顯示「歡迎，XXX」）
  - 用戶識別
- **注意**: 用戶可以隨時更改

#### 3. **pictureUrl** (大頭貼)
- **類型**: String (URL)
- **說明**: 用戶大頭貼的圖片 URL
- **用途**: 
  - 顯示用戶頭像
  - 個人化 UI
- **注意**: 
  - URL 有時效性（會過期）
  - 需要處理圖片載入失敗的情況

#### 4. **statusMessage** (狀態訊息)
- **類型**: String
- **說明**: 用戶的狀態訊息
- **用途**: 
  - 顯示用戶狀態
  - 個人化體驗
- **注意**: 
  - 可能為空字串
  - 用戶可能沒有設定

## 其他可取得的資料（需要額外 scope）

### OpenID Connect 資料（需要 `openid` scope）

如果設置了 `openid` scope，可以使用 `liff.getDecodedIDToken()` 取得：

```javascript
const idToken = await liff.getDecodedIDToken();
console.log('ID Token:', idToken);
```

可取得的資料：
- `iss`: 發行者
- `sub`: 用戶 ID（與 userId 相同）
- `aud`: 受眾
- `exp`: 過期時間
- `iat`: 發行時間
- `amr`: 認證方法
- `name`: 用戶名稱
- `picture`: 大頭貼 URL

### 好友關係（需要 `friends` scope）

如果設置了 `friends` scope，可以檢查好友關係：

```javascript
const friendshipStatus = await liff.getFriendship();
console.log('好友關係:', friendshipStatus);
```

可取得的資料：
- `friendFlag`: 是否為好友（boolean）

**注意**: `friends` scope 需要官方帳號，且用戶必須加入官方帳號為好友。

## 當前代碼中的使用情況

### 已獲取但未使用

目前代碼中獲取了 `liffProfile`，但還沒有實際使用：

```javascript
// frontend/liff/app.js
if (liff.isLoggedIn()) {
    liffProfile = await liff.getProfile();
    console.log('用戶資料:', liffProfile);
    // 目前只是記錄到 console，沒有實際使用
}
```

### 可用的資料

```javascript
liffProfile.userId          // LINE User ID
liffProfile.displayName     // 顯示名稱
liffProfile.pictureUrl      // 大頭貼 URL
liffProfile.statusMessage   // 狀態訊息
```

## 實際應用建議

### 1. 個人化體驗

```javascript
// 顯示歡迎訊息
if (liffProfile) {
    document.getElementById('welcomeMessage').textContent = 
        `歡迎，${liffProfile.displayName}！`;
}

// 顯示用戶頭像
if (liffProfile && liffProfile.pictureUrl) {
    document.getElementById('userAvatar').src = liffProfile.pictureUrl;
}
```

### 2. 儲存用戶偏好

```javascript
// 使用 userId 作為唯一識別碼
const userPreferences = {
    userId: liffProfile.userId,
    favoriteCuisines: [],
    favoriteRestaurants: [],
    // ...
};
localStorage.setItem(`user_${liffProfile.userId}`, JSON.stringify(userPreferences));
```

### 3. 用戶識別

```javascript
// 記錄用戶行為
function trackUserAction(action) {
    console.log(`User ${liffProfile.userId} performed: ${action}`);
    // 可以發送到後端 API 記錄
}
```

## 權限設定

### 當前設定

在 LINE Developers Console 中，你的 LIFF App 應該設置了：
- ✅ **profile**: 獲取用戶基本資料（userId, displayName, pictureUrl, statusMessage）

### 可選設定

- ❌ **openid**: OpenID Connect（如果需要更多認證資訊）
- ❌ **friends**: 好友關係（需要官方帳號）

## 資料隱私注意事項

1. **用戶同意**: 用戶必須同意授權才能取得資料
2. **資料保護**: 不要將用戶資料分享給第三方
3. **資料使用**: 僅用於提供服務，不要用於其他目的
4. **資料儲存**: 如果需要儲存，要符合隱私政策

## 範例：使用用戶資料

```javascript
// 在 home.js 中使用
import { getLiffProfile } from '../app.js';

async function initHomePage() {
    const profile = getLiffProfile();
    
    if (profile) {
        // 顯示個人化歡迎訊息
        const header = document.querySelector('.header h1');
        if (header) {
            header.textContent = `🍽️ ${profile.displayName}，今天吃什麼？`;
        }
        
        // 顯示用戶頭像（如果需要的話）
        // ...
    }
    
    // 其他初始化...
}
```

## 總結

### 當前可取得的資料（已設置 profile scope）

1. ✅ **userId**: LINE User ID（唯一識別碼）
2. ✅ **displayName**: 顯示名稱
3. ✅ **pictureUrl**: 大頭貼 URL
4. ✅ **statusMessage**: 狀態訊息

### 需要額外設置才能取得的資料

1. ❌ **OpenID Connect 資料**: 需要 `openid` scope
2. ❌ **好友關係**: 需要 `friends` scope 和官方帳號

### 建議

- 當前設置（`profile` scope）已經足夠基本使用
- 如果需要個人化體驗，可以使用 `displayName` 和 `pictureUrl`
- 如果需要儲存用戶偏好，可以使用 `userId` 作為唯一識別碼
