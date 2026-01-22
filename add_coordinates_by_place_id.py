#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Google Places API (New) 透過 place_id 獲取餐廳座標
每月有 $200 免費額度，足夠處理 888 間餐廳
"""

import json
import requests
import time
from typing import Optional, Dict

# Google Places API (New) 配置
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    raise ValueError("請設定環境變數 GOOGLE_API_KEY，或在 .env 文件中配置")

PLACES_API_URL = "https://places.googleapis.com/v1/places/{place_id}"

def get_coordinates_by_place_id(place_id: str) -> Optional[Dict[str, float]]:
    """
    使用 Google Places API (New) 透過 place_id 獲取座標
    
    Args:
        place_id: Google Place ID
        
    Returns:
        {'lat': float, 'lng': float} 或 None
    """
    try:
        url = PLACES_API_URL.format(place_id=place_id)
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': API_KEY,
            'X-Goog-FieldMask': 'location'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'location' in data:
                location = data['location']
                return {
                    'lat': location.get('latitude'),
                    'lng': location.get('longitude')
                }
            else:
                print(f"  警告：回應中沒有 location 資料")
                return None
        elif response.status_code == 404:
            print(f"  錯誤：找不到該 place_id")
            return None
        elif response.status_code == 403:
            print(f"  錯誤：API 權限被拒絕（請確認 Places API (New) 已啟用）")
            return None
        else:
            print(f"  錯誤：HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"  詳細：{error_data}")
            except:
                pass
            return None
            
    except Exception as e:
        print(f"  錯誤：{str(e)}")
        return None

def add_coordinates_to_database(json_file: str, batch_size: int = 50, start_index: int = 0):
    """
    為餐廳資料庫添加座標資訊（使用 place_id）
    
    Args:
        json_file: JSON 檔案路徑
        batch_size: 每批處理的餐廳數量
        start_index: 從第幾間開始處理
    """
    print("=" * 80)
    print("開始為餐廳添加座標資訊（使用 place_id）...")
    print("使用 Google Places API (New)")
    print("=" * 80)
    
    # 載入資料庫
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data['restaurants']
    
    # 找出所有沒有座標的餐廳
    no_coords_restaurants = [(i, r) for i, r in enumerate(restaurants) 
                             if not r.get('coordinates') or not r.get('coordinates', {}).get('lat')]
    
    print(f"\n總共無座標餐廳：{len(no_coords_restaurants)} 間")
    print(f"本次處理：從第 {start_index + 1} 間開始，處理 {batch_size} 間\n")
    
    # 處理指定範圍的餐廳
    if start_index >= len(no_coords_restaurants):
        print(f"⚠️  起始索引 {start_index} 超出範圍（總共 {len(no_coords_restaurants)} 間無座標餐廳）")
        return
    
    end_index = min(start_index + batch_size, len(no_coords_restaurants))
    restaurants_to_process = no_coords_restaurants[start_index:end_index]
    
    updated_count = 0
    failed_count = 0
    no_place_id_count = 0
    
    for idx, (original_idx, restaurant) in enumerate(restaurants_to_process, 1):
        name = restaurant.get('name', '未知餐廳')
        place_id = restaurant.get('place_id', '')
        
        current_num = start_index + idx
        print(f"[{current_num}/{len(no_coords_restaurants)}] {name[:50]}")
        
        if not place_id:
            print(f"  ❌ 無 place_id，跳過")
            no_place_id_count += 1
            failed_count += 1
            continue
        
        # 獲取座標
        coordinates = get_coordinates_by_place_id(place_id)
        
        if coordinates:
            restaurants[original_idx]['coordinates'] = coordinates
            print(f"  ✅ ({coordinates['lat']:.4f}, {coordinates['lng']:.4f})")
            updated_count += 1
        else:
            print(f"  ❌ 無法獲取座標")
            failed_count += 1
        
        # 每處理 10 間保存一次
        if idx % 10 == 0:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  💾 已保存進度")
        
        # 避免請求過快（Google Places API 免費額度：每秒最多 50 次請求）
        time.sleep(0.1)
    
    # 最終保存
    print("\n" + "=" * 80)
    print("保存更新後的資料庫...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("✅ 本批次處理完成！")
    print(f"\n統計：")
    print(f"  處理數量：{len(restaurants_to_process)} 間")
    print(f"  成功更新：{updated_count} 間")
    print(f"  失敗：{failed_count} 間")
    print(f"  無 place_id：{no_place_id_count} 間")
    if len(restaurants_to_process) > 0:
        print(f"  成功率：{updated_count/len(restaurants_to_process)*100:.1f}%")
    print("=" * 80)
    
    # 提示下一批次
    if end_index < len(no_coords_restaurants):
        print(f"\n💡 提示：還有 {len(no_coords_restaurants) - end_index} 間餐廳待處理")
        print(f"   下次運行：python3 add_coordinates_by_place_id.py --start {end_index}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="使用 place_id 批量添加餐廳座標")
    parser.add_argument('--batch-size', type=int, default=50, help='每批處理的餐廳數量（預設：50）')
    parser.add_argument('--start', type=int, default=0, help='從第幾間開始處理（預設：0）')
    
    args = parser.parse_args()
    
    add_coordinates_to_database(
        'restaurants_database.json',
        batch_size=args.batch_size,
        start_index=args.start
    )
