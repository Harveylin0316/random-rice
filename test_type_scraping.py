#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試從 OpenRice URL 抓取餐廳類型
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_type_from_openrice(url):
    """
    從 OpenRice URL 抓取餐廳類型
    
    Args:
        url: OpenRice 餐廳頁面 URL
        
    Returns:
        list: 餐廳類型列表
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到 <div class="pdhs-filter-tags-section">
        filter_section = soup.find('div', class_='pdhs-filter-tags-section')
        
        if not filter_section:
            print(f"❌ 找不到 pdhs-filter-tags-section")
            return []
        
        # 在這個 section 中找到所有 <a> 元素，href 包含 "type"
        type_links = filter_section.find_all('a', href=re.compile(r'type'))
        
        types = []
        for link in type_links:
            # 提取文字內容和 href
            text = link.get_text(strip=True)
            href = link.get('href', '')
            
            if text:
                types.append({
                    'text': text,
                    'href': href
                })
        
        return types
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 請求錯誤：{e}")
        return []
    except Exception as e:
        print(f"❌ 解析錯誤：{e}")
        return []

if __name__ == "__main__":
    # 讀取資料庫，找 PALI PALI 餐廳測試
    with open('restaurants_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 找 PALI PALI 餐廳
    test_restaurant = None
    for r in data['restaurants']:
        if 'PALI PALI' in r.get('name', '') and r.get('url'):
            test_restaurant = r
            break
    
    if not test_restaurant:
        print("❌ 找不到 PALI PALI 餐廳")
        exit(1)
    
    print("=" * 80)
    print("測試餐廳資訊")
    print("=" * 80)
    print(f"餐廳名稱：{test_restaurant.get('name')}")
    print(f"URL：{test_restaurant.get('url')}")
    print(f"目前餐廳類型：{test_restaurant.get('type', [])}")
    print()
    
    print("=" * 80)
    print("開始爬取餐廳類型...")
    print("=" * 80)
    
    types = scrape_type_from_openrice(test_restaurant.get('url'))
    
    print()
    print("=" * 80)
    print("爬取結果")
    print("=" * 80)
    if types:
        print(f"✅ 找到 {len(types)} 個包含 'type' 的連結：")
        for i, type_item in enumerate(types, 1):
            print(f"  {i}. 文字：{type_item['text']}")
            print(f"     href：{type_item['href']}")
    else:
        print("❌ 沒有找到包含 'type' 的連結")
    
    # 也檢查一下整個 section 的內容
    print()
    print("=" * 80)
    print("檢查整個 pdhs-filter-tags-section 的內容")
    print("=" * 80)
    try:
        response = requests.get(test_restaurant.get('url'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        filter_section = soup.find('div', class_='pdhs-filter-tags-section')
        if filter_section:
            all_links = filter_section.find_all('a')
            print(f"找到 {len(all_links)} 個 <a> 元素：")
            for i, link in enumerate(all_links, 1):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if 'type' in href:
                    print(f"  {i}. [TYPE] 文字：{text}")
                    print(f"     href：{href}")
                else:
                    print(f"  {i}. 文字：{text}")
                    print(f"     href：{href}")
    except Exception as e:
        print(f"檢查時發生錯誤：{e}")
    
    print()
    print("=" * 80)
