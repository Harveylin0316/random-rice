# 餐廳資料更新指南

## 當前狀態

- **無預算餐廳**：450 間（正在處理中）
- **無照片餐廳**：883 間

## 更新預算

### 批量處理腳本
```bash
# 處理前 50 間無預算餐廳
python3 update_budgets_batch.py --batch-size 50 --start 0

# 繼續處理下一批（從第 50 間開始）
python3 update_budgets_batch.py --batch-size 50 --start 50

# 依此類推...
```

### 完整處理所有餐廳
由於有 450 間餐廳需要處理，建議分批執行：

```bash
# 批次 1: 0-50
python3 update_budgets_batch.py --batch-size 50 --start 0

# 批次 2: 50-100
python3 update_budgets_batch.py --batch-size 50 --start 50

# 批次 3: 100-150
python3 update_budgets_batch.py --batch-size 50 --start 100

# ... 繼續到 450
python3 update_budgets_batch.py --batch-size 50 --start 400
```

## 更新照片

### 批量處理腳本
```bash
# 處理前 50 間無照片餐廳
python3 update_images_batch.py --batch-size 50 --start 0

# 繼續處理下一批
python3 update_images_batch.py --batch-size 50 --start 50
```

### 完整處理所有餐廳
由於有 883 間餐廳需要處理，建議分批執行：

```bash
# 批次 1: 0-50
python3 update_images_batch.py --batch-size 50 --start 0

# 批次 2: 50-100
python3 update_images_batch.py --batch-size 50 --start 50

# ... 繼續到 883
python3 update_images_batch.py --batch-size 50 --start 850
```

## 同時更新預算和照片

使用綜合腳本（較慢，但一次完成）：

```bash
# 測試模式（只處理前 10 間）
python3 update_all_budgets_and_images.py --test --limit 10

# 只更新預算
python3 update_all_budgets_and_images.py --budget-only

# 只更新照片
python3 update_all_budgets_and_images.py --images-only
```

## 注意事項

1. **請求頻率**：腳本已設定延遲（0.8秒），避免請求過快被封鎖
2. **自動保存**：每處理 10 間餐廳會自動保存，防止數據丟失
3. **進度追蹤**：每次處理完成後會顯示進度和下一批次的命令
4. **錯誤處理**：如果某間餐廳爬取失敗，會跳過並繼續處理下一間

## 檢查進度

```bash
# 檢查當前狀態
python3 -c "import json; data = json.load(open('restaurants_database.json', 'r', encoding='utf-8')); no_budget = sum(1 for r in data['restaurants'] if not r.get('budget')); no_images = sum(1 for r in data['restaurants'] if not r.get('images') or len(r.get('images', [])) == 0); print(f'無預算：{no_budget} 間'); print(f'無照片：{no_images} 間')"
```
