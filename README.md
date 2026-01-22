# 今天吃什麼？🍽️ - 餐廳推薦系統

一個根據使用者喜好推薦餐廳的網頁應用程式。

## 📁 專案結構

```
random-rice/
├── backend/              # 後端 API
│   ├── server.js        # Express 伺服器
│   ├── routes/          # API 路由
│   └── utils/           # 工具函數
├── frontend/            # 前端頁面
│   ├── index.html      # 主頁面
│   ├── style.css       # 樣式表
│   └── app.js          # JavaScript 邏輯
├── restaurants_database.json  # 餐廳資料庫（888間餐廳）
└── README.md           # 本文件
```

## 🚀 快速開始

### 1. 安裝後端依賴

```bash
cd backend
npm install
```

### 2. 啟動伺服器

```bash
npm start
```

伺服器將運行在 `http://localhost:3000`

### 3. 開啟瀏覽器

在瀏覽器中打開：`http://localhost:3000`

## ✨ 功能特色

### 已實作功能
- ✅ **料理風格篩選**（多選）：中式、日式、韓式、美式、義式等 14 種
- ✅ **餐廳類型篩選**（多選）：火鍋、燒肉、酒吧、餐酒館等 10 種
- ✅ **預算篩選**：200-400、500-800、1000-1500、2000以上
- ✅ **隨機推薦**：每次推薦結果不同
- ✅ **現代化 UI**：響應式設計，美觀易用

### 待實作功能
- ⏳ **距離篩選**：需要餐廳座標資料
- ⏳ **用餐時段篩選**：需要營業時間資料
- ⏳ **線上訂位篩選**：需要訂位相關資料

## 📊 資料庫統計

- **總餐廳數**：888 間
- **料理風格**：14 種
- **餐廳類型**：10 種
- **預算區間**：4 種

## 🛠️ 技術棧

### 後端
- Node.js
- Express.js
- JSON 資料庫

### 前端
- HTML5
- CSS3（現代化設計）
- Vanilla JavaScript（無框架）

## 📝 API 文檔

詳細 API 文檔請參考：`backend/README.md`

### 主要端點

- `GET /api/restaurants/recommend` - 推薦餐廳
- `GET /api/restaurants/filter-options` - 獲取篩選選項
- `GET /api/restaurants/all` - 獲取所有餐廳

## 🎯 使用範例

1. 選擇想吃的料理風格（可多選）
2. 選擇餐廳類型（可多選）
3. 選擇預算區間
4. 點擊「推薦我」按鈕
5. 查看推薦的 5 間餐廳

## 📄 授權

本專案僅供學習使用。

## 🙏 資料來源

餐廳資料來源：OpenRice
