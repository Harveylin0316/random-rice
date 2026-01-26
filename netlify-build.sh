#!/bin/bash
# Netlify 構建腳本
# 將數據庫文件複製到函數目錄，並確保共享模組被複製到 web 目錄

echo "開始 Netlify 構建..."

# 檢查數據庫文件是否存在
if [ -f "restaurants_database.json" ]; then
  echo "找到數據庫文件，複製到函數目錄..."
  cp restaurants_database.json netlify/functions/restaurants_database.json
  if [ $? -eq 0 ]; then
    echo "✅ 數據庫文件複製成功"
    ls -lh netlify/functions/restaurants_database.json
  else
    echo "❌ 數據庫文件複製失敗"
    exit 1
  fi
else
  echo "❌ 找不到數據庫文件 restaurants_database.json"
  exit 1
fi

# 確保共享模組被複製到 web 目錄
if [ -d "frontend/shared" ]; then
  echo "複製共享模組到 web 目錄..."
  cp -r frontend/shared frontend/web/shared
  if [ $? -eq 0 ]; then
    echo "✅ Web 共享模組複製成功"
  else
    echo "❌ Web 共享模組複製失敗"
    exit 1
  fi
fi

# 確保共享模組被複製到 liff 目錄
if [ -d "frontend/shared" ]; then
  echo "複製共享模組到 liff 目錄..."
  cp -r frontend/shared frontend/liff/shared
  if [ $? -eq 0 ]; then
    echo "✅ LIFF 共享模組複製成功"
  else
    echo "❌ LIFF 共享模組複製失敗"
    exit 1
  fi
fi

echo "構建完成"
