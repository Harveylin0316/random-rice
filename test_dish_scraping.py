#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試從 OpenRice 頁面爬取 dish 資訊（判斷是否為吃到飽）
測試餐廳：紅蟹將軍帝王蟹+燒烤吃到飽火鍋
"""

import requests
from bs4 import BeautifulSoup
import re

# 測試餐廳 URL
TEST_URL = "https://s.openrice.com/cHRSm02BOq700"

def scrape_dish_from_openrice(url: str) -> dict:
    """
    從 OpenRice URL 爬取 dish 資訊
    
    Args:
        url: OpenRice 餐廳頁面 URL
        
    Returns:
        字典，包含：
        - dish: 所有 dish 列表
        - is_buffet: 是否包含「吃到飽」的布林值
        例如: {"dish": ["火鍋吃到飽", "串燒"], "is_buffet": True}
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.openrice.com/',
        }
        
        print(f"正在爬取：{url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找 <div class="pdhs-filter-tags-section">
        filter_section = soup.find('div', class_='pdhs-filter-tags-section')
        
        if not filter_section:
            print("❌ 找不到 <div class='pdhs-filter-tags-section'>")
            return {"dish": [], "is_buffet": False}
        
        print("✅ 找到 pdhs-filter-tags-section")
        
        # 在該 section 中找到所有 <a> 標籤，其 href 包含 "restaurants/dish/"
        dish_links = filter_section.find_all('a', href=re.compile(r'restaurants/dish/'))
        
        print(f"\n找到 {len(dish_links)} 個 dish 相關連結：")
        print("=" * 60)
        
        dishes = []
        is_buffet = False
        
        for link in dish_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"href: {href}")
            print(f"文字: {text}")
            
            # 收集所有 dish 文字
            if text and text not in dishes:
                dishes.append(text)
            
            # 檢查文字是否包含「吃到飽」
            if '吃到飽' in text:
                print("  ✅ 包含「吃到飽」")
                is_buffet = True
            else:
                print("  ❌ 不包含「吃到飽」")
            
            print("-" * 60)
        
        print(f"\n最終 dish 列表: {dishes}")
        print(f"是否為吃到飽: {is_buffet}")
        
        return {"dish": dishes, "is_buffet": is_buffet}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 請求錯誤: {e}")
        return {"dish": [], "is_buffet": False}
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return {"dish": [], "is_buffet": False}

if __name__ == "__main__":
    print("=" * 60)
    print("測試爬取 dish 資訊")
    print("=" * 60)
    print(f"測試餐廳 URL: {TEST_URL}")
    print()
    
    result = scrape_dish_from_openrice(TEST_URL)
    
    print()
    print("=" * 60)
    if result["dish"]:
        print(f"✅ 成功爬取到 dish 資訊:")
        print(f"   dish: {result['dish']}")
        print(f"   is_buffet: {result['is_buffet']}")
        if result["is_buffet"]:
            print("✅ 確認：該餐廳是吃到飽餐廳")
        else:
            print("❌ 該餐廳不是吃到飽餐廳")
    else:
        print("❌ 未找到 dish 資訊")
        print(f"   is_buffet: {result['is_buffet']}")
    print("=" * 60)
