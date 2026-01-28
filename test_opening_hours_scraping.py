#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試從 OpenRice URL 爬取餐廳營業時間
"""

import json
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional

def scrape_opening_hours_from_openrice(url: str) -> Dict:
    """
    從 OpenRice URL 爬取餐廳營業時間
    
    Args:
        url: OpenRice 餐廳頁面 URL
        
    Returns:
        字典，包含：
        - success: 是否成功
        - opening_hours: 營業時間資料
        - raw_html: 原始 HTML（用於調試）
    """
    print(f"\n正在爬取營業時間：{url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 方法1: 查找營業時間相關的 HTML 結構
        # OpenRice 可能使用不同的 class 名稱，我們需要嘗試多種方式
        
        opening_hours = {}
        
        # 嘗試查找包含「營業時間」文字的區塊
        all_text = soup.get_text()
        
        # 檢查是否為 24 小時營業
        is_24h = False
        if re.search(r'24[小時時]|全天|全天候', all_text, re.IGNORECASE):
            is_24h = True
            opening_hours['is_24h'] = True
            print("  ✓ 檢測到：24 小時營業")
            return {
                'success': True,
                'opening_hours': opening_hours,
                'raw_html': None
            }
        
        # 方法2: 查找特定的 HTML 結構
        # 嘗試查找包含營業時間的 div 或 section
        hours_sections = soup.find_all(['div', 'section', 'dl', 'ul', 'li'], 
                                      class_=re.compile(r'hour|time|營業|open|opening', re.IGNORECASE))
        
        print(f"  找到 {len(hours_sections)} 個可能的營業時間區塊")
        
        # 檢查這些區塊的內容
        for i, section in enumerate(hours_sections[:3]):  # 只檢查前3個
            section_text = section.get_text(strip=True)
            if len(section_text) < 200:  # 只顯示較短的文字
                print(f"    區塊 {i+1}: {section_text[:100]}")
        
        # 方法3: 查找包含時間格式的文字（例如：11:00-14:00）
        time_pattern = r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})'
        time_matches = re.findall(time_pattern, all_text)
        
        if time_matches:
            print(f"  找到 {len(time_matches)} 個時間範圍")
            for match in time_matches[:5]:  # 只顯示前5個
                start_hour, start_min, end_hour, end_min = match
                print(f"    - {start_hour}:{start_min} - {end_hour}:{end_min}")
                
                # 嘗試找到這個時間範圍的上下文
                context_pattern = rf'.{{0,50}}{start_hour}:{start_min}\s*[-~至]\s*{end_hour}:{end_min}.{{0,50}}'
                context_match = re.search(context_pattern, all_text)
                if context_match:
                    context = context_match.group(0)
                    print(f"      上下文: {context}")
        
        # 方法4: 優先查找「星期一至五」和「星期六至日」分別的格式
        # 例如：星期一至五11:00 - 14:00, 17:00 - 21:00；星期六至日11:00 - 15:00, 17:00 - 22:00
        weekday_patterns = [
            r'[週周]?[一二三四五]+[至到][週周]?[一二三四五]*',  # 匹配「星期一至五」或「週一至五」
            r'[週周][一五][至到][週周]?[一五]',  # 匹配「週一至五」
        ]
        weekend_patterns = [
            r'[週周]?[六日]+[至到][週周]?[六日]*',  # 匹配「星期六至日」或「週六至日」
            r'[週周][六日][至到][週周]?[六日]',  # 匹配「週六至日」
        ]
        
        weekday_match = None
        weekend_match = None
        
        # 查找週一至五的匹配
        for pattern in weekday_patterns:
            weekday_match = re.search(pattern, all_text)
            if weekday_match:
                break
        
        # 查找週六至日的匹配
        for pattern in weekend_patterns:
            weekend_match = re.search(pattern, all_text)
            if weekend_match:
                break
        
        # 如果找到週一至五或週六至日的格式
        if weekday_match or weekend_match:
            if weekday_match:
                # 提取週一至五的時間範圍
                # 從匹配位置結束處開始，向後查找時間範圍（避免包含週六日的時間）
                match_start = weekday_match.end()  # 從匹配結束處開始
                
                # 如果也有週六日的匹配，則週一至五的時間範圍應該在兩者之間
                if weekend_match:
                    context_end = weekend_match.start()  # 到週六日匹配開始處
                else:
                    context_end = min(len(all_text), match_start + 200)
                
                context = all_text[match_start:context_end]
                print(f"  找到「週一至五」格式: {weekday_match.group(0)}")
                print(f"    時間上下文: {context[:100]}")
                
                time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})', context)
                if time_ranges:
                    parsed_ranges = [
                        f"{start_h}:{start_m}-{end_h}:{end_m}"
                        for start_h, start_m, end_h, end_m in time_ranges
                    ]
                    # 去重
                    seen = set()
                    unique_ranges = []
                    for r in parsed_ranges:
                        if r not in seen:
                            seen.add(r)
                            unique_ranges.append(r)
                    opening_hours['weekdays'] = unique_ranges
                    print(f"    週一到週五: {unique_ranges}")
            
            if weekend_match:
                # 提取週六至日的時間範圍
                match_start = weekend_match.end()  # 從匹配結束處開始
                match_end = min(len(all_text), match_start + 200)
                
                context = all_text[match_start:match_end]
                print(f"  找到「週六至日」格式: {weekend_match.group(0)}")
                print(f"    時間上下文: {context[:100]}")
                
                time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})', context)
                if time_ranges:
                    parsed_ranges = [
                        f"{start_h}:{start_m}-{end_h}:{end_m}"
                        for start_h, start_m, end_h, end_m in time_ranges
                    ]
                    # 去重
                    seen = set()
                    unique_ranges = []
                    for r in parsed_ranges:
                        if r not in seen:
                            seen.add(r)
                            unique_ranges.append(r)
                    opening_hours['weekends'] = unique_ranges
                    print(f"    週六日: {unique_ranges}")
            
            # 如果只找到其中一個，另一個使用相同的值（或留空）
            if 'weekdays' in opening_hours and 'weekends' not in opening_hours:
                opening_hours['weekends'] = opening_hours['weekdays']
                print(f"    週六日（使用週一到週五的時間）: {opening_hours['weekends']}")
            elif 'weekends' in opening_hours and 'weekdays' not in opening_hours:
                opening_hours['weekdays'] = opening_hours['weekends']
                print(f"    週一到週五（使用週六日的時間）: {opening_hours['weekdays']}")
            
            if opening_hours:
                opening_hours['is_24h'] = False
                return {
                    'success': True,
                    'opening_hours': opening_hours,
                    'raw_html': None
                }
        
        # 方法5: 查找「星期一至日」或「週一至週日」格式（所有天相同）
        # 例如：星期一至日11:30 - 15:0017:30 - 22:00
        all_days_patterns = [
            r'[週周]?[一二三四五六日]+[至到][一二三四五六日]*\s*([^\n]{0,200})',  # 標準格式
            r'[週周]?[一二三四五六日]+[至到][日]?\s*([^\n]{0,200})',  # 簡化格式：週一至日
        ]
        
        all_days_match = None
        for pattern in all_days_patterns:
            all_days_match = re.search(pattern, all_text)
            if all_days_match:
                # 確保不是已經匹配過的「週一至五」或「週六至日」
                match_text = all_days_match.group(0)
                if '一至五' not in match_text and '六至日' not in match_text:
                    break
                else:
                    all_days_match = None
        
        if all_days_match:
            time_str = all_days_match.group(1).strip()
            print(f"  找到「週一至日」格式: {time_str[:100]}")
            
            # 改進：從整個文字中提取所有時間範圍（不僅限於匹配的部分）
            # 因為時間可能分散在不同位置
            full_context_start = max(0, all_days_match.start() - 50)
            full_context_end = min(len(all_text), all_days_match.end() + 200)
            full_context = all_text[full_context_start:full_context_end]
            
            # 從完整上下文中提取所有時間範圍
            time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})', full_context)
            if time_ranges:
                parsed_ranges = [
                    f"{start_h}:{start_m}-{end_h}:{end_m}"
                    for start_h, start_m, end_h, end_m in time_ranges
                ]
                # 去重（保持順序）
                seen = set()
                unique_ranges = []
                for r in parsed_ranges:
                    if r not in seen:
                        seen.add(r)
                        unique_ranges.append(r)
                
                opening_hours['weekdays'] = unique_ranges
                opening_hours['weekends'] = unique_ranges  # 如果寫「星期一至日」，通常週末也相同
                opening_hours['is_24h'] = False
                print(f"  解析結果：{unique_ranges}")
                return {
                    'success': True,
                    'opening_hours': opening_hours,
                    'raw_html': None
                }
        
        # 方法5: 查找週一到週日的營業時間（個別）
        # 常見格式：週一：11:00-14:00, 17:00-21:00
        day_patterns = {
            'monday': r'[週周]一[：:]\s*([^\n]+)',
            'tuesday': r'[週周]二[：:]\s*([^\n]+)',
            'wednesday': r'[週周]三[：:]\s*([^\n]+)',
            'thursday': r'[週周]四[：:]\s*([^\n]+)',
            'friday': r'[週周]五[：:]\s*([^\n]+)',
            'saturday': r'[週周]六[：:]\s*([^\n]+)',
            'sunday': r'[週周]日[：:]\s*([^\n]+)',
        }
        
        parsed_hours = {}
        for day_en, pattern in day_patterns.items():
            match = re.search(pattern, all_text)
            if match:
                time_str = match.group(1).strip()
                # 解析時間字串，提取時間範圍
                time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})', time_str)
                if time_ranges:
                    parsed_hours[day_en] = [
                        f"{start_h}:{start_m}-{end_h}:{end_m}"
                        for start_h, start_m, end_h, end_m in time_ranges
                    ]
                    print(f"  {day_en}: {parsed_hours[day_en]}")
        
        # 如果找到任何營業時間，返回結果
        if parsed_hours:
            opening_hours.update(parsed_hours)
            opening_hours['is_24h'] = False
            return {
                'success': True,
                'opening_hours': opening_hours,
                'raw_html': None
            }
        
        # 方法7: 如果找到時間範圍但沒有找到週幾，嘗試推斷
        # 如果找到 11:30-15:00 和 17:30-22:00，可能是標準的營業時間
        if time_matches and len(time_matches) >= 2 and not opening_hours:
            # 嘗試找到包含這些時間的文字段落
            time_ranges = []
            for match in time_matches[:2]:  # 只取前兩個
                start_hour, start_min, end_hour, end_min = match
                time_ranges.append(f"{start_hour}:{start_min}-{end_hour}:{end_min}")
            
            # 檢查這些時間是否在相近的位置（可能是同一段營業時間說明）
            if len(time_ranges) == 2:
                opening_hours['weekdays'] = time_ranges
                opening_hours['weekends'] = time_ranges  # 假設週末相同
                opening_hours['is_24h'] = False
                print(f"  推斷營業時間：{time_ranges}")
                return {
                    'success': True,
                    'opening_hours': opening_hours,
                    'raw_html': None
                }
        
        # 方法5: 查找簡化格式（週一到週五相同，週六日相同）
        weekday_pattern = r'[週周][一五][：:]\s*([^\n]+)'
        weekend_pattern = r'[週周][六日][：:]\s*([^\n]+)'
        
        weekday_match = re.search(weekday_pattern, all_text)
        weekend_match = re.search(weekend_pattern, all_text)
        
        if weekday_match or weekend_match:
            if weekday_match:
                time_str = weekday_match.group(1).strip()
                time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})', time_str)
                if time_ranges:
                    opening_hours['weekdays'] = [
                        f"{start_h}:{start_m}-{end_h}:{end_m}"
                        for start_h, start_m, end_h, end_m in time_ranges
                    ]
                    print(f"  週一到週五: {opening_hours['weekdays']}")
            
            if weekend_match:
                time_str = weekend_match.group(1).strip()
                time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})', time_str)
                if time_ranges:
                    opening_hours['weekends'] = [
                        f"{start_h}:{start_m}-{end_h}:{end_m}"
                        for start_h, start_m, end_h, end_m in time_ranges
                    ]
                    print(f"  週六日: {opening_hours['weekends']}")
            
            if opening_hours:
                opening_hours['is_24h'] = False
                return {
                    'success': True,
                    'opening_hours': opening_hours,
                    'raw_html': None
                }
        
        # 如果都沒找到，返回失敗
        print("  ⚠️  無法找到營業時間資訊")
        return {
            'success': False,
            'opening_hours': None,
            'raw_html': response.text[:2000]  # 返回前2000字元用於調試
        }
        
    except Exception as e:
        print(f"  ❌ 錯誤：{str(e)}")
        return {
            'success': False,
            'opening_hours': None,
            'error': str(e)
        }

def main():
    # 從資料庫中選擇多間餐廳進行測試
    print("載入餐廳資料庫...")
    with open('restaurants_database.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # 選擇多間不同類型的餐廳進行測試
    # 選擇不同索引的餐廳，以涵蓋不同格式
    test_indices = [0, 10, 50, 100, 200, 500]  # 選擇不同位置的餐廳
    test_restaurants = []
    
    for idx in test_indices:
        if idx < len(db['restaurants']):
            test_restaurants.append((idx, db['restaurants'][idx]))
    
    print(f"\n選擇了 {len(test_restaurants)} 間餐廳進行測試")
    print("="*70)
    
    results = []
    
    for i, (original_idx, restaurant) in enumerate(test_restaurants, 1):
        print(f"\n{'='*70}")
        print(f"測試 {i}/{len(test_restaurants)}: {restaurant['name']}")
        print(f"索引: {original_idx}")
        print(f"URL: {restaurant['url']}")
        print("-"*70)
        
        # 爬取營業時間
        result = scrape_opening_hours_from_openrice(restaurant['url'])
        
        # 記錄結果
        test_result = {
            'name': restaurant['name'],
            'url': restaurant['url'],
            'success': result['success'],
            'opening_hours': result.get('opening_hours'),
            'error': result.get('error')
        }
        results.append(test_result)
        
        # 顯示結果
        if result['success']:
            print(f"\n✓ 成功爬取營業時間")
            print(f"營業時間資料：")
            print(json.dumps(result['opening_hours'], ensure_ascii=False, indent=2))
        else:
            print(f"\n✗ 爬取失敗")
            if 'error' in result:
                print(f"錯誤訊息：{result['error']}")
        
        # 添加延遲，避免請求過快
        if i < len(test_restaurants):
            import time
            time.sleep(1)
    
    # 顯示總結
    print("\n" + "="*70)
    print("測試總結")
    print("="*70)
    
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print(f"總測試數：{len(results)}")
    print(f"成功：{success_count}")
    print(f"失敗：{fail_count}")
    print(f"成功率：{success_count/len(results)*100:.1f}%")
    
    print("\n成功案例：")
    for r in results:
        if r['success']:
            print(f"  ✓ {r['name']}")
            if r['opening_hours']:
                if r['opening_hours'].get('is_24h'):
                    print(f"    24小時營業")
                else:
                    if r['opening_hours'].get('weekdays'):
                        print(f"    週一到週五: {r['opening_hours']['weekdays']}")
                    if r['opening_hours'].get('weekends'):
                        # 如果週六日與週一到週五不同，才顯示
                        if r['opening_hours'].get('weekdays') != r['opening_hours'].get('weekends'):
                            print(f"    週六日: {r['opening_hours']['weekends']}")
    
    if fail_count > 0:
        print("\n失敗案例：")
        for r in results:
            if not r['success']:
                print(f"  ✗ {r['name']}")
                if r.get('error'):
                    print(f"    錯誤: {r['error']}")

if __name__ == '__main__':
    main()
