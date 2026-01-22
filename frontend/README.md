# 今天吃什麼 - 前端頁面

## 檔案結構

```
frontend/
├── index.html    # 主頁面
├── style.css     # 樣式表
└── app.js        # JavaScript 邏輯
```

## 功能特色

✅ **現代化 UI 設計**
- 漸層背景
- 卡片式設計
- 響應式布局
- 流暢動畫效果

✅ **完整的篩選功能**
- 料理風格（多選）
- 餐廳類型（多選）
- 預算區間（單選）
- 距離、用餐時段、線上訂位（預留，待實作）

✅ **使用者體驗**
- 載入動畫
- 錯誤處理
- 結果展示卡片
- 一鍵重置

## 使用方式

### 方式 1: 使用後端伺服器（推薦）

後端伺服器已配置為同時提供前端頁面和 API：

```bash
cd backend
npm start
```

然後在瀏覽器打開：`http://localhost:3000`

### 方式 2: 使用簡單 HTTP 伺服器

如果後端未運行，可以使用 Python 簡單伺服器：

```bash
cd frontend
python3 -m http.server 8080
```

然後在瀏覽器打開：`http://localhost:8080`

**注意**: 使用此方式需要修改 `app.js` 中的 `API_BASE_URL` 為後端 API 地址。

## API 連接

前端預設連接到：`http://localhost:3000/api`

如需修改，請編輯 `app.js` 中的 `API_BASE_URL` 變數。

## 瀏覽器支援

- Chrome/Edge (最新版本)
- Firefox (最新版本)
- Safari (最新版本)

## 待實作功能

- [ ] 距離篩選（需要餐廳座標資料）
- [ ] 用餐時段篩選（需要營業時間資料）
- [ ] 線上訂位篩選（需要訂位資料）
- [ ] 使用者位置定位（Geolocation API）
