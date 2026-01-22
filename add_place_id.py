#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 '已簽約餐廳.csv' 讀取 place_id，並添加到 restaurants_database.json 中
"""

import json
import csv
from typing import Dict, Optional

def load_csv_place_ids(csv_file: str) -> Dict[str, str]:
    """
    從 CSV 檔案讀取 place_id，建立映射表
    使用 matched_name 和 URL 作為 key
    """
    place_id_map = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            place_id = row.get('place_id', '').strip()
            matched_name = row.get('matched_name', '').strip()
            url = row.get('URL', '').strip()
            
            if not place_id:
                continue
            
            # 使用 matched_name 作為主要 key
            if matched_name:
                place_id_map[matched_name] = place_id
            
            # 使用 URL 作為備用 key
            if url:
                place_id_map[url] = place_id
    
    return place_id_map

def add_place_ids_to_database(json_file: str, place_id_map: Dict[str, str]):
    """
    為餐廳資料庫添加 place_id
    """
    print("=" * 80)
    print("開始為餐廳資料庫添加 place_id...")
    print("=" * 80)
    
    # 載入資料庫
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data['restaurants']
    total = len(restaurants)
    
    # 統計
    updated_count = 0
    already_has_place_id = 0
    not_found_count = 0
    not_found_restaurants = []
    
    print(f"\n總共餐廳數：{total} 間")
    print(f"開始處理...\n")
    
    # 處理每間餐廳
    for i, restaurant in enumerate(restaurants, 1):
        name = restaurant.get('name', '')
        url = restaurant.get('url', '')
        
        # 如果已經有 place_id，跳過
        if 'place_id' in restaurant and restaurant['place_id']:
            already_has_place_id += 1
            if i % 100 == 0:
                print(f"[{i}/{total}] 跳過已有 place_id 的餐廳...")
            continue
        
        # 嘗試使用 name 匹配
        place_id = place_id_map.get(name)
        
        # 如果 name 匹配失敗，嘗試使用 URL 匹配
        if not place_id and url:
            place_id = place_id_map.get(url)
        
        if place_id:
            restaurant['place_id'] = place_id
            updated_count += 1
            if i % 50 == 0:
                print(f"[{i}/{total}] {name[:50]} ... ✅ place_id: {place_id[:30]}")
        else:
            not_found_count += 1
            not_found_restaurants.append({
                'name': name,
                'url': url
            })
            if i % 50 == 0:
                print(f"[{i}/{total}] {name[:50]} ... ❌ 未找到匹配的 place_id")
    
    # 保存更新後的資料庫
    print("\n" + "=" * 80)
    print("保存更新後的資料庫...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 統計結果
    print("\n" + "=" * 80)
    print("✅ 處理完成！")
    print(f"\n統計：")
    print(f"  總餐廳數：{total} 間")
    print(f"  已有 place_id：{already_has_place_id} 間")
    print(f"  新增 place_id：{updated_count} 間")
    print(f"  未找到匹配：{not_found_count} 間")
    if total > 0:
        success_rate = ((updated_count + already_has_place_id) / total * 100)
        print(f"  成功率：{success_rate:.1f}%")
    print(f"\n資料已保存到：{json_file}")
    
    # 顯示未找到匹配的餐廳（前 10 間）
    if not_found_restaurants:
        print(f"\n未找到匹配的餐廳（前 10 間）：")
        for i, rest in enumerate(not_found_restaurants[:10], 1):
            print(f"  {i}. {rest['name']}")
            if rest['url']:
                print(f"     URL: {rest['url']}")
        if len(not_found_restaurants) > 10:
            print(f"  ... 還有 {len(not_found_restaurants) - 10} 間餐廳未找到匹配")
    
    print("=" * 80)

if __name__ == "__main__":
    csv_file = '已簽約餐廳.csv'
    json_file = 'restaurants_database.json'
    
    print("載入 CSV 檔案...")
    place_id_map = load_csv_place_ids(csv_file)
    print(f"✅ 從 CSV 載入了 {len(place_id_map)} 個 place_id 映射\n")
    
    add_place_ids_to_database(json_file, place_id_map)
