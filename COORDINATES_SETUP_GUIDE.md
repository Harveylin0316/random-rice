# 餐廳座標資料獲取指南

## 📋 使用 Google Geocoding API 獲取座標

### 步驟 1：啟用 Geocoding API

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 選擇你的專案（或建立新專案）
3. 啟用 **Geocoding API**：
   - 在左側選單選擇「API 和服務」→「程式庫」
   - 搜尋「Geocoding API」
   - 點擊「啟用」

### 步驟 2：確認 API Key 權限

1. 前往「API 和服務」→「憑證」
2. 找到你的 API Key
3. 確認：
   - API Key 沒有 IP 限制（或已加入你的 IP）
   - API Key 允許使用 Geocoding API
   - API Key 沒有使用限制

### 步驟 3：執行座標獲取腳本

#### 測試模式（推薦先執行）
```bash
python3 add_coordinates_google.py --test
```

這會處理前 10 間餐廳，確認 API 正常運作。

#### 完整處理
```bash
python3 add_coordinates_google.py
```

這會處理所有餐廳（約 888 間）。

---

## ⚠️ 常見問題

### 問題 1：REQUEST_DENIED 錯誤

**原因**：Geocoding API 未啟用或 API Key 權限不足

**解決方法**：
1. 確認 Geocoding API 已啟用
2. 檢查 API Key 權限設定
3. 確認 API Key 沒有 IP 限制

### 問題 2：OVER_QUERY_LIMIT 錯誤

**原因**：API 配額已用完

**解決方法**：
1. 檢查 Google Cloud Console 中的配額使用情況
2. 等待配額重置（每月重置）
3. 或升級到付費方案

### 問題 3：ZERO_RESULTS 錯誤

**原因**：地址無法找到

**解決方法**：
1. 檢查地址格式是否正確
2. 嘗試簡化地址（移除樓層、室號等）
3. 手動補充座標

---

## 📊 費用說明

### Google Geocoding API 定價

- **免費額度**：每月 $200（約 40,000 次請求）
- **超出後**：每 1,000 次請求 $5

### 本次處理費用估算

- **餐廳總數**：888 間
- **API 請求數**：約 888 次
- **費用**：$0（完全在免費額度內）

---

## ✅ 驗證座標資料

處理完成後，可以檢查資料庫：

```python
import json

with open('restaurants_database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 統計有座標的餐廳
has_coords = sum(1 for r in data['restaurants'] if 'coordinates' in r and r['coordinates'])
print(f"有座標的餐廳：{has_coords} 間")
print(f"總餐廳數：{len(data['restaurants'])} 間")

# 檢查範例
for restaurant in data['restaurants'][:3]:
    if 'coordinates' in restaurant:
        print(f"{restaurant['name']}: {restaurant['coordinates']}")
```

---

## 🚀 下一步

座標資料獲取完成後，就可以實作距離功能了！
