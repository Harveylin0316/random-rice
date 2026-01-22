#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
為無預算資料的餐廳重新查詢 Google Places API，補充預算資訊
"""

import csv
import json
import requests
import time
from typing import Dict, List, Optional

# Google Places API (New) 配置
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
    "X-Goog-FieldMask": "id,displayName,formattedAddress,types,priceLevel"
}

# 價格等級換算為台幣區間
PRICE_LEVEL_TO_RANGE = {
    "PRICE_LEVEL_FREE": "0-100",
    "PRICE_LEVEL_INEXPENSIVE": "200-400",
    "PRICE_LEVEL_MODERATE": "500-800",
    "PRICE_LEVEL_EXPENSIVE": "1000-1500",
    "PRICE_LEVEL_VERY_EXPENSIVE": "2000以上",
}

def get_restaurant_price_level(place_id: str) -> Optional[str]:
    """使用 place_id 呼叫 Google Places API (New) 獲取價格等級"""
    url = API_URL.format(place_id=place_id)
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price_level = data.get('priceLevel')
            return price_level
        elif response.status_code == 429:
            print(f"  API 速率限制，等待 2 秒...")
            time.sleep(2)
            return get_restaurant_price_level(place_id)  # 重試
        else:
            print(f"  錯誤 {response.status_code} 對於 place_id {place_id}")
            return None
    except Exception as e:
        print(f"  請求錯誤對於 place_id {place_id}: {str(e)}")
        return None

def convert_price_level_to_range(price_level: Optional[str]) -> Optional[str]:
    """將價格等級轉換為預算區間"""
    if price_level is None:
        return None
    return PRICE_LEVEL_TO_RANGE.get(price_level)

def match_restaurants_with_place_ids(json_file: str, csv_file: str) -> Dict:
    """匹配 JSON 中的餐廳與 CSV 中的 place_id"""
    
    # 讀取 JSON 資料
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data.get('restaurants', [])
    
    # 讀取 CSV 建立對照表（使用 URL 作為匹配鍵，因為最可靠）
    csv_restaurants = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('URL', '').strip()
            place_id = row.get('place_id', '').strip()
            name = row.get('餐廳名稱', '').strip()
            if url and place_id:
                csv_restaurants[url] = {
                    'place_id': place_id,
                    'name': name,
                    'url': url
                }
    
    # 建立匹配對照表
    matched = {}
    unmatched = []
    
    for restaurant in restaurants:
        url = restaurant.get('url', '').strip()
        if url in csv_restaurants:
            matched[url] = {
                'restaurant': restaurant,
                'place_id': csv_restaurants[url]['place_id']
            }
        else:
            unmatched.append(restaurant)
    
    print(f"總餐廳數：{len(restaurants)}")
    print(f"成功匹配 place_id：{len(matched)}")
    print(f"無法匹配 place_id：{len(unmatched)}")
    
    return matched, unmatched

def update_null_budgets(json_file: str, csv_file: str):
    """為無預算資料的餐廳查詢並更新預算"""
    
    # 匹配餐廳與 place_id
    matched, unmatched = match_restaurants_with_place_ids(json_file, csv_file)
    
    # 找出無預算的餐廳
    no_budget_matched = {}
    for url, info in matched.items():
        restaurant = info['restaurant']
        if restaurant.get('budget') is None:
            no_budget_matched[url] = info
    
    print(f"\n無預算資料且可匹配的餐廳：{len(no_budget_matched)}")
    
    if len(no_budget_matched) == 0:
        print("沒有需要更新的餐廳！")
        return
    
    # 讀取完整資料以便更新
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data.get('restaurants', [])
    
    # 建立 URL 到索引的對照表
    url_to_index = {r.get('url', '').strip(): idx for idx, r in enumerate(restaurants)}
    
    # 查詢並更新預算
    updated_count = 0
    still_null_count = 0
    
    total = len(no_budget_matched)
    print(f"\n開始查詢 {total} 間餐廳的預算資料...")
    print("=" * 60)
    
    for idx, (url, info) in enumerate(no_budget_matched.items(), 1):
        place_id = info['place_id']
        restaurant = info['restaurant']
        name = restaurant.get('name', 'Unknown')
        
        print(f"[{idx}/{total}] {name}")
        print(f"  Place ID: {place_id}")
        
        # 查詢價格等級
        price_level = get_restaurant_price_level(place_id)
        
        if price_level:
            budget_range = convert_price_level_to_range(price_level)
            if budget_range:
                # 更新資料
                restaurant_idx = url_to_index[url]
                restaurants[restaurant_idx]['budget'] = budget_range
                print(f"  ✓ 更新預算：{budget_range} 元")
                updated_count += 1
            else:
                print(f"  ✗ 無法轉換價格等級：{price_level}")
                still_null_count += 1
        else:
            print(f"  ✗ API 無價格等級資料")
            still_null_count += 1
        
        # 避免 API 速率限制（每次請求間隔 0.2 秒）
        if idx < total:
            time.sleep(0.2)
        
        # 每處理 50 間餐廳保存一次
        if idx % 50 == 0:
            print(f"\n已處理 {idx} 間，暫時保存...")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({"restaurants": restaurants}, f, ensure_ascii=False, indent=2)
    
    # 最終保存
    print(f"\n處理完成！")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({"restaurants": restaurants}, f, ensure_ascii=False, indent=2)
    
    print(f"\n更新統計：")
    print(f"  成功更新預算：{updated_count} 間")
    print(f"  仍無預算資料：{still_null_count} 間")
    print(f"\n資料已保存到：{json_file}")
    
    # 最終統計
    final_no_budget = sum(1 for r in restaurants if r.get('budget') is None)
    final_with_budget = len(restaurants) - final_no_budget
    
    print(f"\n最終統計：")
    print(f"  有預算資料：{final_with_budget} 間 ({final_with_budget/len(restaurants)*100:.1f}%)")
    print(f"  無預算資料：{final_no_budget} 間 ({final_no_budget/len(restaurants)*100:.1f}%)")

if __name__ == "__main__":
    json_file = "restaurants_database.json"
    csv_file = "已簽約餐廳.csv"
    
    print("開始為無預算資料的餐廳查詢預算...")
    print("=" * 60)
    
    update_null_budgets(json_file, csv_file)
