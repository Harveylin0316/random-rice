#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Google Places API (New) 是否正常工作
"""

import csv
import json
import requests
import time

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    raise ValueError("請設定環境變數 GOOGLE_API_KEY，或在 .env 文件中配置")

API_URL = "https://places.googleapis.com/v1/places/{place_id}"
HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "id,displayName,formattedAddress,types,priceLevel,rating,userRatingCount"
}

# 讀取第一間餐廳測試
with open("已簽約餐廳.csv", 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    first_row = next(reader)
    
place_id = first_row.get('place_id', '').strip()
restaurant_name = first_row.get('餐廳名稱', '').strip()

print(f"測試餐廳：{restaurant_name}")
print(f"Place ID: {place_id}")
print(f"\n呼叫 API...")

url = API_URL.format(place_id=place_id)
response = requests.get(url, headers=HEADERS, timeout=10)

print(f"狀態碼：{response.status_code}")
print(f"回應：")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
