# 今天吃什麼 - 餐廳推薦系統後端 API

## 專案結構

```
backend/
├── server.js              # Express 伺服器主檔案
├── package.json           # 專案依賴配置
├── routes/
│   └── restaurants.js    # 餐廳相關 API 路由
└── utils/
    └── recommendation.js # 推薦演算法邏輯
```

## 安裝與啟動

### 1. 安裝依賴
```bash
cd backend
npm install
```

### 2. 啟動伺服器
```bash
npm start
# 或
node server.js
```

伺服器將運行在 `http://localhost:3000`

## API 端點

### 1. 推薦餐廳
**GET** `/api/restaurants/recommend`

根據篩選條件推薦餐廳。

**Query Parameters:**
- `cuisine_style` (可選): 料理風格，多選用逗號分隔，例如 `韓式,日式`
- `type` (可選): 餐廳類型，多選用逗號分隔，例如 `火鍋,燒肉`
- `budget` (可選): 預算區間，例如 `500-800`, `2000以上`
- `limit` (可選): 返回數量，預設為 5

**範例請求:**
```bash
# 推薦韓式火鍋，預算 500-800 元，返回 3 間
curl "http://localhost:3000/api/restaurants/recommend?cuisine_style=韓式&type=火鍋&budget=500-800&limit=3"

# 推薦所有燒肉餐廳
curl "http://localhost:3000/api/restaurants/recommend?type=燒肉"

# 隨機推薦 5 間餐廳（無篩選條件）
curl "http://localhost:3000/api/restaurants/recommend"
```

**回應格式:**
```json
{
  "success": true,
  "count": 3,
  "filters": {
    "cuisine_style": ["韓式"],
    "type": ["火鍋"],
    "budget": "500-800"
  },
  "restaurants": [
    {
      "name": "餐廳名稱",
      "address": "餐廳地址",
      "cuisine_style": ["韓式"],
      "type": ["火鍋"],
      "budget": "500-800",
      "url": "https://..."
    }
  ]
}
```

### 2. 獲取篩選選項
**GET** `/api/restaurants/filter-options`

獲取所有可用的篩選選項（料理風格、餐廳類型、預算區間）。

**範例請求:**
```bash
curl "http://localhost:3000/api/restaurants/filter-options"
```

**回應格式:**
```json
{
  "success": true,
  "options": {
    "cuisine_style": ["中式", "日式", "韓式", ...],
    "type": ["火鍋", "燒肉", "酒吧", ...],
    "budget": ["200-400", "500-800", "1000-1500", "2000以上"]
  }
}
```

### 3. 獲取所有餐廳
**GET** `/api/restaurants/all`

獲取資料庫中所有餐廳（用於測試或管理）。

**範例請求:**
```bash
curl "http://localhost:3000/api/restaurants/all"
```

## 資料庫

餐廳資料庫位於專案根目錄的 `restaurants_database.json`。

**餐廳資料結構:**
```json
{
  "name": "餐廳名稱",
  "address": "餐廳地址",
  "cuisine_style": ["料理風格1", "料理風格2"],
  "type": ["餐廳類型1", "餐廳類型2"],
  "budget": "500-800",  // 或 null
  "url": "https://..."
}
```

## 目前支援的篩選條件

✅ **已實作:**
- 料理風格 (cuisine_style)
- 餐廳類型 (type)
- 預算 (budget)

⏳ **待實作:**
- 距離 (distance) - 需要餐廳座標資料
- 用餐時段 (time_slot) - 需要營業時間資料
- 線上訂位 (online_reservation) - 需要訂位資料

## 開發筆記

- 預算篩選：如果餐廳沒有預算資料 (`budget: null`)，會跳過預算篩選
- 多選篩選：料理風格和餐廳類型支援多選，只要符合其中一個條件即可
- 隨機排序：推薦結果會隨機排序，每次請求結果可能不同
