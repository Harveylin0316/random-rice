#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
優化版：批量更新餐廳預算（使用並發處理和正則表達式）
"""

import json
import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# priceRangeId 對應關係
PRICE_RANGE_MAP = {
    '1': '100以下',      # 100元以內
    '2': '100-200',      # 100-200元
    '3': '200-500',      # 200-500元
    '4': '500-1000',     # 500-1000元
    '5': '1000-1500',    # 1000-1500元
    '6': '1500以上'      # 1500元以上
}

def create_session() -> requests.Session:
    """創建帶有重試機制的 Session"""
    session = requests.Session()
    
    # 設置重試策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # 設置 headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9',
    })
    
    return session

def scrape_budget_fast(session: requests.Session, url: str) -> Optional[str]:
    """
    快速爬取預算資訊（使用正則表達式）
    
    Args:
        session: requests Session 對象
        url: OpenRice 餐廳頁面 URL
        
    Returns:
        預算字串，例如 "200-500" 或 None
    """
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        
        # 使用正則表達式直接查找 priceRangeId（不解析整個 HTML）
        # 先嘗試在 pdhs-filter-tags-section 區域內查找
        section_match = re.search(
            r'<div[^>]*class=["\']pdhs-filter-tags-section["\'][^>]*>(.*?)</div>',
            response.text,
            re.DOTALL | re.IGNORECASE
        )
        
        if section_match:
            # 在該 section 中查找 priceRangeId
            section_html = section_match.group(1)
            price_match = re.search(r'priceRangeId=(\d+)', section_html)
        else:
            # 如果找不到 section，直接在全文中查找（備用方案）
            price_match = re.search(r'priceRangeId=(\d+)', response.text)
        
        if price_match:
            price_range_id = price_match.group(1)
            budget = PRICE_RANGE_MAP.get(price_range_id)
            return budget
        
        return None
        
    except Exception as e:
        return None

def process_restaurant(session: requests.Session, restaurant: Dict, index: int, total: int) -> Dict:
    """
    處理單個餐廳
    
    Returns:
        {
            'index': int,
            'name': str,
            'success': bool,
            'budget': str or None,
            'error': str or None
        }
    """
    name = restaurant.get('name', '未知餐廳')
    url = restaurant.get('url', '')
    
    result = {
        'index': index,
        'name': name,
        'success': False,
        'budget': None,
        'error': None
    }
    
    if not url:
        result['error'] = '無 URL'
        return result
    
    budget = scrape_budget_fast(session, url)
    
    if budget:
        result['success'] = True
        result['budget'] = budget
    else:
        result['error'] = '無法獲取預算'
    
    return result

def update_budgets_batch(
    json_file: str,
    batch_size: int = 50,
    start_index: int = 0,
    max_workers: int = 10,
    delay: float = 0.3
):
    """
    批量更新餐廳預算（優化版：並發處理）
    
    Args:
        json_file: JSON 檔案路徑
        batch_size: 每批處理的餐廳數量
        start_index: 從第幾間開始處理
        max_workers: 並發線程數（建議 5-10）
        delay: 每個請求之間的延遲（秒）
    """
    print("=" * 80)
    print("開始批量更新餐廳預算（優化版）")
    print("=" * 80)
    
    # 載入資料庫
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data['restaurants']
    
    # 找出所有需要更新預算的餐廳（可以選擇只更新 null 的，或全部更新）
    # 這裡選擇更新所有餐廳（可以根據需求修改）
    restaurants_to_update = [(i, r) for i, r in enumerate(restaurants) if r.get('url')]
    
    print(f"\n總餐廳數：{len(restaurants)} 間")
    print(f"有 URL 的餐廳：{len(restaurants_to_update)} 間")
    print(f"本次處理：從第 {start_index + 1} 間開始，處理 {batch_size} 間")
    print(f"並發線程數：{max_workers}")
    print(f"請求延遲：{delay} 秒\n")
    
    # 處理指定範圍的餐廳
    if start_index >= len(restaurants_to_update):
        print(f"⚠️  起始索引 {start_index} 超出範圍（總共 {len(restaurants_to_update)} 間餐廳）")
        return
    
    end_index = min(start_index + batch_size, len(restaurants_to_update))
    restaurants_to_process = restaurants_to_update[start_index:end_index]
    
    # 創建 Session（所有線程共享）
    session = create_session()
    
    updated_count = 0
    failed_count = 0
    
    print(f"開始處理 {len(restaurants_to_process)} 間餐廳...\n")
    start_time = time.time()
    
    # 使用線程池並發處理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任務
        future_to_restaurant = {
            executor.submit(
                process_restaurant,
                session,
                restaurant,
                start_index + idx + 1,
                len(restaurants_to_update)
            ): (original_idx, restaurant)
            for idx, (original_idx, restaurant) in enumerate(restaurants_to_process)
        }
        
        # 處理完成的任務
        completed = 0
        for future in as_completed(future_to_restaurant):
            original_idx, restaurant = future_to_restaurant[future]
            completed += 1
            
            try:
                result = future.result()
                
                if result['success']:
                    restaurants[original_idx]['budget'] = result['budget']
                    updated_count += 1
                    print(f"[{result['index']}/{len(restaurants_to_update)}] {result['name'][:50]} ... ✅ {result['budget']}")
                else:
                    failed_count += 1
                    print(f"[{result['index']}/{len(restaurants_to_update)}] {result['name'][:50]} ... ❌ {result['error']}")
                
                # 每處理 10 間保存一次
                if completed % 10 == 0:
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    print(f"  💾 已保存進度（{completed}/{len(restaurants_to_process)}，速度：{rate:.1f} 間/秒）")
                
                # 控制請求速率（避免過快）
                time.sleep(delay)
                
            except Exception as e:
                failed_count += 1
                print(f"[{completed}/{len(restaurants_to_process)}] 處理錯誤：{str(e)}")
    
    # 最終保存
    print("\n" + "=" * 80)
    print("保存更新後的資料庫...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("✅ 本批次處理完成！")
    print(f"\n統計：")
    print(f"  處理數量：{len(restaurants_to_process)} 間")
    print(f"  成功更新：{updated_count} 間")
    print(f"  失敗：{failed_count} 間")
    if len(restaurants_to_process) > 0:
        print(f"  成功率：{updated_count/len(restaurants_to_process)*100:.1f}%")
    print(f"  總耗時：{elapsed_time:.1f} 秒")
    print(f"  平均速度：{len(restaurants_to_process)/elapsed_time:.1f} 間/秒")
    print("=" * 80)
    
    # 提示下一批次
    if end_index < len(restaurants_to_update):
        print(f"\n💡 提示：還有 {len(restaurants_to_update) - end_index} 間餐廳待處理")
        print(f"   下次運行：python3 update_budgets_optimized.py --start {end_index}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="優化版批量更新餐廳預算")
    parser.add_argument('--batch-size', type=int, default=50, help='每批處理的餐廳數量（預設：50）')
    parser.add_argument('--start', type=int, default=0, help='從第幾間開始處理（預設：0）')
    parser.add_argument('--workers', type=int, default=10, help='並發線程數（預設：10）')
    parser.add_argument('--delay', type=float, default=0.3, help='每個請求之間的延遲（秒，預設：0.3）')
    
    args = parser.parse_args()
    
    update_budgets_batch(
        'restaurants_database.json',
        batch_size=args.batch_size,
        start_index=args.start,
        max_workers=args.workers,
        delay=args.delay
    )
