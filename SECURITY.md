# 🔒 安全性設定指南

## ⚠️ 重要安全提醒

**API Key 已從代碼中移除，改為使用環境變數。**

如果您之前已經推送到 GitHub，**請立即在 Google Cloud Console 中撤銷舊的 API Key 並重新生成新的 Key**。

## 設定步驟

### 1. 安裝 python-dotenv

```bash
pip install python-dotenv
```

### 2. 創建 .env 文件

在專案根目錄創建 `.env` 文件：

```bash
cp .env.example .env
```

### 3. 填入您的 API Key

編輯 `.env` 文件：

```
GOOGLE_API_KEY=your_actual_api_key_here
```

### 4. 確保 .env 不被提交

`.env` 文件已經在 `.gitignore` 中，不會被提交到 Git。

## 已修復的文件

以下文件已改為使用環境變數：
- `add_coordinates_by_place_id.py`
- `add_coordinates_google.py`
- `fetch_restaurant_data.py`
- `test_api.py`
- `update_null_budgets.py`

## 如果 API Key 已暴露

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 選擇您的專案
3. 進入 "APIs & Services" > "Credentials"
4. 找到暴露的 API Key
5. 點擊 "Restrict key" 或 "Delete" 來限制或刪除
6. 創建新的 API Key
7. 更新 `.env` 文件中的新 Key

## 最佳實踐

- ✅ 永遠不要將 API Key 硬編碼在代碼中
- ✅ 使用環境變數或配置文件（並加入 .gitignore）
- ✅ 定期輪換 API Key
- ✅ 在 Google Cloud Console 中設定 API Key 限制（IP、HTTP referrer 等）
