# 如何在 LINE 內打開 LIFF App

## 方法 1：通過 LINE Developers Console（最簡單）

### 步驟：
1. 登入 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇你的 Provider
3. 選擇你的 **LINE Login Channel**
4. 在左側選單點擊「**LIFF**」
5. 找到你的 LIFF App（名稱：今天吃什麼）
6. 點擊「**Open LIFF app**」按鈕（或「**開啟 LIFF app**」）
7. 會在 LINE 內打開你的 LIFF App

**優點**：最簡單，適合開發和測試

---

## 方法 2：通過 Rich Menu（需要官方帳號）

如果你有 LINE 官方帳號，可以在 Rich Menu 中設置按鈕連結到 LIFF App。

### 步驟：
1. 在 LINE Developers Console 中，選擇你的 **Messaging API Channel**（官方帳號）
2. 設置 Rich Menu，添加按鈕
3. 按鈕的 URI 設置為：
   ```
   https://liff.line.me/你的LIFF_ID
   ```
   或
   ```
   https://你的網站名稱.netlify.app/liff
   ```
4. 用戶點擊 Rich Menu 按鈕就會打開 LIFF App

**優點**：用戶體驗最好，適合正式發布

---

## 方法 3：通過深層連結（Deep Link）

### LIFF Deep Link 格式：
```
https://liff.line.me/你的LIFF_ID
```

例如：
```
https://liff.line.me/2008944358-649rLhGj
```

### 使用方式：
1. **在聊天中發送連結**：
   - 將連結發送給自己或好友
   - 點擊連結就會在 LINE 內打開 LIFF App

2. **在網頁中嵌入連結**：
   - 在網頁中添加連結
   - 用戶點擊後會在 LINE 內打開（如果用戶在 LINE 內瀏覽）

3. **QR Code**：
   - 生成 QR Code，掃描後打開連結
   - 會在 LINE 內打開 LIFF App

---

## 方法 4：通過官方帳號發送訊息

如果你有官方帳號，可以通過 Messaging API 發送包含 LIFF 連結的訊息。

### 步驟：
1. 在官方帳號中發送訊息給用戶
2. 訊息中包含 LIFF 連結：
   ```
   今天吃什麼？快來試試看！
   https://liff.line.me/2008944358-649rLhGj
   ```
3. 用戶點擊連結就會打開 LIFF App

---

## 方法 5：通過網頁連結（如果用戶在 LINE 內瀏覽）

如果你的網站有連結到 LIFF App，用戶在 LINE 內瀏覽時點擊連結也會打開 LIFF App。

### 範例：
```html
<a href="https://liff.line.me/2008944358-649rLhGj">打開「今天吃什麼」</a>
```

---

## 推薦測試流程

### 開發階段：
1. 使用 **方法 1**（LINE Developers Console）快速測試
2. 確認功能正常

### 正式發布：
1. 設置 **Rich Menu**（方法 2）
2. 或通過 **官方帳號發送連結**（方法 4）
3. 用戶點擊後打開 LIFF App

---

## 你的 LIFF ID

```
2008944358-649rLhGj
```

### Deep Link：
```
https://liff.line.me/2008944358-649rLhGj
```

### 網站連結：
```
https://你的網站名稱.netlify.app/liff
```

---

## 注意事項

1. **必須在 LINE 內**：LIFF App 只能在 LINE 內打開
2. **Deep Link 優先**：使用 `https://liff.line.me/你的LIFF_ID` 格式的連結最可靠
3. **測試建議**：開發階段使用 LINE Developers Console 的「Open LIFF app」按鈕最方便

---

## 快速測試

**現在就可以測試**：
1. 打開 [LINE Developers Console](https://developers.line.biz/console/)
2. 找到你的 LIFF App
3. 點擊「**Open LIFF app**」
4. 在 LINE 內打開並測試功能
