#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新餐廳預算（分批處理，避免一次處理太多）
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Optional

def scrape_price_from_openrice(url: str) -> Optional[str]:
    """從 OpenRice URL 爬取餐廳價格資訊"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.openrice.com/',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        all_text = soup.get_text()
        
        # 檢查是否已結業
        if any(keyword in all_text for keyword in ['已結業', '已歇業', '已停業']):
            return None
        
        # 優先查找 |NT$XXX-XXX| 範圍格式
        pipe_range_match = re.search(r'\|NT\$(\d+)\s*[-~至]\s*NT\$(\d+)\|', all_text)
        if not pipe_range_match:
            pipe_range_match = re.search(r'\|NT\$(\d+)\s*[-~至]\s*(\d+)\|', all_text)
        if pipe_range_match:
            min_price = int(pipe_range_match.group(1))
            max_price = int(pipe_range_match.group(2))
            return convert_to_budget_range(min_price, max_price)
        
        # 查找 |NT$XXX以上| 格式
        pipe_above_match = re.search(r'\|NT\$(\d+)以上\|', all_text)
        if pipe_above_match:
            price_num = int(pipe_above_match.group(1))
            return convert_to_budget_range(price_num, price_num * 2)
        
        # 查找 |NT$XXX| 單一價格格式
        pipe_single_match = re.search(r'\|NT\$(\d+)\|', all_text)
        if pipe_single_match:
            price_num = int(pipe_single_match.group(1))
            return convert_to_budget_range(price_num, price_num * 1.5)
        
        # 查找 NT$XXX-XXX 格式
        nt_range_match = re.search(r'NT\$(\d+)\s*[-~至]\s*NT\$(\d+)', all_text)
        if not nt_range_match:
            nt_range_match = re.search(r'NT\$(\d+)\s*[-~至]\s*(\d+)', all_text)
        if nt_range_match:
            min_price = int(nt_range_match.group(1))
            max_price = int(nt_range_match.group(2))
            return convert_to_budget_range(min_price, max_price)
        
        # 查找其他價格格式
        price_patterns = [
            r'人均[消費]*[：:]?\s*[\$NT]*\s*(\d+)\s*[-~至]\s*[\$NT]*\s*(\d+)',
            r'平均[消費]*[：:]?\s*[\$NT]*\s*(\d+)\s*[-~至]\s*[\$NT]*\s*(\d+)',
            r'消費[：:]?\s*[\$NT]*\s*(\d+)\s*[-~至]\s*[\$NT]*\s*(\d+)',
            r'(\d+)\s*[-~至]\s*(\d+)\s*[元]*',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, all_text)
            if match:
                min_price = int(match.group(1))
                max_price = int(match.group(2)) if len(match.groups()) > 1 else int(min_price * 1.5)
                return convert_to_budget_range(min_price, max_price)
        
        return None
        
    except Exception as e:
        return None

def convert_to_budget_range(min_price: int, max_price: int) -> str:
    """將價格轉換為預算區間格式"""
    avg_price = (min_price + max_price) / 2
    
    if avg_price < 200:
        return "200以下"
    elif avg_price < 400:
        return "200-400"
    elif avg_price < 800:
        return "500-800"
    elif avg_price < 1500:
        return "1000-1500"
    elif avg_price < 2000:
        return "1500-2000"
    else:
        return "2000以上"

def update_budgets_batch(file_path: str, batch_size: int = 50, start_index: int = 0):
    """
    批量更新餐廳預算
    """
    print("=" * 80)
    print("開始批量更新餐廳預算...")
    print("=" * 80)
    
    # 載入資料庫
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 找出所有沒有預算的餐廳
    no_budget_restaurants = [(i, r) for i, r in enumerate(data['restaurants']) if not r.get('budget')]
    
    print(f"\n總共無預算餐廳：{len(no_budget_restaurants)} 間")
    print(f"本次處理：從第 {start_index + 1} 間開始，處理 {batch_size} 間\n")
    
    # 處理指定範圍的餐廳
    end_index = min(start_index + batch_size, len(no_budget_restaurants))
    restaurants_to_process = no_budget_restaurants[start_index:end_index]
    
    updated_count = 0
    failed_count = 0
    
    for idx, (original_idx, restaurant) in enumerate(restaurants_to_process, 1):
        name = restaurant.get('name', '未知餐廳')
        url = restaurant.get('url', '')
        
        current_num = start_index + idx
        print(f"[{current_num}/{len(no_budget_restaurants)}] {name[:50]}")
        
        if not url:
            print(f"  ❌ 無 URL，跳過")
            failed_count += 1
            continue
        
        # 爬取價格
        budget = scrape_price_from_openrice(url)
        
        if budget:
            data['restaurants'][original_idx]['budget'] = budget
            print(f"  ✅ {budget}")
            updated_count += 1
        else:
            print(f"  ❌ 未找到價格")
            failed_count += 1
        
        # 每處理 10 間保存一次
        if idx % 10 == 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  💾 已保存進度")
        
        # 避免請求過快
        time.sleep(0.8)
    
    # 最終保存
    print("\n" + "=" * 80)
    print("保存更新後的資料庫...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("✅ 本批次處理完成！")
    print(f"\n統計：")
    print(f"  處理數量：{len(restaurants_to_process)} 間")
    print(f"  成功更新：{updated_count} 間")
    print(f"  失敗：{failed_count} 間")
    if len(restaurants_to_process) > 0:
        print(f"  成功率：{updated_count/len(restaurants_to_process)*100:.1f}%")
    print("=" * 80)
    
    # 提示下一批次
    if end_index < len(no_budget_restaurants):
        print(f"\n💡 提示：還有 {len(no_budget_restaurants) - end_index} 間餐廳待處理")
        print(f"   下次運行：python3 update_budgets_batch.py --start {end_index}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="批量更新餐廳預算")
    parser.add_argument('--batch-size', type=int, default=50, help='每批處理的餐廳數量（預設：50）')
    parser.add_argument('--start', type=int, default=0, help='從第幾間開始處理（預設：0）')
    
    args = parser.parse_args()
    
    update_budgets_batch(
        'restaurants_database.json',
        batch_size=args.batch_size,
        start_index=args.start
    )
