#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新餐廳的 dish 和 is_buffet 欄位
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
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.openrice.com/'
    })
    
    return session

def scrape_dish_from_openrice(session: requests.Session, url: str) -> Dict[str, any]:
    """
    從 OpenRice URL 爬取 dish 資訊（優化版）
    
    Args:
        session: requests.Session 對象（連接池，已包含重試機制）
        url: OpenRice 餐廳頁面 URL
        
    Returns:
        字典，包含：
        - dish: 所有 dish 列表
        - is_buffet: 是否包含「吃到飽」的布林值
    """
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找 <div class="pdhs-filter-tags-section">
        filter_section = soup.find('div', class_='pdhs-filter-tags-section')
        
        if not filter_section:
            return {"dish": [], "is_buffet": False}
        
        # 在該 section 中找到所有 <a> 標籤，其 href 包含 "restaurants/dish/"
        dish_links = filter_section.find_all('a', href=re.compile(r'restaurants/dish/'))
        
        dishes = []
        is_buffet = False
        
        for link in dish_links:
            text = link.get_text(strip=True)
            
            # 收集所有 dish 文字
            if text and text not in dishes:
                dishes.append(text)
            
            # 檢查文字是否包含「吃到飽」
            if '吃到飽' in text:
                is_buffet = True
        
        return {"dish": dishes, "is_buffet": is_buffet}
        
    except requests.exceptions.RequestException as e:
        return {"dish": [], "is_buffet": False}
    except Exception as e:
        return {"dish": [], "is_buffet": False}

def process_restaurant(session: requests.Session, restaurant: Dict, index: int, total: int) -> Dict:
    """
    處理單個餐廳
    
    Args:
        session: requests.Session 對象
        restaurant: 餐廳資料
        index: 當前索引
        total: 總數
        
    Returns:
        更新後的餐廳資料
    """
    restaurant_name = restaurant.get('name', 'Unknown')
    url = restaurant.get('url', '')
    
    # 如果沒有 URL，跳過
    if not url:
        with print_lock:
            print(f"[{index+1}/{total}] ⚠️  {restaurant_name}: 沒有 URL，跳過")
        return restaurant
    
    # 爬取 dish 資訊
    result = scrape_dish_from_openrice(session, url)
    
    # 更新餐廳資料
    restaurant['dish'] = result['dish']
    restaurant['is_buffet'] = result['is_buffet']
    
    # 輸出結果
    with print_lock:
        dish_count = len(result['dish'])
        buffet_status = "✅ 吃到飽" if result['is_buffet'] else "❌ 非吃到飽"
        print(f"[{index+1}/{total}] {buffet_status} | {restaurant_name}: {dish_count} 個 dish")
    
    return restaurant

def update_dish_batch(file_path: str, batch_size: int = 50, start_index: int = 0, workers: int = 10, delay: float = 0.1):
    """
    批量更新餐廳的 dish 和 is_buffet 欄位
    
    Args:
        file_path: 資料庫 JSON 檔案路徑
        batch_size: 每批處理的餐廳數量
        start_index: 起始索引（用於斷點續傳）
        workers: 並發線程數
        delay: 每個請求之間的延遲（秒）
    """
    # 讀取資料庫
    print(f"正在讀取資料庫: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data.get('restaurants', [])
    total = len(restaurants)
    
    print(f"資料庫中共有 {total} 間餐廳")
    
    # 檢查起始索引
    if start_index >= total:
        print(f"❌ 起始索引 {start_index} 超出範圍（總數: {total}）")
        return
    
    # 確定要處理的餐廳範圍
    end_index = min(start_index + batch_size, total)
    restaurants_to_process = restaurants[start_index:end_index]
    
    print(f"將處理第 {start_index+1} 到 {end_index} 間餐廳（共 {len(restaurants_to_process)} 間）")
    print(f"使用 {workers} 個並發線程，每個請求延遲 {delay} 秒")
    print("=" * 80)
    
    # 創建 Session（所有線程共享）
    session = create_session()
    
    # 使用線程池並發處理
    updated_restaurants = []
    success_count = 0
    error_count = 0
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # 提交所有任務
        future_to_restaurant = {
            executor.submit(
                process_restaurant,
                session,
                restaurant,
                start_index + i,
                total
            ): (restaurant, i)
            for i, restaurant in enumerate(restaurants_to_process)
        }
        
        # 收集結果
        for future in as_completed(future_to_restaurant):
            restaurant, i = future_to_restaurant[future]
            try:
                updated_restaurant = future.result()
                updated_restaurants.append((start_index + i, updated_restaurant))
                success_count += 1
                
                # 添加延遲以避免過於頻繁的請求
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                error_count += 1
                with print_lock:
                    print(f"❌ 處理 {restaurant.get('name', 'Unknown')} 時發生錯誤: {e}")
                # 即使出錯也保留原始資料
                updated_restaurants.append((start_index + i, restaurant))
    
    # 按索引排序
    updated_restaurants.sort(key=lambda x: x[0])
    
    # 更新資料庫
    for index, updated_restaurant in updated_restaurants:
        restaurants[index] = updated_restaurant
    
    # 保存資料庫
    print("\n" + "=" * 80)
    print("正在保存資料庫...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ 資料庫已保存")
    
    # 統計資訊
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 80)
    print("處理完成！")
    print(f"成功: {success_count} 間")
    print(f"錯誤: {error_count} 間")
    print(f"耗時: {elapsed_time:.2f} 秒")
    print(f"平均: {elapsed_time/len(restaurants_to_process):.2f} 秒/間")
    
    # 統計吃到飽餐廳數量
    buffet_count = sum(1 for _, r in updated_restaurants if r.get('is_buffet', False))
    print(f"吃到飽餐廳: {buffet_count} 間")
    print("=" * 80)

if __name__ == "__main__":
    import sys
    
    file_path = "restaurants_database.json"
    batch_size = 50
    start_index = 0
    workers = 10
    delay = 0.1
    
    # 解析命令行參數
    if len(sys.argv) > 1:
        batch_size = int(sys.argv[1])
    if len(sys.argv) > 2:
        start_index = int(sys.argv[2])
    if len(sys.argv) > 3:
        workers = int(sys.argv[3])
    if len(sys.argv) > 4:
        delay = float(sys.argv[4])
    
    print("=" * 80)
    print("批量更新餐廳 dish 和 is_buffet 欄位")
    print("=" * 80)
    print(f"檔案: {file_path}")
    print(f"批次大小: {batch_size}")
    print(f"起始索引: {start_index}")
    print(f"並發線程: {workers}")
    print(f"請求延遲: {delay} 秒")
    print("=" * 80)
    print()
    
    update_dish_batch(file_path, batch_size, start_index, workers, delay)
