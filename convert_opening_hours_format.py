#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將餐廳資料庫的營業時間格式從舊格式轉換為新格式

舊格式：
{
    "weekdays": ["11:00-14:00", "17:00-19:30"],
    "weekends": ["11:00-14:00"],
    "is_24h": false
}

新格式：
{
    "monday": ["11:00-14:00", "17:00-19:30"],
    "tuesday": ["11:00-14:00", "17:00-19:30"],
    "wednesday": ["11:00-14:00", "17:00-19:30"],
    "thursday": ["11:00-14:00", "17:00-19:30"],
    "friday": ["11:00-14:00", "17:00-19:30"],
    "saturday": ["11:00-14:00"],
    "sunday": ["11:00-14:00"],
    "is_24h": false
}
"""

import json
import sys
from typing import Dict, Any

def convert_opening_hours(old_format: Dict[str, Any]) -> Dict[str, Any]:
    """
    將舊格式轉換為新格式
    
    Args:
        old_format: 舊格式的營業時間資料
        
    Returns:
        新格式的營業時間資料
    """
    new_format = {
        'monday': [],
        'tuesday': [],
        'wednesday': [],
        'thursday': [],
        'friday': [],
        'saturday': [],
        'sunday': [],
        'is_24h': False
    }
    
    # 處理 is_24h
    if 'is_24h' in old_format:
        new_format['is_24h'] = bool(old_format['is_24h'])
    
    # 如果已經是 24 小時營業，所有天都設為空列表
    if new_format['is_24h']:
        return new_format
    
    # 處理舊格式的 weekdays 和 weekends
    weekdays_times = old_format.get('weekdays', [])
    weekends_times = old_format.get('weekends', [])
    
    # 如果舊格式沒有 weekdays 和 weekends，檢查是否已經是新格式
    if not weekdays_times and not weekends_times:
        # 檢查是否已經是新格式
        if 'monday' in old_format or 'tuesday' in old_format:
            # 已經是部分新格式，補齊缺少的欄位
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                if day in old_format:
                    new_format[day] = old_format[day] if isinstance(old_format[day], list) else []
                else:
                    new_format[day] = []
            if 'is_24h' in old_format:
                new_format['is_24h'] = old_format['is_24h']
            return new_format
    
    # 將 weekdays 的時間分配到週一到週五
    if weekdays_times and isinstance(weekdays_times, list):
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            new_format[day] = weekdays_times.copy()
    
    # 將 weekends 的時間分配到週六和週日
    if weekends_times and isinstance(weekends_times, list):
        for day in ['saturday', 'sunday']:
            new_format[day] = weekends_times.copy()
    
    # 如果只有 weekdays 沒有 weekends，週六日使用相同的時間
    if weekdays_times and not weekends_times:
        for day in ['saturday', 'sunday']:
            new_format[day] = weekdays_times.copy()
    
    # 如果只有 weekends 沒有 weekdays，週一到週五使用相同的時間
    if weekends_times and not weekdays_times:
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            new_format[day] = weekends_times.copy()
    
    return new_format

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
    
    # 統計需要轉換的餐廳
    needs_conversion = []
    already_new_format = []
    no_opening_hours = []
    
    for i, restaurant in enumerate(restaurants):
        opening_hours = restaurant.get('opening_hours')
        if opening_hours is None:
            no_opening_hours.append(i)
            continue
        
        # 檢查是否已經是 new format
        has_new_format = 'monday' in opening_hours or 'tuesday' in opening_hours
        has_old_format = 'weekdays' in opening_hours or 'weekends' in opening_hours
        
        if has_new_format and not has_old_format:
            already_new_format.append(i)
        elif has_old_format:
            needs_conversion.append((i, restaurant))
    
    print(f"\n需要轉換的餐廳：{len(needs_conversion)} 間")
    print(f"已經是新格式：{len(already_new_format)} 間")
    print(f"沒有 opening_hours：{len(no_opening_hours)} 間")
    
    if not needs_conversion:
        print("\n✓ 所有餐廳的營業時間格式已經是新格式！")
        return
    
    print("\n開始轉換營業時間格式...")
    print("="*70)
    
    updated_count = 0
    
    for index, restaurant in needs_conversion:
        name = restaurant.get('name', 'Unknown')
        old_opening_hours = restaurant.get('opening_hours', {})
        
        # 轉換格式
        new_opening_hours = convert_opening_hours(old_opening_hours)
        
        # 更新資料庫
        restaurants[index]['opening_hours'] = new_opening_hours
        updated_count += 1
        
        # 顯示更新資訊（每 100 間顯示一次）
        if updated_count % 100 == 0:
            print(f"已處理：{updated_count}/{len(needs_conversion)}")
    
    print(f"\n✓ 已轉換 {updated_count} 間餐廳的營業時間格式")
    
    # 保存更新後的資料庫
    print("\n保存更新後的資料庫...")
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print("✓ 資料庫已保存")
    
    # 顯示統計
    print("\n" + "="*70)
    print("轉換總結")
    print("="*70)
    print(f"總餐廳數：{total}")
    print(f"有 opening_hours：{len([r for r in restaurants if r.get('opening_hours')])} 間")
    print(f"已轉換：{updated_count} 間")
    print(f"已經是新格式：{len(already_new_format)} 間")
    
    # 顯示一些範例
    print("\n轉換後的範例：")
    print("="*70)
    example_count = 0
    for i, restaurant in enumerate(restaurants):
        opening_hours = restaurant.get('opening_hours')
        if opening_hours and 'monday' in opening_hours and example_count < 5:
            name = restaurant.get('name', 'Unknown')
            
            print(f"\n{example_count + 1}. {name}")
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                day_name = {'monday': '週一', 'tuesday': '週二', 'wednesday': '週三', 
                           'thursday': '週四', 'friday': '週五', 'saturday': '週六', 'sunday': '週日'}[day]
                times = opening_hours.get(day, [])
                if times:
                    print(f"   {day_name}: {', '.join(times)}")
                else:
                    print(f"   {day_name}: 全日休息")
            print(f"   24 小時: {opening_hours.get('is_24h', False)}")
            
            example_count += 1

if __name__ == '__main__':
    main()
