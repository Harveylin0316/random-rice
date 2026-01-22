#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新餐廳照片（分批處理）
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from typing import List

def scrape_images_from_openrice(url: str) -> List[str]:
    """從 OpenRice URL 爬取餐廳照片"""
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
            
            if any(keyword in url_lower for keyword in exclude_keywords):
                continue
            
            # 優先保留 OpenRice CDN 的照片
            if 'orstatic.com' in url_lower or 'openrice.com' in url_lower:
                if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.webp', 'photo', 'image']):
                    if any(size in url_lower for size in ['px', 'mx', 'large', 'medium', 'thumb']) or 'userphoto' in url_lower or 'photo' in url_lower:
                        filtered_urls.append(url)
            else:
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
        return []

def update_images_batch(file_path: str, batch_size: int = 50, start_index: int = 0):
    """批量更新餐廳照片"""
    print("=" * 80)
    print("開始批量更新餐廳照片...")
    print("=" * 80)
    
    # 載入資料庫
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 找出所有沒有照片的餐廳
    no_images_restaurants = [(i, r) for i, r in enumerate(data['restaurants']) 
                             if not r.get('images') or len(r.get('images', [])) == 0]
    
    print(f"\n總共無照片餐廳：{len(no_images_restaurants)} 間")
    print(f"本次處理：從第 {start_index + 1} 間開始，處理 {batch_size} 間\n")
    
    # 處理指定範圍的餐廳
    if start_index >= len(no_images_restaurants):
        print(f"⚠️  起始索引 {start_index} 超出範圍（總共 {len(no_images_restaurants)} 間無照片餐廳）")
        return
    
    end_index = min(start_index + batch_size, len(no_images_restaurants))
    restaurants_to_process = no_images_restaurants[start_index:end_index]
    
    updated_count = 0
    failed_count = 0
    
    for idx, (original_idx, restaurant) in enumerate(restaurants_to_process, 1):
        name = restaurant.get('name', '未知餐廳')
        url = restaurant.get('url', '')
        
        current_num = start_index + idx
        print(f"[{current_num}/{len(no_images_restaurants)}] {name[:50]}")
        
        if not url:
            print(f"  ❌ 無 URL，跳過")
            failed_count += 1
            continue
        
        # 爬取照片
        images = scrape_images_from_openrice(url)
        
        if images:
            data['restaurants'][original_idx]['images'] = images
            print(f"  ✅ {len(images)} 張")
            updated_count += 1
        else:
            print(f"  ❌ 未找到照片")
            data['restaurants'][original_idx]['images'] = []  # 標記為已處理
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
    if end_index < len(no_images_restaurants):
        print(f"\n💡 提示：還有 {len(no_images_restaurants) - end_index} 間餐廳待處理")
        print(f"   下次運行：python3 update_images_batch.py --start {end_index}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="批量更新餐廳照片")
    parser.add_argument('--batch-size', type=int, default=50, help='每批處理的餐廳數量（預設：50）')
    parser.add_argument('--start', type=int, default=0, help='從第幾間開始處理（預設：0）')
    
    args = parser.parse_args()
    
    update_images_batch(
        'restaurants_database.json',
        batch_size=args.batch_size,
        start_index=args.start
    )
