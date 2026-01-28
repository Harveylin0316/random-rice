#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新餐廳的 opening_hours 欄位
使用並發處理、連接池、重試機制等優化技術
"""

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

# 全局變數
print_lock = Lock()
update_lock = Lock()

def create_session() -> requests.Session:
    """創建帶有重試機制和連接池的 Session"""
    session = requests.Session()
    
    # 設置重試策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # 設置 headers
    # 注意：不設置 Accept-Encoding，讓 requests 自動處理壓縮（包括 Brotli）
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.openrice.com/'
    })
    
    return session

def scrape_opening_hours_from_openrice(session: requests.Session, url: str) -> Dict:
    """
    從 OpenRice URL 爬取餐廳營業時間（優化版 - 使用 HTML class）
    
    Args:
        session: requests.Session 對象（連接池，已包含重試機制）
        url: OpenRice 餐廳頁面 URL
        
    Returns:
        字典，包含：
        - success: 是否成功
        - opening_hours: 營業時間資料
    """
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        opening_hours = {}
        
        # 方法1: 使用 HTML class 結構解析（最準確）
        # 嘗試多種方式查找 opening-hours-list
        opening_hours_list = soup.select_one('.opening-hours-list')
        if not opening_hours_list:
            opening_hours_list = soup.find(class_='opening-hours-list')
        if not opening_hours_list:
            opening_hours_list = soup.find(class_=lambda x: x and 'opening-hours-list' in str(x))
        
        if opening_hours_list:
            # 查找所有 opening-hours-day 元素
            day_elements = opening_hours_list.find_all(class_='opening-hours-day')
            # 如果找不到，嘗試使用 CSS selector
            if not day_elements:
                day_elements = opening_hours_list.select('.opening-hours-day')
            
            # 使用週一到週日七個欄位
            days_times = {
                'monday': [],
                'tuesday': [],
                'wednesday': [],
                'thursday': [],
                'friday': [],
                'saturday': [],
                'sunday': []
            }
            
            for day_elem in day_elements:
                date_elem = day_elem.find(class_='opening-hours-date')
                if not date_elem:
                    date_elem = day_elem.select_one('.opening-hours-date')
                time_elem = day_elem.find(class_='opening-hours-time')
                if not time_elem:
                    time_elem = day_elem.select_one('.opening-hours-time')
                
                if date_elem and time_elem:
                    date_text = date_elem.get_text(strip=True)
                    
                    # 優化：檢查 time_elem 內部是否有多個時間 div
                    # 有些餐廳在同一天有多個營業時段（如：11:00-14:00 和 17:00-19:30）
                    time_divs = time_elem.find_all('div')
                    time_texts = []
                    
                    if len(time_divs) > 1:
                        # 有多個 div，分別提取每個 div 的文字
                        for div in time_divs:
                            div_text = div.get_text(strip=True)
                            if div_text and div_text not in ['', ' ']:
                                time_texts.append(div_text)
                    else:
                        # 只有一個 div 或沒有 div，使用整個 time_elem 的文字
                        time_text = time_elem.get_text(strip=True)
                        time_texts.append(time_text)
                    
                    # 如果沒有找到任何文字，跳過
                    if not time_texts:
                        continue
                    
                    # 處理每個時間文字
                    day_time_ranges = []
                    has_rest = False
                    
                    for time_text in time_texts:
                        # 檢查是否有「全日休息」
                        if '全日休息' in time_text or ('休息' in time_text and '營業' not in time_text and not re.search(r'\d{1,2}:\d{2}', time_text)):
                            has_rest = True
                            # 如果是休息日，直接跳出循環，不處理任何時間範圍
                            break
                        
                        # 解析時間範圍（可能有多個）
                        time_matches = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})', time_text)
                        for time_match in time_matches:
                            start_h, start_m, end_h, end_m = time_match
                            time_range = f"{start_h}:{start_m}-{end_h}:{end_m}"
                            if time_range not in day_time_ranges:
                                day_time_ranges.append(time_range)
                    
                    # 如果這一天是休息日且沒有時間範圍，跳過（不添加到任何列表）
                    if has_rest and not day_time_ranges:
                        continue
                    
                    # 如果找到時間範圍，處理它們
                    if day_time_ranges:
                        # 解析日期文字，判斷對應到哪些天
                        target_days = []
                        
                        # 檢查具體的日期
                        if '星期一' in date_text or ('一' in date_text and '二' not in date_text and '三' not in date_text and '四' not in date_text and '五' not in date_text and '六' not in date_text and '日' not in date_text):
                            target_days.append('monday')
                        if '星期二' in date_text or ('二' in date_text and '一' not in date_text and '三' not in date_text and '四' not in date_text and '五' not in date_text and '六' not in date_text and '日' not in date_text):
                            target_days.append('tuesday')
                        if '星期三' in date_text or ('三' in date_text and '一' not in date_text and '二' not in date_text and '四' not in date_text and '五' not in date_text and '六' not in date_text and '日' not in date_text):
                            target_days.append('wednesday')
                        if '星期四' in date_text or ('四' in date_text and '一' not in date_text and '二' not in date_text and '三' not in date_text and '五' not in date_text and '六' not in date_text and '日' not in date_text):
                            target_days.append('thursday')
                        if '星期五' in date_text or ('五' in date_text and '一' not in date_text and '二' not in date_text and '三' not in date_text and '四' not in date_text and '六' not in date_text and '日' not in date_text):
                            target_days.append('friday')
                        if '星期六' in date_text or ('六' in date_text and '一' not in date_text and '二' not in date_text and '三' not in date_text and '四' not in date_text and '五' not in date_text and '日' not in date_text):
                            target_days.append('saturday')
                        if '星期日' in date_text or '星期天' in date_text or ('日' in date_text and '一' not in date_text and '二' not in date_text and '三' not in date_text and '四' not in date_text and '五' not in date_text and '六' not in date_text):
                            target_days.append('sunday')
                        
                        # 處理範圍（如「星期一至五」、「星期二至五」等）
                        if '一至五' in date_text or '一到五' in date_text:
                            target_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
                        elif '二至五' in date_text or '二到五' in date_text:
                            target_days = ['tuesday', 'wednesday', 'thursday', 'friday']
                        elif '三至五' in date_text or '三到五' in date_text:
                            target_days = ['wednesday', 'thursday', 'friday']
                        elif '一至三' in date_text or '一到三' in date_text:
                            target_days = ['monday', 'tuesday', 'wednesday']
                        elif '一至四' in date_text or '一到四' in date_text:
                            target_days = ['monday', 'tuesday', 'wednesday', 'thursday']
                        elif '六至日' in date_text or '六到日' in date_text or '六日' in date_text or '星期六至日' in date_text:
                            target_days = ['saturday', 'sunday']
                        elif '一至日' in date_text or '一到日' in date_text:
                            target_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                        
                        # 如果沒有找到具體的日期，嘗試從文字中推斷
                        if not target_days:
                            # 如果包含「一」到「五」，且不包含「六」「日」，可能是週一至五
                            if ('一' in date_text or '二' in date_text or '三' in date_text or '四' in date_text or '五' in date_text) and '六' not in date_text and '日' not in date_text:
                                # 預設為週一至五（如果沒有明確標示）
                                target_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
                            # 如果包含「六」或「日」，且不包含「一」到「五」，可能是週六日
                            elif ('六' in date_text or '日' in date_text) and '一' not in date_text and '二' not in date_text and '三' not in date_text and '四' not in date_text and '五' not in date_text:
                                target_days = ['saturday', 'sunday']
                        
                        # 將時間範圍添加到對應的日期
                        for day in target_days:
                            for time_range in day_time_ranges:
                                if time_range not in days_times[day]:
                                    days_times[day].append(time_range)
            
            # 檢查是否有任何一天有營業時間
            has_any_time = any(days_times[day] for day in days_times)
            
            if has_any_time:
                # 將每天的營業時間添加到 opening_hours
                for day in days_times:
                    opening_hours[day] = days_times[day]
                
                opening_hours['is_24h'] = False
                return {
                    'success': True,
                    'opening_hours': opening_hours
                }
        
        # 方法2: 如果 HTML class 方法失敗，回退到文字解析方法
        all_text = soup.get_text()
        
        # 優化：先清理文字，移除多餘的空白和換行
        all_text = re.sub(r'\s+', ' ', all_text)
        
        # 檢查是否為 24 小時營業
        is_24h = False
        if re.search(r'24[小時時]|全天|全天候|24\s*小時', all_text, re.IGNORECASE):
            is_24h = True
            opening_hours['is_24h'] = True
            return {
                'success': True,
                'opening_hours': opening_hours
            }
        
        # 優化：查找包含營業時間的區塊（通常在特定 HTML 元素中）
        # 優先查找包含「營業時間」、「營業」、「Opening Hours」等關鍵字的區塊
        hours_sections = []
        for elem in soup.find_all(['div', 'section', 'dl', 'ul', 'li', 'p', 'span', 'td']):
            elem_text = elem.get_text()
            if any(keyword in elem_text for keyword in ['營業時間', '營業', 'Opening', 'Hours', '時間']):
                if re.search(r'\d{1,2}:\d{2}', elem_text):
                    hours_sections.append(elem_text)
        
        # 如果找到相關區塊，優先使用這些區塊的文字
        if hours_sections:
            all_text = ' '.join(hours_sections)
        
        # 方法1: 優先查找「星期一至五」和「星期六至日」分別的格式
        weekday_patterns = [
            r'星期[一二三四五]+[至到][一二三四五]*',  # 匹配「星期二至五」或「星期一至五」
            r'[週周]?[一二三四五]+[至到][週周]?[一二三四五]*',  # 匹配「星期一至五」或「週一至五」
            r'[週周][一五][至到][週周]?[一五]',  # 匹配「週一至五」
            r'週?[一五][至到]週?[一五]',  # 匹配「週一至五」或「一至五」
        ]
        weekend_patterns = [
            r'星期[六日]+[至到][六日]*',  # 匹配「星期六至日」
            r'[週周]?[六日]+[至到][週周]?[六日]*',  # 匹配「星期六至日」或「週六至日」
            r'[週周][六日][至到][週周]?[六日]',  # 匹配「週六至日」
            r'週?[六日][至到]週?[六日]',  # 匹配「週六至日」或「六至日」
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
                match_start = weekday_match.end()
                
                # 如果也有週六日的匹配，則週一至五的時間範圍應該在兩者之間
                if weekend_match:
                    context_end = weekend_match.start()
                else:
                    context_end = min(len(all_text), match_start + 200)
                
                context = all_text[match_start:context_end]
                
                # 檢查是否有「全日休息」（只檢查前50字元，避免誤判）
                # 注意：不要只檢查「休息」，因為可能在其他地方出現
                if re.search(r'全日休息|公休', context[:50]):
                    # 如果週一至五全日休息，則不設置 weekdays
                    pass
                else:
                    # 優化：擴大搜索範圍，並改進時間格式匹配
                    # 支持更多時間格式：11:30-14:00, 11:30~14:00, 11:30至14:00
                    time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至到]\s*(\d{1,2}):(\d{2})', context)
                    # 如果沒找到，嘗試更寬鬆的格式
                    if not time_ranges:
                        time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至到]\s*(\d{1,2}):(\d{2})', all_text[match_start:match_start+300])
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
                        if unique_ranges:
                            opening_hours['weekdays'] = unique_ranges
            
            if weekend_match:
                # 提取週六至日的時間範圍
                match_start = weekend_match.end()
                match_end = min(len(all_text), match_start + 200)
                
                context = all_text[match_start:match_end]
                
                # 檢查是否有「全日休息」（在匹配的文字中）
                match_text = weekend_match.group(0)
                if '休息' in match_text or '公休' in match_text:
                    # 如果匹配的文字本身就包含休息，跳過
                    pass
                elif re.search(r'全日休息|公休', context[:50]):  # 只檢查前50字元，移除「休息」避免誤判
                    # 如果週六日全日休息，則不設置 weekends
                    pass
                else:
                    # 優化：擴大搜索範圍，並改進時間格式匹配
                    time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至到]\s*(\d{1,2}):(\d{2})', context)
                    # 如果沒找到，嘗試更寬鬆的格式
                    if not time_ranges:
                        time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至到]\s*(\d{1,2}):(\d{2})', all_text[match_start:match_start+300])
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
                        if unique_ranges:
                            opening_hours['weekends'] = unique_ranges
            
            # 如果只找到其中一個，另一個使用相同的值
            if 'weekdays' in opening_hours and 'weekends' not in opening_hours:
                opening_hours['weekends'] = opening_hours['weekdays']
            elif 'weekends' in opening_hours and 'weekdays' not in opening_hours:
                opening_hours['weekdays'] = opening_hours['weekends']
            
            # 如果找到任何營業時間，返回成功
            if 'weekdays' in opening_hours or 'weekends' in opening_hours:
                opening_hours['is_24h'] = False
                # 確保返回成功
                result = {
                    'success': True,
                    'opening_hours': opening_hours
                }
                return result
        
        # 方法2: 查找「星期一至日」或「週一至週日」格式（所有天相同）
        # 只有在方法1沒有找到時才執行
        if not opening_hours:
            all_days_patterns = [
                r'[週周]?[一二三四五六日]+[至到][一二三四五六日]*\s*([^\n]{0,200})',
                r'[週周]?[一二三四五六日]+[至到][日]?\s*([^\n]{0,200})',
            ]
            
            all_days_match = None
            for pattern in all_days_patterns:
                all_days_match = re.search(pattern, all_text)
                if all_days_match:
                    match_text = all_days_match.group(0)
                    # 排除已經被方法1處理的格式（「一至五」、「六至日」、「二至五」等）
                    # 只處理「一至日」、「一至週日」、「週一至日」等完整格式
                    if ('一至日' in match_text or '一至週日' in match_text or 
                        ('週一至日' in match_text or '週一至週日' in match_text)):
                        break
                    else:
                        all_days_match = None
            
            if all_days_match:
                time_str = all_days_match.group(1).strip()
                full_context_start = max(0, all_days_match.start() - 50)
                full_context_end = min(len(all_text), all_days_match.end() + 200)
                full_context = all_text[full_context_start:full_context_end]
                
                time_ranges = re.findall(r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})', full_context)
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
                    opening_hours['weekends'] = unique_ranges
                    opening_hours['is_24h'] = False
                    return {
                        'success': True,
                        'opening_hours': opening_hours
                    }
        
        # 方法3: 如果找到時間範圍但沒有找到週幾，嘗試推斷（只有在前面方法都沒找到時才執行）
        if not opening_hours:
            time_pattern = r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})'
            time_matches = re.findall(time_pattern, all_text)
            
            if time_matches and len(time_matches) >= 2:
                time_ranges = []
                for match in time_matches[:2]:
                    start_hour, start_min, end_hour, end_min = match
                    time_ranges.append(f"{start_hour}:{start_min}-{end_hour}:{end_min}")
                
                if len(time_ranges) == 2:
                    opening_hours['weekdays'] = time_ranges
                    opening_hours['weekends'] = time_ranges
                    opening_hours['is_24h'] = False
                    return {
                        'success': True,
                        'opening_hours': opening_hours
                    }
        
        # 如果都沒找到，返回失敗
        return {
            'success': False,
            'opening_hours': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'opening_hours': None,
            'error': str(e)
        }

def update_restaurant_opening_hours(session: requests.Session, restaurant: Dict, index: int, total: int) -> Dict:
    """
    更新單個餐廳的 opening_hours 欄位
    
    Args:
        session: requests.Session 對象
        restaurant: 餐廳字典
        index: 當前索引
        total: 總數
        
    Returns:
        更新結果字典
    """
    restaurant_name = restaurant.get('name', 'Unknown')
    url = restaurant.get('url', '')
    
    if not url:
        with print_lock:
            print(f"[{index}/{total}] ⚠️  跳過：{restaurant_name} (無 URL)")
        return {
            'index': index,
            'name': restaurant_name,
            'success': False,
            'reason': '無 URL'
        }
    
    # 爬取營業時間
    result = scrape_opening_hours_from_openrice(session, url)
    
    if result['success']:
        opening_hours = result['opening_hours']
        with print_lock:
            if opening_hours.get('is_24h'):
                print(f"[{index}/{total}] ✓ {restaurant_name} - 24小時營業")
            elif opening_hours.get('weekdays'):
                weekdays_str = ', '.join(opening_hours['weekdays'])
                if opening_hours.get('weekends') and opening_hours['weekends'] != opening_hours['weekdays']:
                    weekends_str = ', '.join(opening_hours['weekends'])
                    print(f"[{index}/{total}] ✓ {restaurant_name} - 週一至五: {weekdays_str}; 週六日: {weekends_str}")
                else:
                    print(f"[{index}/{total}] ✓ {restaurant_name} - {weekdays_str}")
        
        return {
            'index': index,
            'name': restaurant_name,
            'success': True,
            'opening_hours': opening_hours
        }
    else:
        error_msg = result.get('error', '無法找到營業時間')
        with print_lock:
            print(f"[{index}/{total}] ✗ {restaurant_name} - {error_msg}")
        return {
            'index': index,
            'name': restaurant_name,
            'success': False,
            'reason': error_msg
        }

def main():
    # 讀取資料庫
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
    
    # 統計需要更新的餐廳（沒有 opening_hours 或需要更新的）
    restaurants_to_update = []
    for i, restaurant in enumerate(restaurants):
        if 'opening_hours' not in restaurant or restaurant.get('opening_hours') is None:
            restaurants_to_update.append((i, restaurant))
    
    total_to_update = len(restaurants_to_update)
    print(f"\n需要更新的餐廳：{total_to_update} 間")
    
    if total_to_update == 0:
        print("所有餐廳都已更新，無需處理")
        return
    
    # 確認是否繼續
    print("\n開始批量更新營業時間...")
    print("="*70)
    
    # 創建 Session（每個線程共享）
    session = create_session()
    
    # 統計變數
    success_count = 0
    fail_count = 0
    updated_count = 0
    failed_restaurants = []  # 記錄失敗的餐廳
    
    # 使用線程池並發處理
    max_workers = 5  # 並發數，避免請求過快
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任務
        future_to_restaurant = {
            executor.submit(update_restaurant_opening_hours, session, restaurant, idx+1, total_to_update): (idx, restaurant)
            for idx, restaurant in restaurants_to_update
        }
        
        # 處理完成的任务
        for future in as_completed(future_to_restaurant):
            idx, restaurant = future_to_restaurant[future]
            try:
                result = future.result()
                
                if result['success']:
                    success_count += 1
                    # 更新資料庫
                    with update_lock:
                        restaurants[idx]['opening_hours'] = result['opening_hours']
                        updated_count += 1
                else:
                    fail_count += 1
                    # 記錄失敗的餐廳
                    failed_restaurants.append({
                        'name': result['name'],
                        'url': restaurant.get('url', ''),
                        'reason': result.get('reason', '未知錯誤')
                    })
                    
            except Exception as e:
                fail_count += 1
                with print_lock:
                    print(f"處理 {restaurant.get('name', 'Unknown')} 時發生錯誤：{str(e)}")
            
            # 顯示進度
            completed = success_count + fail_count
            if completed % 10 == 0 or completed == total_to_update:
                elapsed = time.time() - start_time
                avg_time = elapsed / completed if completed > 0 else 0
                remaining = (total_to_update - completed) * avg_time
                with print_lock:
                    print(f"\n進度：{completed}/{total_to_update} ({completed/total_to_update*100:.1f}%)")
                    print(f"成功：{success_count} | 失敗：{fail_count}")
                    if remaining > 0:
                        print(f"預估剩餘時間：{remaining/60:.1f} 分鐘\n")
    
    # 保存更新後的資料庫
    print("\n" + "="*70)
    print("保存更新後的資料庫...")
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print("✓ 資料庫已保存")
    
    # 顯示總結
    elapsed_time = time.time() - start_time
    print("\n" + "="*70)
    print("更新總結")
    print("="*70)
    print(f"總數：{total_to_update} 間")
    print(f"成功：{success_count} 間 ({success_count/total_to_update*100:.1f}%)")
    print(f"失敗：{fail_count} 間 ({fail_count/total_to_update*100:.1f}%)")
    print(f"已更新：{updated_count} 間")
    print(f"耗時：{elapsed_time/60:.2f} 分鐘")
    print(f"平均速度：{total_to_update/elapsed_time*60:.1f} 間/分鐘")
    
    # 顯示失敗的餐廳列表
    if failed_restaurants:
        print("\n" + "="*70)
        print("失敗的餐廳列表：")
        print("="*70)
        for i, failed in enumerate(failed_restaurants, 1):
            print(f"{i}. {failed['name']}")
            print(f"   URL: {failed['url']}")
            print(f"   原因: {failed['reason']}")
            print()
    
    print("="*70)

if __name__ == '__main__':
    main()
