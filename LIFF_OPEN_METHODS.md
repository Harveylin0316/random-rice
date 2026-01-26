# 如何打開 LIFF App - 多種方法

## 方法 1：通過 Deep Link（最簡單）

### 步驟：

1. **在 LINE Desktop 或手機 LINE 中**，發送以下連結給自己或好友：
   ```
   https://liff.line.me/2008944358-649rLhGj
   ```

2. **點擊連結**，就會在 LINE 內打開 LIFF App

### 快速測試：
- 複製連結：`https://liff.line.me/2008944358-649rLhGj`
- 在 LINE Desktop 的聊天中發送給自己
- 點擊連結即可打開

---

## 方法 2：在 LINE Developers Console 中查找

### 步驟：

1. 登入 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇你的 **Provider**
3. 選擇你的 **LINE Login Channel**
4. 在左側選單點擊「**LIFF**」
5. 找到你的 LIFF App（名稱：今天吃什麼）
6. **點擊 LIFF App 的名稱**（不是按鈕，是名稱本身）
7. 在詳細頁面中，應該會看到：
   - LIFF ID
   - Endpoint URL
   - 可能會有「**Open**」或「**開啟**」連結

**注意**：不同版本的 Console 界面可能不同，可能沒有「Open LIFF app」按鈕，但可以通過 Deep Link 打開。

---

## 方法 3：通過 QR Code

### 步驟：

1. **生成 QR Code**：
   - 使用任何 QR Code 生成器
   - 內容填入：`https://liff.line.me/2008944358-649rLhGj`
   - 生成 QR Code

2. **掃描 QR Code**：
   - 在 LINE 內使用「掃描」功能
   - 或使用手機相機掃描
   - 會自動打開 LIFF App

---

## 方法 4：在聊天中發送連結

### 步驟：

1. **在 LINE Desktop 或手機 LINE 中**
2. **打開與自己的聊天**（或任何聊天）
3. **發送連結**：
   ```
   https://liff.line.me/2008944358-649rLhGj
   ```
4. **點擊連結**，就會打開 LIFF App

---

## 方法 5：通過官方帳號（如果有）

如果你有 LINE 官方帳號：

1. 在官方帳號中發送訊息給用戶
2. 訊息中包含連結：
   ```
   🍽️ 今天吃什麼？
   
   快來試試看！
   https://liff.line.me/2008944358-649rLhGj
   ```
3. 用戶點擊連結就會打開

---

## 推薦方法（最簡單）

### 現在就可以測試：

1. **打開 LINE Desktop**（如果還沒下載：https://desktop.line.me/）
2. **登入你的 LINE 帳號**
3. **打開與自己的聊天**（或任何聊天）
4. **發送以下訊息**：
   ```
   https://liff.line.me/2008944358-649rLhGj
   ```
5. **點擊連結**，就會在 LINE 內打開 LIFF App

---

## 你的 LIFF Deep Link

```
https://liff.line.me/2008944358-649rLhGj
```

**複製這個連結，在 LINE 內發送給自己，然後點擊即可打開！**

---

## 注意事項

- **必須在 LINE 內**：LIFF App 只能在 LINE 內打開
- **Deep Link 最可靠**：使用 `https://liff.line.me/你的LIFF_ID` 格式的連結最可靠
- **瀏覽器無法打開**：在一般瀏覽器中點擊 Deep Link 不會打開 LINE，需要在 LINE 內點擊

---

## 如果還是不行

1. **確認 LIFF App 已創建**：
   - 在 LINE Developers Console 中確認 LIFF App 存在
   - 確認 LIFF ID 正確：`2008944358-649rLhGj`

2. **確認 Channel 狀態**：
   - Developing 狀態也可以測試
   - 不需要改為 Public 才能測試

3. **嘗試其他方法**：
   - 使用 QR Code
   - 在手機 LINE 中測試
