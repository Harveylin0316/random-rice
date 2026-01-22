#!/bin/bash

# API 測試腳本

BASE_URL="http://localhost:3000"

echo "=========================================="
echo "測試餐廳推薦 API"
echo "=========================================="
echo ""

echo "1. 測試根路由..."
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""
echo ""

echo "2. 獲取篩選選項..."
curl -s "$BASE_URL/api/restaurants/filter-options" | python3 -m json.tool | head -20
echo ""
echo ""

echo "3. 隨機推薦 3 間餐廳（無篩選）..."
curl -s "$BASE_URL/api/restaurants/recommend?limit=3" | python3 -m json.tool | head -30
echo ""
echo ""

echo "4. 推薦日式燒肉餐廳..."
curl -G -s "$BASE_URL/api/restaurants/recommend" \
  --data-urlencode "cuisine_style=日式" \
  --data-urlencode "type=燒肉" \
  --data-urlencode "limit=3" | python3 -m json.tool | head -40
echo ""
echo ""

echo "5. 推薦火鍋餐廳（預算 500-800）..."
curl -G -s "$BASE_URL/api/restaurants/recommend" \
  --data-urlencode "type=火鍋" \
  --data-urlencode "budget=500-800" \
  --data-urlencode "limit=3" | python3 -m json.tool | head -40
echo ""
echo ""

echo "=========================================="
echo "測試完成！"
echo "=========================================="
