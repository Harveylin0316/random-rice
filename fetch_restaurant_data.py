#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Google Places API (New) 獲取餐廳詳細資訊
並整理成新的資料庫格式
"""

import csv
import json
import requests
import time
from typing import Dict, List, Optional, Set

# Google Places API (New) 配置
API_KEY = "AIzaSyCtMM-KM8Y-m7JiBZRFLpqsnvGnNcTd9fs"
API_URL = "https://places.googleapis.com/v1/places/{place_id}"
HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "id,displayName,formattedAddress,types,priceLevel,rating,userRatingCount"
}

# 價格等級換算為台幣（可以根據需要調整）
# Google Places API (New) 返回字符串格式的價格等級
PRICE_LEVEL_TO_NTD = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 300,  # 便宜 ($)
    "PRICE_LEVEL_MODERATE": 600,     # 中等 ($$)
    "PRICE_LEVEL_EXPENSIVE": 1200,   # 高價 ($$$)
    "PRICE_LEVEL_VERY_EXPENSIVE": 2000,  # 很貴 ($$$$)
}

# 料理風格關鍵字映射
CUISINE_KEYWORDS = {
    '台式': ['台', '台式', '台灣', '滷肉飯', '牛肉麵', '小籠包', '水餃', '麵線', '蚵仔煎'],
    '日式': ['日', '日式', '日本', '和牛', '燒肉', '壽司', '拉麵', '丼飯', '居酒屋', '和食'],
    '韓式': ['韓', '韓式', '韓國', '韓燒', '韓式燒肉', '韓式料理', '泡菜', '韓炸雞'],
    '美式': ['美式', '美國', '漢堡', '牛排', '義大利麵', 'pizza', 'pasta'],
    '義式': ['義', '義式', '義大利', 'pizza', 'pasta', '義大利麵', '義大利餐廳'],
    '法式': ['法', '法式', '法國', '法國料理'],
    '泰式': ['泰', '泰式', '泰國', '泰式料理'],
    '印度': ['印度', '咖哩', '印度料理'],
    '中式': ['中', '中式', '中華', '川菜', '粵菜', '港式', '港式茶餐廳', '廣東'],
    '火鍋': ['火鍋', '鍋物', '涮涮鍋', '麻辣鍋', '汕頭火鍋'],
    '燒肉': ['燒肉', '烤肉', '炭火'],
    '酒吧': ['bar', '酒吧', 'lounge', 'bistro', '餐酒館', '餐酒'],
    '素食': ['素食', '蔬食', 'vegan', 'vegetarian'],
}

# 餐廳類型關鍵字映射
TYPE_KEYWORDS = {
    '燒肉': ['燒肉', '烤肉', '炭火', '和牛燒肉', '日式燒肉'],
    '火鍋': ['火鍋', '鍋物', '涮涮鍋', '麻辣鍋', '汕頭火鍋'],
    '吃到飽': ['吃到飽', '放題', '無限', 'buffet', 'all you can eat'],
    '餐酒館': ['餐酒館', '餐酒', 'bistro', '餐酒餐廳'],
    '酒吧': ['bar', '酒吧', 'lounge', 'pub'],
    '鐵板燒': ['鐵板燒', '鐵板'],
    '牛排': ['牛排', 'steak', '牛排館'],
    '定食': ['定食', '套餐'],
}

def get_restaurant_details(place_id: str) -> Optional[Dict]:
    """使用 place_id 呼叫 Google Places API (New) 獲取餐廳詳情"""
    url = API_URL.format(place_id=place_id)
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print(f"API 速率限制，等待 2 秒...")
            time.sleep(2)
            return get_restaurant_details(place_id)  # 重試
        else:
            print(f"錯誤 {response.status_code} 對於 place_id {place_id}: {response.text}")
            return None
    except Exception as e:
        print(f"請求錯誤對於 place_id {place_id}: {str(e)}")
        return None

def extract_cuisine_style(name: str, types: List[str]) -> List[str]:
    """從餐廳名稱和類型推斷料理風格"""
    name_lower = name.lower()
    types_lower = ' '.join([t.lower() for t in types])
    combined_text = f"{name_lower} {types_lower}"
    
    matched_cuisines = []
    
    for cuisine, keywords in CUISINE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in combined_text:
                matched_cuisines.append(cuisine)
                break  # 找到一個關鍵字就足夠
    
    # 如果沒找到，使用預設值
    if not matched_cuisines:
        # 根據 types 判斷
        if 'restaurant' in types_lower:
            matched_cuisines.append('其他')
        else:
            matched_cuisines.append('其他')
    
    return matched_cuisines if matched_cuisines else ['其他']

def extract_restaurant_type(name: str, types: List[str]) -> List[str]:
    """從餐廳名稱和類型推斷餐廳類型"""
    name_lower = name.lower()
    types_lower = ' '.join([t.lower() for t in types])
    combined_text = f"{name_lower} {types_lower}"
    
    matched_types = []
    
    for rest_type, keywords in TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in combined_text:
                matched_types.append(rest_type)
                break
    
    # 特殊處理：bar 和 lounge 類型
    if any(word in combined_text for word in ['bar', '酒吧', 'lounge', 'bistro']):
        if '餐酒' in name_lower or '餐酒' in types_lower:
            if '餐酒館' not in matched_types:
                matched_types.append('餐酒館')
        else:
            if '酒吧' not in matched_types:
                matched_types.append('酒吧')
    
    # 如果沒找到，根據 types 推斷
    if not matched_types:
        if 'restaurant' in types_lower:
            matched_types.append('一般餐廳')
        elif 'bar' in types_lower or 'night_club' in types_lower:
            matched_types.append('酒吧')
        else:
            matched_types.append('其他')
    
    return matched_types if matched_types else ['其他']

def calculate_budget(price_level: Optional[str]) -> Optional[int]:
    """根據價格等級計算人均預算（台幣）"""
    if price_level is None:
        return None
    return PRICE_LEVEL_TO_NTD.get(price_level)

def process_restaurants(csv_file: str, output_file: str):
    """處理餐廳資料"""
    restaurants = []
    
    # 讀取 CSV 檔案
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    total = len(rows)
    print(f"總共有 {total} 間餐廳需要處理\n")
    
    for idx, row in enumerate(rows, 1):
        place_id = row.get('place_id', '').strip()
        restaurant_name = row.get('餐廳名稱', '').strip()
        restaurant_address = row.get('餐廳地址', '').strip()
        url = row.get('URL', '').strip()
        
        if not place_id:
            print(f"[{idx}/{total}] 跳過：{restaurant_name} (無 place_id)")
            continue
        
        print(f"[{idx}/{total}] 處理：{restaurant_name}")
        
        # 呼叫 API
        api_data = get_restaurant_details(place_id)
        
        if not api_data:
            print(f"  警告：無法取得 API 資料，使用原始資料")
            # 使用原始資料
            restaurant_info = {
                "name": restaurant_name,
                "address": restaurant_address,
                "cuisine_style": extract_cuisine_style(restaurant_name, []),
                "type": extract_restaurant_type(restaurant_name, []),
                "budget": None,
                "url": url
            }
        else:
            # 解析 API 資料
            api_name = api_data.get('displayName', {}).get('text', restaurant_name)
            api_address = api_data.get('formattedAddress', restaurant_address)
            api_types = api_data.get('types', [])
            price_level = api_data.get('priceLevel')
            
            # 使用 API 名稱和原始地址（優先使用原始地址，因為可能更準確）
            final_address = restaurant_address if restaurant_address else api_address
            
            # 推斷料理風格和類型
            cuisine_style = extract_cuisine_style(api_name, api_types)
            rest_type = extract_restaurant_type(api_name, api_types)
            budget = calculate_budget(price_level)
            
            restaurant_info = {
                "name": api_name,
                "address": final_address,
                "cuisine_style": cuisine_style,
                "type": rest_type,
                "budget": budget,
                "url": url
            }
            
            if price_level:
                print(f"  價格等級: {price_level}, 預算: {budget} 元")
            print(f"  料理風格: {', '.join(cuisine_style)}")
            print(f"  類型: {', '.join(rest_type)}")
        
        restaurants.append(restaurant_info)
        
        # 避免 API 速率限制（每次請求間隔 0.1 秒）
        if idx < total:
            time.sleep(0.1)
        
        # 每處理 50 間餐廳保存一次（防止資料遺失）
        if idx % 50 == 0:
            print(f"\n已處理 {idx} 間，暫時保存...")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"restaurants": restaurants}, f, ensure_ascii=False, indent=2)
    
    # 最終保存
    print(f"\n處理完成！共處理 {len(restaurants)} 間餐廳")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"restaurants": restaurants}, f, ensure_ascii=False, indent=2)
    
    print(f"\n資料已保存到：{output_file}")
    
    # 統計資訊
    print("\n=== 統計資訊 ===")
    cuisine_counts = {}
    type_counts = {}
    budget_counts = {"無資料": 0}
    
    for r in restaurants:
        for cuisine in r['cuisine_style']:
            cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
        for rest_type in r['type']:
            type_counts[rest_type] = type_counts.get(rest_type, 0) + 1
        budget = r['budget']
        if budget:
            budget_range = f"{budget}元"
            budget_counts[budget_range] = budget_counts.get(budget_range, 0) + 1
        else:
            budget_counts["無資料"] += 1
    
    print("\n料理風格分布：")
    for cuisine, count in sorted(cuisine_counts.items(), key=lambda x: -x[1]):
        print(f"  {cuisine}: {count}")
    
    print("\n餐廳類型分布：")
    for rest_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {rest_type}: {count}")
    
    print("\n預算分布：")
    for budget, count in sorted(budget_counts.items(), key=lambda x: -x[1]):
        print(f"  {budget}: {count}")

if __name__ == "__main__":
    csv_file = "已簽約餐廳.csv"
    output_file = "restaurants_database.json"
    
    print("開始處理餐廳資料...")
    print("=" * 50)
    
    process_restaurants(csv_file, output_file)
