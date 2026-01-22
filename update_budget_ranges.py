#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將餐廳資料庫中的預算從單一數字改為區間格式
"""

import json
from typing import Optional

# 價格等級對應的預算區間（台幣）
PRICE_LEVEL_TO_RANGE = {
    "PRICE_LEVEL_FREE": "0-100",
    "PRICE_LEVEL_INEXPENSIVE": "200-400",      # 便宜 ($)
    "PRICE_LEVEL_MODERATE": "500-800",         # 中等 ($$)
    "PRICE_LEVEL_EXPENSIVE": "1000-1500",      # 高價 ($$$)
    "PRICE_LEVEL_VERY_EXPENSIVE": "2000以上",  # 很貴 ($$$$)
}

# 舊的單一價格對應到新的區間
OLD_PRICE_TO_RANGE = {
    300: "200-400",
    600: "500-800",
    1200: "1000-1500",
    2000: "2000以上",
}

def convert_budget_to_range(budget: Optional[int]) -> Optional[str]:
    """將單一預算數字轉換為區間格式"""
    if budget is None:
        return None
    
    # 直接映射舊的價格到區間
    if budget in OLD_PRICE_TO_RANGE:
        return OLD_PRICE_TO_RANGE[budget]
    
    # 如果不在映射中，根據數值範圍判斷
    if budget < 300:
        return "200以下"
    elif budget < 500:
        return "200-400"
    elif budget < 800:
        return "500-800"
    elif budget < 1500:
        return "800-1500"
    elif budget < 2000:
        return "1500-2000"
    else:
        return "2000以上"

def update_restaurant_budgets(input_file: str, output_file: str):
    """更新餐廳資料庫中的預算欄位"""
    
    # 讀取原始資料
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data.get('restaurants', [])
    total = len(restaurants)
    
    print(f"開始更新 {total} 間餐廳的預算欄位...")
    
    updated_count = 0
    null_count = 0
    
    # 更新每間餐廳的預算
    for restaurant in restaurants:
        old_budget = restaurant.get('budget')
        new_budget = convert_budget_to_range(old_budget)
        
        if old_budget is not None:
            restaurant['budget'] = new_budget
            updated_count += 1
        else:
            null_count += 1
    
    # 保存更新後的資料
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n更新完成！")
    print(f"已更新預算：{updated_count} 間")
    print(f"無預算資料：{null_count} 間")
    print(f"\n資料已保存到：{output_file}")
    
    # 統計新的預算分布
    print("\n=== 新的預算分布 ===")
    budget_counts = {}
    for restaurant in restaurants:
        budget = restaurant.get('budget')
        if budget:
            budget_counts[budget] = budget_counts.get(budget, 0) + 1
        else:
            budget_counts["無資料"] = budget_counts.get("無資料", 0) + 1
    
    for budget_range, count in sorted(budget_counts.items(), key=lambda x: -x[1]):
        print(f"  {budget_range}元: {count}")

if __name__ == "__main__":
    input_file = "restaurants_database.json"
    output_file = "restaurants_database.json"  # 直接覆蓋原檔案
    
    update_restaurant_budgets(input_file, output_file)
