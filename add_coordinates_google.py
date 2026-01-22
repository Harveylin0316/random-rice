#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Google Geocoding API 將餐廳地址轉換為座標
每月有 $200 免費額度（約 40,000 次請求），足夠處理 888 間餐廳
"""

import json
import requests
import time
from typing import Optional, Dict

# Google Geocoding API 配置
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    raise ValueError("請設定環境變數 GOOGLE_API_KEY，或在 .env 文件中配置")

GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

def geocode_address(address: str) -> Optional[Dict[str, float]]:
    """
    使用 Google Geocoding API 將地址轉換為座標
    
    Args:
        address: 餐廳地址
        
    Returns:
        {'lat': float, 'lng': float} 或 None
    """
    try:
        params = {
            'address': address,
            'key': API_KEY,
            'language': 'zh-TW',
            'region': 'tw'  # 限制在台灣地區
        }
        
        response = requests.get(GEOCODING_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                return {
                    'lat': location['lat'],
                    'lng': location['lng']
                }
            elif data['status'] == 'ZERO_RESULTS':
                print(f"  警告：找不到地址")
                return None
            elif data['status'] == 'OVER_QUERY_LIMIT':
                print(f"  錯誤：API 配額已用完")
                return None
            elif data['status'] == 'REQUEST_DENIED':
                print(f"  錯誤：API 請求被拒絕（請確認 Geocoding API 已啟用）")
                return None
            else:
                print(f"  錯誤：{data['status']}")
                return None
        else:
            print(f"  錯誤：HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  錯誤：{str(e)}")
        return None

def add_coordinates_to_database(input_file: str, output_file: str, test_mode: bool = False):
    """
    為餐廳資料庫添加座標資訊
    
    Args:
        input_file: 輸入的 JSON 檔案路徑
        output_file: 輸出的 JSON 檔案路徑
        test_mode: 測試模式（只處理前 10 間餐廳）
    """
    print("=" * 80)
    print("開始為餐廳添加座標資訊...")
    print("使用 Google Geocoding API（免費額度內）")
    print("=" * 80)
    
    # 載入資料庫
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data['restaurants']
    
    # 測試模式：只處理前 10 間
    if test_mode:
        restaurants = restaurants[:10]
        print("\n⚠️  測試模式：只處理前 10 間餐廳\n")
    
    total = len(restaurants)
    
    # 統計
    updated_count = 0
    failed_count = 0
    already_has_coords = 0
    failed_restaurants = []
    
    print(f"總共餐廳數：{total} 間")
    print(f"開始處理...\n")
    
    # 處理每間餐廳
    for i, restaurant in enumerate(restaurants, 1):
        # 如果已經有座標，跳過
        if 'coordinates' in restaurant and restaurant['coordinates']:
            already_has_coords += 1
            if i % 50 == 0:
                print(f"[{i}/{total}] 跳過已有座標的餐廳...")
            continue
        
        address = restaurant.get('address', '')
        name = restaurant.get('name', '未知')[:50]
        
        if not address:
            print(f"[{i}/{total}] {name} ... ⚠️  無地址")
            failed_count += 1
            failed_restaurants.append({'name': name, 'reason': '無地址'})
            continue
        
        print(f"[{i}/{total}] {name} ... ", end='', flush=True)
        
        # 獲取座標
        coordinates = geocode_address(address)
        
        if coordinates:
            restaurant['coordinates'] = coordinates
            updated_count += 1
            print(f"✅ ({coordinates['lat']:.4f}, {coordinates['lng']:.4f})")
        else:
            failed_count += 1
            failed_restaurants.append({'name': name, 'address': address, 'reason': '無法獲取座標'})
            print("❌ 無法獲取座標")
        
        # 每處理 1 間餐廳暫停 0.1 秒（避免觸發 API 速率限制）
        # Google Geocoding API 免費額度：每秒最多 50 次請求
        time.sleep(0.1)
        
        # 每 50 間顯示進度
        if i % 50 == 0:
            print(f"\n進度: {i}/{total} ({i*100//total}%) | 成功: {updated_count} | 失敗: {failed_count}\n")
    
    # 保存更新後的資料庫
    print("\n" + "=" * 80)
    print("保存更新後的資料庫...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 統計結果
    print("\n" + "=" * 80)
    print("✅ 處理完成！")
    print(f"\n統計：")
    print(f"  總餐廳數：{total} 間")
    print(f"  已有座標：{already_has_coords} 間")
    print(f"  新增座標：{updated_count} 間")
    print(f"  失敗：{failed_count} 間")
    if total > 0:
        success_rate = ((updated_count + already_has_coords) / total * 100)
        print(f"  成功率：{success_rate:.1f}%")
    print(f"\n資料已保存到：{output_file}")
    
    # 顯示失敗的餐廳（前 10 間）
    if failed_restaurants:
        print(f"\n失敗的餐廳（前 10 間）：")
        for i, rest in enumerate(failed_restaurants[:10], 1):
            print(f"  {i}. {rest['name']}")
            if 'address' in rest:
                print(f"     地址：{rest['address']}")
            print(f"     原因：{rest['reason']}")
        if len(failed_restaurants) > 10:
            print(f"  ... 還有 {len(failed_restaurants) - 10} 間餐廳失敗")
    
    # 費用提醒
    if not test_mode:
        print("\n💰 費用提醒：")
        print(f"  本次處理：{updated_count} 次 API 請求")
        print(f"  Google Geocoding API 免費額度：每月 $200（約 40,000 次）")
        print(f"  剩餘免費額度：約 {40000 - updated_count} 次")
        print(f"  本次費用：$0（在免費額度內）")
    
    print("=" * 80)

if __name__ == "__main__":
    import sys
    
    # 檢查是否為測試模式
    test_mode = '--test' in sys.argv
    
    if test_mode:
        print("⚠️  測試模式：只處理前 10 間餐廳")
        print("完整處理請執行：python3 add_coordinates_google.py\n")
    else:
        print("⚠️  注意：此腳本會為所有餐廳添加座標")
        print("建議先執行測試模式：python3 add_coordinates_google.py --test\n")
        response = input("確定要繼續嗎？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            exit(0)
    
    print("\n開始處理...\n")
    
    add_coordinates_to_database(
        'restaurants_database.json',
        'restaurants_database.json',
        test_mode=test_mode
    )
