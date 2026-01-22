#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 OpenRice 頁面爬取餐廳照片並更新到資料庫
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Optional, Dict

def scrape_restaurant_images(url: str) -> List[str]:
    """
    從 OpenRice URL 爬取餐廳照片
    返回照片 URL 列表
    """
    print(f"  正在爬取照片：{url}")
    
    try:
        # 設定 headers 模擬瀏覽器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.openrice.com/',
        }
        
        # 發送請求
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        image_urls = []
        
        # 方法1: 查找 OpenRice 常見的圖片元素
        # OpenRice 通常使用 img 標籤，src 或 data-src 屬性
        
        # 查找所有 img 標籤
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            # 優先使用 data-src（懶加載）
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
                elif img_url.startswith('/'):
                    # 相對路徑，可能需要補全域名
                    if 'openrice.com' in url:
                        base_url = 'https://www.openrice.com'
                        img_url = base_url + img_url
                        if img_url not in image_urls:
                            image_urls.append(img_url)
        
        # 方法2: 查找背景圖片（可能在 style 屬性中）
        elements_with_bg = soup.find_all(attrs={'style': re.compile(r'background.*image|background-image')})
        for element in elements_with_bg:
            style = element.get('style', '')
            # 提取 URL
            url_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
            if url_match:
                bg_url = url_match.group(1)
                if bg_url.startswith('http'):
                    if bg_url not in image_urls:
                        image_urls.append(bg_url)
                elif bg_url.startswith('//'):
                    bg_url = 'https:' + bg_url
                    if bg_url not in image_urls:
                        image_urls.append(bg_url)
        
        # 方法3: 查找 OpenRice 特定的圖片容器
        # OpenRice 可能使用特定的 class 或 data 屬性
        photo_containers = soup.find_all(['div', 'section'], class_=re.compile(r'photo|image|gallery|picture', re.I))
        for container in photo_containers:
            imgs = container.find_all('img')
            for img in imgs:
                img_url = img.get('data-src') or img.get('src') or img.get('data-lazy-src')
                if img_url and img_url.startswith('http'):
                    if img_url not in image_urls:
                        image_urls.append(img_url)
        
        # 過濾和清理圖片 URL
        # 移除明顯不是餐廳照片的 URL（如 logo、icon 等）
        filtered_urls = []
        exclude_keywords = ['logo', 'icon', 'avatar', 'profile', 'button', 'arrow', 'close', 'menu-icon', 'spinner', 'loading']
        
        # OpenRice 照片 URL 特徵
        # 通常包含：userphoto, photo, dish, food 等關鍵字
        # 或者來自 cdn-tw.orstatic.com 域名
        
        for url in image_urls:
            url_lower = url.lower()
            
            # 跳過明顯不是照片的 URL
            if any(keyword in url_lower for keyword in exclude_keywords):
                continue
            
            # 優先保留 OpenRice CDN 的照片
            if 'orstatic.com' in url_lower or 'openrice.com' in url_lower:
                # 確保是圖片格式
                if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.webp', 'photo', 'image']):
                    # 跳過太小的圖片（可能是圖示），通常照片 URL 會包含尺寸標記
                    if any(size in url_lower for size in ['px', 'mx', 'large', 'medium', 'thumb']):
                        filtered_urls.append(url)
                    elif 'userphoto' in url_lower or 'photo' in url_lower:
                        # OpenRice 的照片通常包含這些關鍵字
                        filtered_urls.append(url)
            else:
                # 其他來源的圖片，確保是合理的圖片 URL
                if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    # 檢查是否可能是餐廳照片（包含相關關鍵字）
                    if any(keyword in url_lower for keyword in ['photo', 'image', 'picture', 'food', 'dish', 'restaurant']):
                        filtered_urls.append(url)
        
        # 去重並限制照片數量（取前 10 張）
        unique_urls = []
        seen = set()
        for url in filtered_urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
                if len(unique_urls) >= 10:
                    break
        
        return unique_urls
        
    except requests.exceptions.RequestException as e:
        print(f"  請求錯誤：{str(e)}")
        return []
    except Exception as e:
        print(f"  處理錯誤：{str(e)}")
        return []

def update_restaurant_images(file_path: str, test_mode: bool = False, limit: int = 10):
    """
    為餐廳資料庫添加照片 URL
    """
    print("=" * 80)
    print("開始爬取餐廳照片...")
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
    print("開始處理...\n")
    
    updated_count = 0
    failed_count = 0
    already_has_images_count = 0
    
    for i, restaurant in enumerate(restaurants_to_process, 1):
        name = restaurant.get('name', '未知餐廳')
        url = restaurant.get('url', '')
        current_images = restaurant.get('images', [])
        
        print(f"[{i}/{len(restaurants_to_process)}] {name[:40]}")
        
        # 如果已經有照片，跳過（除非要強制更新）
        if current_images and len(current_images) > 0:
            print(f"  ✅ (已有 {len(current_images)} 張照片)")
            already_has_images_count += 1
            continue
        
        if not url:
            print(f"  ❌ 無 URL")
            failed_count += 1
            continue
        
        # 爬取照片
        images = scrape_restaurant_images(url)
        
        if images:
            restaurant['images'] = images
            print(f"  ✅ 找到 {len(images)} 張照片")
            updated_count += 1
        else:
            print(f"  ❌ 未找到照片")
            restaurant['images'] = []  # 標記為已處理
            failed_count += 1
        
        # 避免請求過快
        time.sleep(1)
    
    # 保存更新後的資料庫
    print("\n" + "=" * 80)
    print("保存更新後的資料庫...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("✅ 處理完成！")
    print("\n統計：")
    print(f"  總餐廳數：{len(restaurants_to_process)} 間")
    print(f"  已有照片：{already_has_images_count} 間")
    print(f"  新增照片：{updated_count} 間")
    print(f"  失敗：{failed_count} 間")
    if len(restaurants_to_process) > 0:
        success_rate = ((updated_count + already_has_images_count) / len(restaurants_to_process)) * 100
        print(f"  成功率：{success_rate:.1f}%")
    print("=" * 80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="從 OpenRice 爬取餐廳照片")
    parser.add_argument('--test', action='store_true', help='測試模式：只處理前 10 間餐廳')
    parser.add_argument('--limit', type=int, default=10, help='測試模式下處理的餐廳數量（預設：10）')
    
    args = parser.parse_args()
    
    update_restaurant_images('restaurants_database.json', test_mode=args.test, limit=args.limit)
