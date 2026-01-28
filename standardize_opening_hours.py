#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一餐廳資料庫的營業時間格式

標準格式：
{
    "weekdays": ["11:00-14:00", "17:00-19:30"],  # 週一至五，空列表表示沒有營業時間
    "weekends": ["11:00-14:00"],  # 週六日，空列表表示全日休息或沒有營業時間
    "is_24h": false  # 是否 24 小時營業
}
"""

import json
import sys
from typing import Dict, List, Any

def standardize_opening_hours(opening_hours: Dict[str, Any]) -> Dict[str, Any]:
    """
    統一營業時間格式
    
    Args:
        opening_hours: 原始營業時間資料
        
    Returns:
        標準化後的營業時間資料
    """
    standardized = {
        'weekdays': [],
        'weekends': [],
        'is_24h': False
    }
    
    # 處理 is_24h
    if 'is_24h' in opening_hours:
        standardized['is_24h'] = bool(opening_hours['is_24h'])
    elif opening_hours.get('is_24h') is None:
        standardized['is_24h'] = False
    
    # 處理 weekdays
    if 'weekdays' in opening_hours:
        weekdays = opening_hours['weekdays']
        if isinstance(weekdays, list):
            standardized['weekdays'] = weekdays
        elif weekdays is not None:
            # 如果不是列表，嘗試轉換
            standardized['weekdays'] = [weekdays] if weekdays else []
    else:
        # 如果沒有 weekdays，檢查是否有其他格式
        # 例如：只有一個時間範圍，可能是舊格式
        if 'weekends' in opening_hours and opening_hours['weekends']:
            # 如果只有 weekends，假設 weekdays 和 weekends 相同
            standardized['weekdays'] = opening_hours['weekends'] if isinstance(opening_hours['weekends'], list) else []
        else:
            standardized['weekdays'] = []
    
    # 處理 weekends
    if 'weekends' in opening_hours:
        weekends = opening_hours['weekends']
        if isinstance(weekends, list):
            standardized['weekends'] = weekends
        elif weekends is not None:
            # 如果不是列表，嘗試轉換
            standardized['weekends'] = [weekends] if weekends else []
    else:
        # 如果沒有 weekends，檢查是否有 weekdays
        if 'weekdays' in opening_hours and opening_hours['weekdays']:
            # 如果只有 weekdays，假設 weekends 和 weekdays 相同
            standardized['weekends'] = opening_hours['weekdays'] if isinstance(opening_hours['weekdays'], list) else []
        else:
            standardized['weekends'] = []
    
    # 如果兩個都是空列表，且 is_24h 為 False，可能是沒有營業時間
    # 保持原樣（空列表）
    
    return standardized

def main():
    """主函數"""
    db_file = 'restaurants_database.json'
    backup_file = 'restaurants_database_backup.json'
    
    print("載入餐廳資料庫...")
    with open(db_file, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    restaurants = db.get('restaurants', [])
    total = len(restaurants)
    
    print(f"找到 {total} 間餐廳")
    print("="*70)
    
    # 創建備份
    print(f"\n創建備份：{backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print("✓ 備份完成")
    
    # 統計需要標準化的餐廳
    needs_standardization = []
    already_standard = []
    
    for i, restaurant in enumerate(restaurants):
        opening_hours = restaurant.get('opening_hours')
        if opening_hours is None:
            continue
        
        # 檢查是否需要標準化
        needs_fix = False
        
        # 檢查是否缺少必要欄位
        if 'weekdays' not in opening_hours:
            needs_fix = True
        if 'weekends' not in opening_hours:
            needs_fix = True
        if 'is_24h' not in opening_hours:
            needs_fix = True
        
        # 檢查類型是否正確
        if 'weekdays' in opening_hours and not isinstance(opening_hours['weekdays'], list):
            needs_fix = True
        if 'weekends' in opening_hours and not isinstance(opening_hours['weekends'], list):
            needs_fix = True
        if 'is_24h' in opening_hours and not isinstance(opening_hours['is_24h'], bool):
            needs_fix = True
        
        if needs_fix:
            needs_standardization.append((i, restaurant))
        else:
            already_standard.append(i)
    
    print(f"\n需要標準化的餐廳：{len(needs_standardization)} 間")
    print(f"已經符合標準：{len(already_standard)} 間")
    
    if not needs_standardization:
        print("\n✓ 所有餐廳的營業時間格式已經統一！")
        return
    
    print("\n開始標準化營業時間格式...")
    print("="*70)
    
    updated_count = 0
    
    for index, restaurant in needs_standardization:
        name = restaurant.get('name', 'Unknown')
        old_opening_hours = restaurant.get('opening_hours', {})
        
        # 標準化
        standardized = standardize_opening_hours(old_opening_hours)
        
        # 更新資料庫
        restaurants[index]['opening_hours'] = standardized
        updated_count += 1
        
        # 顯示更新資訊（每 50 間顯示一次）
        if updated_count % 50 == 0:
            print(f"已處理：{updated_count}/{len(needs_standardization)}")
    
    print(f"\n✓ 已標準化 {updated_count} 間餐廳的營業時間格式")
    
    # 保存更新後的資料庫
    print("\n保存更新後的資料庫...")
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print("✓ 資料庫已保存")
    
    # 顯示統計
    print("\n" + "="*70)
    print("標準化總結")
    print("="*70)
    print(f"總餐廳數：{total}")
    print(f"有 opening_hours：{len([r for r in restaurants if r.get('opening_hours')])} 間")
    print(f"已標準化：{updated_count} 間")
    print(f"已符合標準：{len(already_standard)} 間")
    
    # 顯示一些範例
    print("\n標準化後的範例：")
    print("="*70)
    example_count = 0
    for i, restaurant in enumerate(restaurants):
        opening_hours = restaurant.get('opening_hours')
        if opening_hours and example_count < 5:
            name = restaurant.get('name', 'Unknown')
            weekdays = opening_hours.get('weekdays', [])
            weekends = opening_hours.get('weekends', [])
            is_24h = opening_hours.get('is_24h', False)
            
            print(f"\n{example_count + 1}. {name}")
            if weekdays:
                print(f"   週一至五: {', '.join(weekdays)}")
            else:
                print(f"   週一至五: 無")
            if weekends:
                print(f"   週六日: {', '.join(weekends)}")
            else:
                print(f"   週六日: 全日休息")
            print(f"   24 小時: {is_24h}")
            
            example_count += 1

if __name__ == '__main__':
    main()
