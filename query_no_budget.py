#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查詢無預算資料的餐廳
可輸出為 JSON 或 CSV 格式
"""

import json
import csv
import sys

def find_restaurants_without_budget(input_file: str, output_format: str = "json"):
    """找出所有無預算資料的餐廳"""
    
    # 讀取資料
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data.get('restaurants', [])
    
    # 過濾出無預算的餐廳
    no_budget_restaurants = [r for r in restaurants if r.get('budget') is None]
    
    print(f"總共餐廳數：{len(restaurants)}")
    print(f"無預算資料：{len(no_budget_restaurants)}")
    print(f"有預算資料：{len(restaurants) - len(no_budget_restaurants)}")
    
    if output_format == "json":
        # 輸出為 JSON
        output_file = "restaurants_no_budget.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"restaurants": no_budget_restaurants}, f, ensure_ascii=False, indent=2)
        print(f"\n已輸出到：{output_file}")
        
    elif output_format == "csv":
        # 輸出為 CSV
        output_file = "restaurants_no_budget.csv"
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'address', 'cuisine_style', 'type', 'budget', 'url'])
            writer.writeheader()
            for restaurant in no_budget_restaurants:
                # 將陣列轉為字串
                row = restaurant.copy()
                row['cuisine_style'] = ', '.join(row.get('cuisine_style', []))
                row['type'] = ', '.join(row.get('type', []))
                writer.writerow(row)
        print(f"\n已輸出到：{output_file}")
    
    elif output_format == "list":
        # 只列出前20間（方便查看）
        print(f"\n前20間無預算餐廳：")
        print("=" * 80)
        for i, restaurant in enumerate(no_budget_restaurants[:20], 1):
            cuisine = ', '.join(restaurant.get('cuisine_style', []))
            rest_type = ', '.join(restaurant.get('type', []))
            print(f"{i}. {restaurant['name']}")
            print(f"   地址：{restaurant['address']}")
            print(f"   料理風格：{cuisine}")
            print(f"   類型：{rest_type}")
            print()
    
    # 統計無預算餐廳的料理風格和類型分布
    print("\n=== 無預算餐廳統計 ===")
    cuisine_counts = {}
    type_counts = {}
    
    for restaurant in no_budget_restaurants:
        for cuisine in restaurant.get('cuisine_style', []):
            cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
        for rest_type in restaurant.get('type', []):
            type_counts[rest_type] = type_counts.get(rest_type, 0) + 1
    
    print("\n料理風格分布：")
    for cuisine, count in sorted(cuisine_counts.items(), key=lambda x: -x[1]):
        print(f"  {cuisine}: {count}")
    
    print("\n餐廳類型分布：")
    for rest_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {rest_type}: {count}")
    
    return no_budget_restaurants

if __name__ == "__main__":
    input_file = "restaurants_database.json"
    
    # 可以選擇輸出格式：json, csv, list
    output_format = sys.argv[1] if len(sys.argv) > 1 else "list"
    
    if output_format not in ["json", "csv", "list"]:
        print("用法: python3 query_no_budget.py [json|csv|list]")
        print("  json: 輸出為 JSON 檔案")
        print("  csv: 輸出為 CSV 檔案")
        print("  list: 只列出前20間（預設）")
        sys.exit(1)
    
    find_restaurants_without_budget(input_file, output_format)
