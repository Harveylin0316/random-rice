# LINE LIFF App - 今天吃什麼

這是「今天吃什麼」的 LINE LIFF 版本，可以在 LINE 內使用。

## 功能特點

- ✅ 餐廳推薦功能（今天吃什麼）
- ✅ LINE 特定功能（分享、關閉按鈕）
- ✅ 路由系統（支持未來擴展多個頁面）
- ✅ 移動端優化 UI/UX
- ✅ 地理位置功能
- ✅ 餐廳篩選（料理風格、類型、預算、地區）

## 架構說明

```
frontend/liff/
├── index.html              # 主頁面
├── app.js                  # LIFF 初始化和路由啟動
├── style.css              # 樣式文件
├── pages/                 # 頁面模組
│   ├── router.js          # 路由管理器
│   ├── home.js            # 餐廳推薦頁面
│   └── components/        # 組件
│       └── liff-features.js  # LINE 特定功能
└── shared/                # 共享模組（從 frontend/shared 複製）
    ├── api.js
    ├── constants.js
    └── utils.js
```

## 設置步驟

### 1. 獲取 LIFF ID

1. 登入 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇或創建 Provider
3. 創建 **LINE Login Channel**
4. 在 Channel 中創建 **LIFF App**
5. 設置：
   - **LIFF app name**: 今天吃什麼
   - **Size**: Full（全螢幕）
   - **Endpoint URL**: `https://your-site.netlify.app/liff`
   - **Scope**: `profile`（獲取用戶基本資料）
6. 複製 **LIFF ID**

### 2. 配置 LIFF ID

有兩種方式設置 LIFF ID：

**方式 1：在 URL 參數中（測試用）**
```
https://your-site.netlify.app/liff?liffId=你的LIFF_ID
```

**方式 2：在代碼中設置（正式環境）**
編輯 `frontend/liff/app.js`，將 `YOUR_LIFF_ID_HERE` 替換為你的 LIFF ID。

### 3. 部署

確保 `netlify-build.sh` 正確複製了共享模組到 `frontend/liff/shared/`。

## 路由系統

當前支持的路由：
- `/liff` 或 `/liff?page=home` - 餐廳推薦頁面（今天吃什麼）

未來可以添加：
- `/liff?page=favorites` - 我的最愛
- `/liff?page=history` - 搜尋歷史
- `/liff?page=settings` - 設定

### 添加新頁面

1. 在 `frontend/liff/pages/` 創建新頁面文件（例如 `favorites.js`）
2. 在 `router.js` 中添加路由映射：
```javascript
import { initFavoritesPage } from './favorites.js';

const routes = {
    'home': initHomePage,
    'favorites': initFavoritesPage,  // 新增
};
```

## LINE 特定功能

### 分享功能
- 如果支援 `shareTargetPicker` API，會在標題右上角顯示分享按鈕
- 點擊後可以分享給 LINE 好友

### 關閉功能
- 如果在 LINE 內，會在標題左上角顯示關閉按鈕
- 點擊後會關閉 LIFF App

### 外部連結處理
- 在 LINE 內打開外部連結時，會自動使用 `liff.openWindow()` 打開外部瀏覽器

## Rich Menu 配置

在 LINE 官方帳號的 Rich Menu 中，可以設置按鈕連結到：

```
https://your-site.netlify.app/liff?page=home
```

每個按鈕可以對應不同的頁面（通過 `page` 參數）。

## 測試

### 本地測試

1. 啟動後端服務器：
```bash
cd backend
npm start
```

2. 在瀏覽器中打開：
```
http://localhost:3000/liff?liffId=你的LIFF_ID
```

### LINE 內測試

1. 部署到 Netlify
2. 在 LINE Developers Console 設置 LIFF App 的 Endpoint URL
3. 在 LINE 內打開 LIFF App 進行測試

## 注意事項

- LIFF App 必須在 HTTPS 環境下運行（Netlify 自動提供）
- 某些功能（如分享）只在 LINE 內可用
- 地理位置功能需要用戶授權
- 確保 `frontend/shared/` 模組已正確複製到 `frontend/liff/shared/`

## 開發計劃

- [x] 路由系統架構
- [x] 餐廳推薦功能（今天吃什麼）
- [x] LINE 特定功能（分享、關閉）
- [x] UI/UX 優化
- [ ] 我的最愛功能
- [ ] 搜尋歷史功能
- [ ] 設定頁面
- [ ] 用戶個人化功能
