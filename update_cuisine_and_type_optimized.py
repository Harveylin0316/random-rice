#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
優化版：批量更新餐廳的料理風格和餐廳類型
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
from typing import Dict, List, Optional, Tuple

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
        'Upgrade-Insecure-Requests': '1'
    })
    
    return session

def scrape_cuisine_and_type_from_openrice(session: requests.Session, url: str) -> Tuple[List[str], List[str]]:
    """
    從 OpenRice URL 同時抓取料理風格和餐廳類型（優化版）
    使用正則表達式快速提取，比 BeautifulSoup 快很多
    
    Args:
        session: requests.Session 對象（連接池，已包含重試機制）
        url: OpenRice 餐廳頁面 URL
        
    Returns:
        tuple: (料理風格列表, 餐廳類型列表)
    """
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        html = response.text
        
        cuisines = []
        types = []
        
        # 先找到 pdhs-filter-tags-section，縮小搜尋範圍
        section_match = re.search(
            r'<div[^>]*class=["\']pdhs-filter-tags-section["\'][^>]*>(.*?)</div>',
            html,
            re.DOTALL | re.IGNORECASE
        )
        
        if not section_match:
            return [], []
        
        section_html = section_match.group(1)
        
        # 匹配包含 cuisine 的 <a> 標籤
        # 格式：<a ... href="...cuisine..." ...>文字</a>
        # 需要處理註釋、換行、嵌套標籤等情況
        cuisine_pattern = r'<a[^>]*href=["\'][^"\']*cuisine[^"\']*["\'][^>]*>(.*?)</a>'
        for match in re.finditer(cuisine_pattern, section_html, re.IGNORECASE | re.DOTALL):
            text_html = match.group(1)
            # 移除 HTML 標籤和註釋
            text_clean = re.sub(r'<!--.*?-->', '', text_html, flags=re.DOTALL)  # 移除註釋
            text_clean = re.sub(r'<[^>]+>', '', text_clean)  # 移除 HTML 標籤
            text_clean = re.sub(r'\s+', ' ', text_clean).strip()  # 正規化空白
            if text_clean:
                cuisines.append(text_clean)
        
        # 匹配包含 type 的 <a> 標籤
        type_pattern = r'<a[^>]*href=["\'][^"\']*type[^"\']*["\'][^>]*>(.*?)</a>'
        for match in re.finditer(type_pattern, section_html, re.IGNORECASE | re.DOTALL):
            text_html = match.group(1)
            # 移除 HTML 標籤和註釋
            text_clean = re.sub(r'<!--.*?-->', '', text_html, flags=re.DOTALL)  # 移除註釋
            text_clean = re.sub(r'<[^>]+>', '', text_clean)  # 移除 HTML 標籤
            text_clean = re.sub(r'\s+', ' ', text_clean).strip()  # 正規化空白
            if text_clean:
                types.append(text_clean)
        
        # 去重並返回
        return list(set(cuisines)), list(set(types))
        
    except Exception:
        # Session 已經有重試機制，這裡直接返回空列表
        return [], []

def process_restaurant(session: requests.Session, restaurant: Dict, index: int, total: int) -> Tuple[int, Dict, List[str], List[str]]:
    """
    處理單個餐廳
    
    Returns:
        tuple: (索引, 餐廳資料, 料理風格列表, 餐廳類型列表)
    """
    name = restaurant.get('name', '未知')
    url = restaurant.get('url', '')
    
    if not url:
        return index, restaurant, [], []
    
    cuisines, types = scrape_cuisine_and_type_from_openrice(session, url)
    
    return index, restaurant, cuisines, types

def update_cuisine_and_type_optimized(
    json_file: str = 'restaurants_database.json',
    batch_size: int = 50,
    start_index: int = 0,
    workers: int = 10,
    delay: float = 0.2
):
    """
    優化版批量更新餐廳的料理風格和餐廳類型
    
    Args:
        json_file: 資料庫 JSON 檔案路徑
        batch_size: 每批處理的餐廳數量
        start_index: 起始索引
        workers: 並發線程數
        delay: 每個請求之間的延遲（秒）
    """
    print("=" * 80)
    print("開始批量更新餐廳的料理風格和餐廳類型（優化版）")
    print("=" * 80)
    
    # 載入資料庫
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data['restaurants']
    total = len(restaurants)
    
    # 過濾出有 URL 的餐廳
    restaurants_to_process = [
        (i, r) for i, r in enumerate(restaurants)
        if r.get('url') and i >= start_index
    ]
    
    if not restaurants_to_process:
        print(f"❌ 沒有需要處理的餐廳（起始索引 {start_index} 超出範圍）")
        return
    
    # 限制批次大小
    if batch_size > 0:
        restaurants_to_process = restaurants_to_process[:batch_size]
    
    total_to_process = len(restaurants_to_process)
    print(f"\n總餐廳數：{total} 間")
    print(f"需要處理：{total_to_process} 間（從索引 {start_index} 開始）")
    print(f"並發線程數：{workers}")
    print(f"請求延遲：{delay} 秒")
    print()
    
    # 統計
    updated_cuisine_count = 0
    updated_type_count = 0
    success_count = 0
    error_count = 0
    
    # 使用優化的 Session（包含重試機制和連接池）
    session = create_session()
    
    start_time = time.time()
    
    try:
        # 使用線程池並發處理
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # 提交所有任務
            future_to_restaurant = {
                executor.submit(process_restaurant, session, restaurant, index, total): (index, restaurant)
                for index, restaurant in restaurants_to_process
            }
            
            # 處理完成的任務
            completed = 0
            for future in as_completed(future_to_restaurant):
                completed += 1
                index, restaurant = future_to_restaurant[future]
                
                try:
                    idx, rest, cuisines, types = future.result()
                    
                    # 更新資料庫
                    with update_lock:
                        if cuisines:
                            restaurants[idx]['cuisine_style'] = cuisines
                            updated_cuisine_count += 1
                        if types:
                            restaurants[idx]['type'] = types
                            updated_type_count += 1
                        
                        if cuisines or types:
                            success_count += 1
                        else:
                            error_count += 1
                    
                    # 顯示進度
                    with print_lock:
                        progress = (completed / total_to_process) * 100
                        elapsed = time.time() - start_time
                        avg_time = elapsed / completed if completed > 0 else 0
                        remaining = (total_to_process - completed) * avg_time
                        
                        status = "✅" if (cuisines or types) else "⚠️"
                        print(f"[{completed}/{total_to_process}] ({progress:.1f}%) "
                              f"{status} {rest.get('name', '未知')[:30]:<30} "
                              f"料理風格:{len(cuisines)} 類型:{len(types)} "
                              f"剩餘時間: {remaining/60:.1f}分鐘")
                        
                        if cuisines:
                            print(f"    料理風格: {', '.join(cuisines)}")
                        if types:
                            print(f"    餐廳類型: {', '.join(types)}")
                
                except Exception as e:
                    error_count += 1
                    with print_lock:
                        print(f"[{completed}/{total_to_process}] ❌ {restaurant.get('name', '未知')} - 錯誤: {e}")
                
                # 控制請求頻率
                time.sleep(delay)
        
        # 保存更新後的資料庫
        print("\n" + "=" * 80)
        print("保存更新後的資料庫...")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 統計結果
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 80)
        print("✅ 處理完成！")
        print(f"\n統計：")
        print(f"  總處理數：{total_to_process} 間")
        print(f"  成功更新料理風格：{updated_cuisine_count} 間")
        print(f"  成功更新餐廳類型：{updated_type_count} 間")
        print(f"  成功：{success_count} 間")
        print(f"  失敗：{error_count} 間")
        print(f"  耗時：{elapsed_time/60:.2f} 分鐘")
        print(f"  平均速度：{total_to_process/elapsed_time*60:.1f} 間/分鐘")
        print("=" * 80)
        
    finally:
        session.close()

if __name__ == "__main__":
    import sys
    
    # 解析命令行參數
    batch_size = 0  # 0 表示處理所有
    start_index = 0
    workers = 10
    delay = 0.2
    
    if len(sys.argv) > 1:
        batch_size = int(sys.argv[1])
    if len(sys.argv) > 2:
        start_index = int(sys.argv[2])
    if len(sys.argv) > 3:
        workers = int(sys.argv[3])
    if len(sys.argv) > 4:
        delay = float(sys.argv[4])
    
    update_cuisine_and_type_optimized(
        batch_size=batch_size,
        start_index=start_index,
        workers=workers,
        delay=delay
    )
