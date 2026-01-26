# LIFF App 下一步指南

## ✅ 已完成

- [x] 創建 LIFF App
- [x] 配置 LIFF ID
- [x] 代碼部署到 Netlify
- [x] 瀏覽器測試基本功能正常

## 📋 接下來的步驟

### 1. 在 LINE 內完整測試（重要）

#### 方法 A：使用 LINE Desktop（推薦）

1. **下載 LINE Desktop**：
   - Windows: https://desktop.line.me/
   - Mac: https://desktop.line.me/

2. **登入你的 LINE 帳號**

3. **打開 LIFF App**：
   - 在 [LINE Developers Console](https://developers.line.biz/console/) 找到你的 LIFF App
   - 點擊「**Open LIFF app**」按鈕
   - 會在 LINE Desktop 內打開

4. **測試所有功能**：
   - ✅ 表單填寫
   - ✅ 餐廳推薦
   - ✅ 分享按鈕（右上角）
   - ✅ 關閉按鈕（左上角）
   - ✅ 地理位置功能
   - ✅ 所有 UI/UX

#### 方法 B：使用手機 LINE

1. 在手機上打開 LINE
2. 發送 Deep Link 給自己：
   ```
   https://liff.line.me/2008944358-649rLhGj
   ```
3. 點擊連結打開 LIFF App
4. 測試所有功能

---

### 2. 確認功能正常後，改為 Public

當所有功能測試通過後：

1. 登入 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇你的 **LINE Login Channel**
3. 點擊「**Settings**」或「**設定**」
4. 找到「**Channel status**」或「**頻道狀態**」
5. 點擊「**Change to public**」或「**改為公開**」
6. 確認變更

**注意**：改為 Public 後，所有 LINE 用戶都可以使用你的 LIFF App。

---

### 3. 設置 Rich Menu（可選，如果有官方帳號）

如果你有 LINE 官方帳號，可以在 Rich Menu 中設置按鈕：

1. 在 LINE Developers Console 中，選擇你的 **Messaging API Channel**（官方帳號）
2. 設置 Rich Menu，添加按鈕
3. 按鈕的 URI 設置為：
   ```
   https://liff.line.me/2008944358-649rLhGj
   ```
   或
   ```
   https://random-rice.netlify.app/liff
   ```
4. 用戶點擊 Rich Menu 按鈕就會打開 LIFF App

---

### 4. 分享給用戶

#### 方式 A：通過官方帳號發送連結

如果你有官方帳號，可以發送訊息給用戶：
```
🍽️ 今天吃什麼？

告訴我你的喜好，我來推薦餐廳給你！

👉 https://liff.line.me/2008944358-649rLhGj
```

#### 方式 B：生成 QR Code

1. 生成包含 Deep Link 的 QR Code：
   ```
   https://liff.line.me/2008944358-649rLhGj
   ```
2. 用戶掃描 QR Code 就會打開 LIFF App

#### 方式 C：在網站上添加連結

在你的網站上添加連結：
```html
<a href="https://liff.line.me/2008944358-649rLhGj">打開「今天吃什麼」</a>
```

---

## 🎯 測試檢查清單

### 基本功能
- [ ] 表單可以正常填寫
- [ ] 料理風格選擇正常
- [ ] 餐廳類型選擇正常
- [ ] 預算選擇正常
- [ ] 地區選擇正常
- [ ] 地理位置功能正常（如果使用）

### 推薦功能
- [ ] 點擊「推薦我」後有結果顯示
- [ ] 餐廳卡片正常顯示
- [ ] 餐廳圖片輪播正常
- [ ] 「換一批」按鈕正常
- [ ] 訂位連結正常
- [ ] 導航連結正常

### LINE 特定功能（需要在 LINE 內測試）
- [ ] 分享按鈕可以點擊
- [ ] 關閉按鈕可以點擊
- [ ] 外部連結正常打開

### UI/UX
- [ ] 移動端顯示正常
- [ ] 桌面端顯示正常
- [ ] 所有按鈕和互動正常

---

## 📝 你的 LIFF 資訊

- **LIFF ID**: `2008944358-649rLhGj`
- **Deep Link**: `https://liff.line.me/2008944358-649rLhGj`
- **網站連結**: `https://random-rice.netlify.app/liff`
- **Netlify 網站**: `random-rice.netlify.app`

---

## 🚀 正式發布前的最後檢查

1. ✅ 所有功能測試通過
2. ✅ 在 LINE Desktop 和手機上都測試過
3. ✅ UI/UX 沒有問題
4. ✅ 錯誤處理正常
5. ✅ 性能良好

完成後就可以正式發布了！

---

## 💡 未來擴展（可選）

當你準備好添加其他功能時：

1. **我的最愛**：`/liff?page=favorites`
2. **搜尋歷史**：`/liff?page=history`
3. **設定**：`/liff?page=settings`

只需在 `frontend/liff/pages/` 創建新文件，並在 `router.js` 中註冊即可。
