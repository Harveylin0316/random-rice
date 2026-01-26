# 在電腦上測試 LIFF App

## 方法 1：使用 LINE Desktop（推薦）

### Windows / Mac 版 LINE

1. **下載並安裝 LINE Desktop**：
   - Windows: https://desktop.line.me/
   - Mac: https://desktop.line.me/

2. **登入你的 LINE 帳號**

3. **打開 LIFF App**：
   - 方法 A：在 LINE Developers Console 點擊「Open LIFF app」
   - 方法 B：在 LINE Desktop 中發送 Deep Link 給自己：
     ```
     https://liff.line.me/2008944358-649rLhGj
     ```
   - 方法 C：在聊天中點擊連結

4. **測試功能**：
   - LIFF App 會在 LINE Desktop 內打開
   - 可以測試所有功能

**優點**：功能完整，最接近手機體驗

---

## 方法 2：直接在瀏覽器中訪問（開發測試）

### 注意事項：
- 某些 LINE 特定功能可能無法使用（如分享、關閉按鈕）
- 但基本功能（餐廳推薦）可以正常測試

### 步驟：

1. **直接訪問你的網站**：
   ```
   https://你的網站名稱.netlify.app/liff
   ```

2. **或使用本地開發服務器**：
   ```bash
   # 啟動後端服務器
   cd backend
   npm start
   
   # 在瀏覽器中打開
   http://localhost:3000/liff
   ```

3. **測試功能**：
   - 表單填寫
   - 餐廳推薦
   - 基本 UI/UX

**優點**：快速測試，不需要 LINE

**缺點**：某些 LINE 特定功能無法測試

---

## 方法 3：使用瀏覽器開發者工具模擬移動設備

### 步驟：

1. **在瀏覽器中打開**：
   ```
   https://你的網站名稱.netlify.app/liff
   ```

2. **開啟開發者工具**：
   - Chrome/Edge: `F12` 或 `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Firefox: `F12` 或 `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)

3. **切換到移動設備模式**：
   - 點擊工具欄中的設備圖標（手機/平板圖標）
   - 或按 `Ctrl+Shift+M` (Windows) / `Cmd+Shift+M` (Mac)

4. **選擇設備**：
   - iPhone
   - Android
   - 或自定義尺寸

5. **測試功能**：
   - 模擬移動設備體驗
   - 測試響應式設計

**優點**：可以測試移動端 UI，不需要實際設備

---

## 推薦測試流程

### 開發階段（快速測試）：
1. **使用瀏覽器直接訪問**（方法 2）
   - 測試基本功能
   - 檢查 UI/UX
   - 確認表單和推薦功能

2. **使用瀏覽器開發者工具**（方法 3）
   - 測試移動端響應式設計
   - 檢查觸摸交互

### 完整測試階段：
1. **使用 LINE Desktop**（方法 1）
   - 測試 LINE 特定功能
   - 測試分享、關閉按鈕
   - 確認完整體驗

### 最終測試：
1. **在手機上測試**
   - 確認實際使用體驗
   - 測試地理位置功能

---

## 你的測試連結

### Deep Link（LINE Desktop）：
```
https://liff.line.me/2008944358-649rLhGj
```

### 網站連結（瀏覽器）：
```
https://你的網站名稱.netlify.app/liff
```

### 本地開發（瀏覽器）：
```
http://localhost:3000/liff
```

---

## 功能對比

| 功能 | 瀏覽器直接訪問 | LINE Desktop | 手機 LINE |
|------|---------------|--------------|-----------|
| 基本功能（餐廳推薦） | ✅ | ✅ | ✅ |
| UI/UX | ✅ | ✅ | ✅ |
| 分享按鈕 | ❌ | ✅ | ✅ |
| 關閉按鈕 | ❌ | ✅ | ✅ |
| 地理位置 | ✅ | ✅ | ✅ |
| LINE 用戶資料 | ❌ | ✅ | ✅ |

---

## 快速開始

### 現在就可以測試：

**方法 1（推薦）：LINE Desktop**
1. 下載 LINE Desktop
2. 登入
3. 在 LINE Developers Console 點擊「Open LIFF app」

**方法 2（快速）：瀏覽器**
1. 直接訪問：`https://你的網站名稱.netlify.app/liff`
2. 測試基本功能

---

## 注意事項

- **瀏覽器測試**：某些 LINE 特定功能會顯示警告或無法使用，這是正常的
- **LINE Desktop**：功能最完整，最接近手機體驗
- **開發階段**：可以先用瀏覽器快速測試，再用 LINE Desktop 完整測試
