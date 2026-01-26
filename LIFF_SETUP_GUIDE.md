# LINE LIFF App 創建指南

## 步驟 1：登入 LINE Developers Console

1. 訪問：https://developers.line.biz/console/
2. 使用你的 LINE 帳號登入

## 步驟 2：選擇或創建 Provider

- 如果已有 Provider，直接選擇
- 如果沒有，點擊「**Create**」創建新的 Provider
  - **Provider name**: 例如「今天吃什麼」或你的品牌名稱

## 步驟 3：創建 LINE Login Channel

⚠️ **重要**：必須創建 **LINE Login Channel**，不是 Messaging API Channel！

1. 在 Provider 頁面，點擊「**Create**」
2. 選擇「**LINE Login**」
3. 填寫 Channel 資訊：
   - **Channel name**: `今天吃什麼`（或你想要的名稱）
   - **Channel description**: `餐廳推薦服務`（可選）
   - **App type**: 選擇「**Web app**」
   - **Email address**: 你的 Email（必填）
   - **Privacy policy URL**: （可選，如果有的話）
   - **Terms of service URL**: （可選，如果有的話）
4. 點擊「**Create**」創建

## 步驟 4：創建 LIFF App

創建 Login Channel 後，進入該 Channel：

1. 在左側選單找到「**LIFF**」
2. 點擊「**Add**」或「**Create**」按鈕
3. 填寫 LIFF App 資訊：

### LIFF App 設定詳解

#### 1. **LIFF app name**
```
今天吃什麼
```
- 這是顯示在 LINE 內的名稱
- 可以自由命名

#### 2. **Size**
選擇：**Full**（全螢幕）
- **Full**: 全螢幕顯示（推薦）
- **Tall**: 高型顯示
- **Compact**: 緊湊型顯示

#### 3. **Endpoint URL**
```
https://random-rice.netlify.app/liff
```
- **重要**：替換 `random-rice` 為你的 Netlify 網站名稱
- 格式：`https://你的網站名稱.netlify.app/liff`
- 如果還沒部署，可以先填寫，部署後再更新
- **必須是 HTTPS**（Netlify 自動提供）
- 這個 URL 會指向 LIFF App 的 `index.html`

#### 4. **Scope**（權限範圍）
勾選以下選項：

✅ **profile** - 獲取用戶基本資料
- 可以獲取用戶的顯示名稱、頭像
- 用於個人化體驗（目前代碼中已支持，但未強制使用）

❌ **openid** - OpenID Connect（可選）
- 如果需要更進階的身份驗證功能
- 目前不需要，可以暫時不勾選

#### 5. **Bot link feature**（Bot 連結功能）
選擇：**Don't add as friend**（不自動加好友）
- 這是工具型應用，不需要自動加好友
- 避免打擾用戶

#### 6. **Add friend option**
選擇：**Don't add as friend**（不自動加好友）
- 同上，不需要自動加好友

4. 點擊「**Add**」或「**Create**」完成創建

## 步驟 5：獲取 LIFF ID

創建完成後：

1. 在 LIFF 列表中會顯示你的 LIFF App
2. 點擊 LIFF App，可以看到詳細資訊
3. 複製 **LIFF ID**（格式類似：`1234567890-abcdefgh`）

## 步驟 6：配置 LIFF ID

有兩種方式設置 LIFF ID：

### 方式 1：在代碼中設置（推薦，正式環境）

編輯 `frontend/liff/app.js`：

找到這一行：
```javascript
const defaultLiffId = 'YOUR_LIFF_ID_HERE';
```

替換為：
```javascript
const defaultLiffId = '你的LIFF_ID';
```

### 方式 2：在 URL 參數中（測試用）

測試時可以在 URL 中添加：
```
https://random-rice.netlify.app/liff?liffId=你的LIFF_ID
```

## 步驟 7：部署到 Netlify

1. 確保代碼已推送到 GitHub
2. 在 Netlify 中：
   - 如果還沒部署，創建新站點並連接 GitHub
   - 如果已部署，觸發重新部署

3. 部署完成後，訪問：
   ```
   https://你的網站名稱.netlify.app/liff
   ```

## 步驟 8：測試 LIFF App

### 方式 1：在瀏覽器中測試（開發用）

訪問：
```
https://你的網站名稱.netlify.app/liff?liffId=你的LIFF_ID
```

### 方式 2：在 LINE 內測試（正式測試）

1. 在 LINE Developers Console 中，找到你的 LIFF App
2. 點擊「**Open LIFF app**」按鈕
3. 會在 LINE 內打開 LIFF App
4. 測試各項功能：
   - 表單填寫
   - 餐廳推薦
   - 分享功能（右上角按鈕）
   - 關閉功能（左上角按鈕）

## 重要提醒

### Endpoint URL 設定

根據你的 Netlify 部署情況：

**如果已部署到 Netlify：**
```
https://你的網站名稱.netlify.app/liff
```

**如果還沒部署：**
- 可以先填寫一個臨時 URL
- 部署後再更新 Endpoint URL

**更新 Endpoint URL：**
1. 在 LINE Developers Console 中找到你的 LIFF App
2. 點擊「**Edit**」
3. 更新 Endpoint URL
4. 保存

### 本地開發測試

如果需要本地測試，可以使用：
```
http://localhost:3000/liff?liffId=你的LIFF_ID
```

但注意：
- 本地測試時，某些 LINE 功能可能無法使用
- 正式環境必須使用 HTTPS

## 常見問題

### Q: 創建 LIFF App 時找不到「LIFF」選項？
A: 確保你創建的是 **LINE Login Channel**，不是 Messaging API Channel。

### Q: Endpoint URL 應該填什麼？
A: 填寫你的 Netlify 部署地址 + `/liff`，例如：
```
https://random-rice.netlify.app/liff
```

### Q: 可以有多個 LIFF App 嗎？
A: 可以，一個 Login Channel 可以創建多個 LIFF App，每個對應不同的功能或頁面。

### Q: LIFF ID 在哪裡找到？
A: 創建 LIFF App 後，在 LIFF 列表中點擊你的 App，可以看到 LIFF ID。

### Q: 如何更新 LIFF App 設定？
A: 在 LINE Developers Console 中找到你的 LIFF App，點擊「Edit」即可修改。

## 下一步

創建完成後：
1. 複製 LIFF ID
2. 更新 `frontend/liff/app.js` 中的 LIFF ID
3. 推送到 GitHub
4. 在 Netlify 部署
5. 在 LINE 內測試

## Rich Menu 配置（可選）

如果你有官方帳號，可以在 Rich Menu 中設置按鈕連結到：

```
https://你的網站名稱.netlify.app/liff?page=home
```

這樣用戶點擊 Rich Menu 按鈕就會打開 LIFF App。
