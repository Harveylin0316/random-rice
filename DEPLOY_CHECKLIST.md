# Netlify 部署檢查清單

## ✅ 部署前檢查

### 1. 文件結構
- [x] `netlify.toml` - Netlify 配置文件
- [x] `netlify/functions/restaurants.js` - Netlify Function
- [x] `frontend/` - 前端文件目錄
- [x] `restaurants_database.json` - 餐廳資料庫（必須在根目錄）

### 2. 代碼更新
- [x] 前端 `app.js` 已更新 API_BASE_URL 為自動檢測環境
- [x] Netlify Function 已創建並配置路由
- [x] CORS headers 已配置

### 3. GitHub 提交
- [ ] 確認所有更改已提交到 GitHub
- [ ] 確認 `restaurants_database.json` 已提交（文件大小可能較大）

## 🚀 部署步驟

### 步驟 1: 在 Netlify 上連接 GitHub

1. 登入 [Netlify](https://app.netlify.com/)
2. 點擊「Add new site」→「Import an existing project」
3. 選擇「GitHub」並授權
4. 選擇 `random-rice` 專案

### 步驟 2: 構建設置（通常自動讀取 netlify.toml）

Netlify 會自動讀取 `netlify.toml`，但你可以檢查：

- **Base directory**: （留空）
- **Build command**: （留空）
- **Publish directory**: `frontend`

### 步驟 3: 部署

1. 點擊「Deploy site」
2. 等待構建完成（通常 1-2 分鐘）
3. 檢查構建日誌是否有錯誤

### 步驟 4: 驗證部署

訪問你的 Netlify URL（例如：`https://your-site.netlify.app`），測試：

- [ ] 前端頁面正常載入
- [ ] 獲取位置功能（需要 HTTPS 或 localhost）
- [ ] 篩選選項正常載入（`/api/restaurants/filter-options`）
- [ ] 地區選項正常載入（`/api/restaurants/location-options`）
- [ ] 推薦餐廳功能正常（`/api/restaurants/recommend`）
- [ ] 餐廳照片正常顯示
- [ ] 訂位和導航按鈕正常

## 🐛 常見問題排查

### 問題 1: Functions 找不到資料庫文件

**錯誤訊息**: `Cannot find module` 或 `ENOENT: no such file or directory`

**解決方案**:
1. 確認 `restaurants_database.json` 在專案根目錄
2. 確認文件已提交到 GitHub
3. 檢查 Netlify 構建日誌，確認文件被包含在部署中

### 問題 2: API 請求返回 404

**錯誤訊息**: `404 Not Found` 或 `Failed to fetch`

**解決方案**:
1. 檢查 `netlify.toml` 中的重定向規則
2. 確認 `netlify/functions/restaurants.js` 存在
3. 檢查 Netlify Functions 日誌

### 問題 3: CORS 錯誤

**錯誤訊息**: `Access-Control-Allow-Origin` 相關錯誤

**解決方案**:
- 確認 `netlify/functions/restaurants.js` 中已設置 CORS headers
- 檢查瀏覽器控制台是否有詳細錯誤訊息

### 問題 4: 地理位置功能不工作

**原因**: 地理位置 API 需要 HTTPS 環境

**解決方案**:
- Netlify 自動提供 HTTPS，所以應該可以正常工作
- 如果仍有問題，檢查瀏覽器權限設置

## 📝 部署後檢查

部署完成後，請檢查：

1. **網站 URL**: 確認可以訪問
2. **Functions 日誌**: 在 Netlify Dashboard → Functions 查看日誌
3. **構建日誌**: 確認沒有錯誤或警告
4. **功能測試**: 完整測試所有功能

## 🔗 相關文件

- `NETLIFY_DEPLOY.md` - 詳細部署指南
- `netlify.toml` - Netlify 配置文件
- `netlify/functions/restaurants.js` - API Function
