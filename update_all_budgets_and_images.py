#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新所有餐廳的預算和照片
1. 從 OpenRice 爬取價格資訊
2. 從 OpenRice 爬取照片
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Optional, Dict

def scrape_price_from_openrice(url: str) -> Optional[str]:
    """
    從 OpenRice URL 爬取餐廳價格資訊
    返回價格區間字串，如 "500-800"
    """
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
        
        # 查找 NT$XXX-XXX 格式（不在 | | 中）
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
                max_price = int(match.group(2)) if len(match.groups()) > 1 else min_price * 1.5
                return convert_to_budget_range(min_price, max_price)
        
        return None
        
    except Exception as e:
        print(f"    價格爬取錯誤：{str(e)}")
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

def scrape_images_from_openrice(url: str) -> List[str]:
    """
    從 OpenRice URL 爬取餐廳照片
    返回照片 URL 列表
    """
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
        image_urls = []
        
        # 查找所有 img 標籤
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            img_url = img.get('data-src') or img.get('src') or img.get('data-lazy-src') or img.get('data-original')
            
            if img_url:
                # 確保是完整的 URL
                if img_url.startswith('http'):
                    if img_url not in image_urls:
                        image_urls.append(img_url)
                elif img_url.startswith('//'):
                    img_url = 'https:' + img_url
                    if img_url not in image_urls:
                        image_urls.append(img_url)
        
        # 過濾照片 URL
        filtered_urls = []
        exclude_keywords = ['logo', 'icon', 'avatar', 'profile', 'button', 'arrow', 'close', 'spinner', 'loading']
        
        for url in image_urls:
            url_lower = url.lower()
            
            # 跳過明顯不是照片的 URL
            if any(keyword in url_lower for keyword in exclude_keywords):
                continue
            
            # 優先保留 OpenRice CDN 的照片
            if 'orstatic.com' in url_lower or 'openrice.com' in url_lower:
                # 確保是圖片格式
                if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.webp', 'photo', 'image']):
                    # 跳過太小的圖片，通常照片 URL 會包含尺寸標記
                    if any(size in url_lower for size in ['px', 'mx', 'large', 'medium', 'thumb']) or 'userphoto' in url_lower or 'photo' in url_lower:
                        filtered_urls.append(url)
            else:
                # 其他來源的圖片
                if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    if any(keyword in url_lower for keyword in ['photo', 'image', 'picture', 'food', 'dish', 'restaurant']):
                        filtered_urls.append(url)
        
        # 去重並限制數量
        unique_urls = []
        seen = set()
        for url in filtered_urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
                if len(unique_urls) >= 10:
                    break
        
        return unique_urls
        
    except Exception as e:
        print(f"    照片爬取錯誤：{str(e)}")
        return []

def update_all_restaurants(file_path: str, update_budget: bool = True, update_images: bool = True, test_mode: bool = False, limit: int = 10):
    """
    更新所有餐廳的預算和照片
    """
    print("=" * 80)
    print("開始更新餐廳資料...")
    print("=" * 80)
    
    # 載入資料庫
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data['restaurants']
    
    if test_mode:
        print(f"\n⚠️  測試模式：只處理前 {limit} 間餐廳")
        restaurants_to_process = restaurants[:limit]
    else:
        restaurants_to_process = restaurants
    
    print(f"\n總共餐廳數：{len(restaurants_to_process)} 間")
    
    # 統計
    no_budget_count = sum(1 for r in restaurants_to_process if not r.get('budget'))
    no_images_count = sum(1 for r in restaurants_to_process if not r.get('images') or len(r.get('images', [])) == 0)
    
    print(f"  無預算：{no_budget_count} 間")
    print(f"  無照片：{no_images_count} 間")
    print("\n開始處理...\n")
    
    budget_updated = 0
    images_updated = 0
    failed_budget = 0
    failed_images = 0
    
    for i, restaurant in enumerate(restaurants_to_process, 1):
        name = restaurant.get('name', '未知餐廳')
        url = restaurant.get('url', '')
        
        print(f"[{i}/{len(restaurants_to_process)}] {name[:40]}")
        
        if not url:
            print(f"  ❌ 無 URL，跳過")
            continue
        
        # 更新預算
        if update_budget and not restaurant.get('budget'):
            print(f"  正在爬取價格...", end=' ')
            budget = scrape_price_from_openrice(url)
            if budget:
                restaurant['budget'] = budget
                print(f"✅ {budget}")
                budget_updated += 1
            else:
                print(f"❌ 未找到")
                failed_budget += 1
            time.sleep(0.5)  # 避免請求過快
        
        # 更新照片
        if update_images and (not restaurant.get('images') or len(restaurant.get('images', [])) == 0):
            print(f"  正在爬取照片...", end=' ')
            images = scrape_images_from_openrice(url)
            if images:
                restaurant['images'] = images
                print(f"✅ {len(images)} 張")
                images_updated += 1
            else:
                print(f"❌ 未找到")
                restaurant['images'] = []  # 標記為已處理
                failed_images += 1
            time.sleep(0.5)  # 避免請求過快
        
        # 每處理 10 間餐廳保存一次（防止數據丟失）
        if i % 10 == 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  💾 已保存進度（{i}/{len(restaurants_to_process)}）")
    
    # 最終保存
    print("\n" + "=" * 80)
    print("保存更新後的資料庫...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("✅ 處理完成！")
    print("\n統計：")
    print(f"  總餐廳數：{len(restaurants_to_process)} 間")
    if update_budget:
        print(f"  預算更新：{budget_updated} 間")
        print(f"  預算失敗：{failed_budget} 間")
    if update_images:
        print(f"  照片更新：{images_updated} 間")
        print(f"  照片失敗：{failed_images} 間")
    print("=" * 80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="更新所有餐廳的預算和照片")
    parser.add_argument('--test', action='store_true', help='測試模式：只處理前 10 間餐廳')
    parser.add_argument('--limit', type=int, default=10, help='測試模式下處理的餐廳數量（預設：10）')
    parser.add_argument('--budget-only', action='store_true', help='只更新預算')
    parser.add_argument('--images-only', action='store_true', help='只更新照片')
    
    args = parser.parse_args()
    
    update_budget = not args.images_only
    update_images = not args.budget_only
    
    update_all_restaurants(
        'restaurants_database.json',
        update_budget=update_budget,
        update_images=update_images,
        test_mode=args.test,
        limit=args.limit
    )
