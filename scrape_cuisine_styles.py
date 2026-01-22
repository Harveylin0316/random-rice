#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 OpenRice 頁面爬取餐廳料理風格並更新資料庫
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Optional

def scrape_cuisine_style_from_openrice(url: str) -> List[str]:
    """
    從 OpenRice URL 爬取餐廳料理風格
    返回料理風格列表
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
            return []
        
        cuisine_styles = []
        
        # 方法1: 查找 OpenRice 常見的料理風格標籤
        # OpenRice 通常在特定位置顯示料理風格，可能是 "菜式"、"料理"、"菜系" 等關鍵字
        
        # 查找包含料理風格關鍵字的元素
        cuisine_keywords = [
            '菜式', '料理', '菜系', '菜餚', '美食', '風味',
            'Cuisine', 'cuisine', '菜', '式'
        ]
        
        # 常見的料理風格列表
        possible_cuisines = [
            '台式', '台菜', '台灣', '台灣菜',
            '中式', '中菜', '中華', '中國菜',
            '日式', '日料', '日本', '日本料理',
            '韓式', '韓料', '韓國', '韓國料理',
            '美式', '美國', 'American',
            '義式', '義大利', 'Italian', '義大利菜',
            '法式', '法國', 'French', '法國菜',
            '泰式', '泰國', 'Thai', '泰國菜',
            '印度', 'Indian', '印度菜',
            '越南', 'Vietnamese', '越南菜',
            '新加坡', 'Singaporean', '新加坡菜',
            '馬來西亞', 'Malaysian', '馬來菜',
            '港式', '香港', 'Hong Kong',
            '粵式', '粵菜', '廣東',
            '川菜', '四川',
            '湘菜', '湖南',
            '素食', '蔬食', 'Vegan', 'Vegetarian',
            '燒烤', '燒肉', '烤肉',
            '火鍋', '鍋物',
            '壽司', 'Sushi',
            '拉麵', 'Ramen',
            '居酒屋', 'Izakaya',
            '酒吧', 'Bar', 'Pub',
            '咖啡', 'Coffee', 'Cafe',
            '甜點', 'Dessert', '甜品',
            '麵食', 'Noodles',
            '飯類', 'Rice',
            '小吃', 'Street Food'
        ]
        
        # 方法1: 查找頁面中明確標示的料理風格
        # 通常在標題、描述或特定標籤中
        
        # 查找標題中的料理風格
        title = soup.find('title')
        if title:
            title_text = title.text
            for cuisine in possible_cuisines:
                if cuisine in title_text and cuisine not in cuisine_styles:
                    cuisine_styles.append(cuisine)
        
        # 查找 meta 標籤中的料理風格
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            content = meta.get('content', '') or meta.get('property', '') or ''
            if content:
                for cuisine in possible_cuisines:
                    if cuisine in content and cuisine not in cuisine_styles:
                        cuisine_styles.append(cuisine)
        
        # 方法2: 查找包含 "菜式"、"料理" 等關鍵字的文字
        text_elements = soup.find_all(['p', 'div', 'span', 'li', 'td', 'h1', 'h2', 'h3', 'h4'])
        for element in text_elements:
            text = element.get_text()
            
            # 查找 "菜式："、"料理：" 等格式
            patterns = [
                r'菜式[：:]\s*([^，,。\n]+)',
                r'料理[：:]\s*([^，,。\n]+)',
                r'菜系[：:]\s*([^，,。\n]+)',
                r'菜餚[：:]\s*([^，,。\n]+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    # 清理匹配的文字
                    match = match.strip()
                    # 檢查是否包含已知的料理風格
                    for cuisine in possible_cuisines:
                        if cuisine in match and cuisine not in cuisine_styles:
                            cuisine_styles.append(cuisine)
        
        # 方法3: 查找 OpenRice 特定的料理風格標籤或 class
        # 查找包含 cuisine、food-type 等 class 的元素
        cuisine_elements = soup.find_all(['div', 'span', 'a'], class_=re.compile(r'cuisine|food|type|category', re.I))
        for element in cuisine_elements:
            text = element.get_text()
            for cuisine in possible_cuisines:
                if cuisine in text and cuisine not in cuisine_styles:
                    cuisine_styles.append(cuisine)
        
        # 方法4: 查找 OpenRice 特定的資料結構
        # 查找 JSON-LD 結構化資料
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                json_data = json.loads(script.string)
                # 查找 servesCuisine 欄位
                if isinstance(json_data, dict):
                    if 'servesCuisine' in json_data:
                        cuisine = json_data['servesCuisine']
                        if isinstance(cuisine, str) and cuisine not in cuisine_styles:
                            cuisine_styles.append(cuisine)
                        elif isinstance(cuisine, list):
                            for c in cuisine:
                                if c not in cuisine_styles:
                                    cuisine_styles.append(c)
            except:
                pass
        
        # 方法5: 查找特定的 HTML 結構
        # OpenRice 可能使用特定的 class 或 data 屬性來標示料理風格
        cuisine_containers = soup.find_all(['div', 'span', 'li'], 
                                          class_=re.compile(r'cuisine|food-type|category|tag|label', re.I))
        for container in cuisine_containers:
            text = container.get_text().strip()
            # 檢查是否包含已知的料理風格
            for cuisine in possible_cuisines:
                if cuisine.lower() in text.lower() and cuisine not in cuisine_styles:
                    # 進一步確認：檢查是否在合理的上下文中
                    parent_text = ''
                    parent = container.find_parent()
                    if parent:
                        parent_text = parent.get_text()[:100]
                    if any(keyword in (text + parent_text).lower() for keyword in ['菜', '料理', '式', 'cuisine', 'food']):
                        cuisine_styles.append(cuisine)
        
        # 過濾和標準化料理風格
        # 移除一些明顯不是料理風格的詞彙
        exclude_words = ['Rice', 'Noodles', '麵食', '飯類', '小吃', 'Street Food']
        filtered_styles = [s for s in cuisine_styles if s not in exclude_words]
        
        # 標準化料理風格名稱
        standardized_styles = []
        style_mapping = {
            '台菜': '台式',
            '台灣': '台式',
            '台灣菜': '台式',
            '中菜': '中式',
            '中華': '中式',
            '中國菜': '中式',
            '日料': '日式',
            '日本': '日式',
            '日本料理': '日式',
            '韓料': '韓式',
            '韓國': '韓式',
            '韓國料理': '韓式',
            '義大利': '義式',
            'Italian': '義式',
            '義大利菜': '義式',
            '法國': '法式',
            'French': '法式',
            '法國菜': '法式',
            '泰國': '泰式',
            'Thai': '泰式',
            '泰國菜': '泰式',
            'Indian': '印度',
            '印度菜': '印度',
            '蔬食': '素食',
            'Vegan': '素食',
            'Vegetarian': '素食',
            '粵式': '中式',
            '粵菜': '中式',
            '廣東': '中式',
            '川菜': '中式',
            '四川': '中式',
            '湘菜': '中式',
            '湖南': '中式',
            '港式': '中式',
            '香港': '中式',
        }
        
        # 優先級列表：如果同時找到多個相關風格，優先選擇更具體的
        priority_order = ['台式', '日式', '韓式', '中式', '美式', '義式', '法式', '泰式', '印度', '素食']
        
        for style in filtered_styles:
            # 映射到標準名稱
            standardized = style_mapping.get(style, style)
            if standardized not in standardized_styles:
                standardized_styles.append(standardized)
        
        # 按照優先級排序
        def get_priority(style):
            try:
                return priority_order.index(style)
            except ValueError:
                return 999
        
        standardized_styles.sort(key=get_priority)
        
        # 如果找到太多，只保留前3個最重要的
        return standardized_styles[:3]
        
    except requests.exceptions.RequestException as e:
        print(f"    請求錯誤：{str(e)}")
        return []
    except Exception as e:
        print(f"    處理錯誤：{str(e)}")
        return []

def update_cuisine_styles(file_path: str, test_mode: bool = False, limit: int = 10):
    """
    更新所有餐廳的料理風格
    """
    print("=" * 80)
    print("開始爬取餐廳料理風格...")
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
    no_url_count = 0
    
    for i, restaurant in enumerate(restaurants_to_process, 1):
        name = restaurant.get('name', '未知餐廳')
        url = restaurant.get('url', '')
        current_styles = restaurant.get('cuisine_style', [])
        
        print(f"[{i}/{len(restaurants_to_process)}] {name[:40]}")
        
        if not url:
            print(f"  ❌ 無 URL，跳過")
            no_url_count += 1
            continue
        
        # 爬取料理風格
        cuisine_styles = scrape_cuisine_style_from_openrice(url)
        
        if cuisine_styles:
            restaurant['cuisine_style'] = cuisine_styles
            print(f"  ✅ {', '.join(cuisine_styles)}")
            updated_count += 1
        else:
            print(f"  ❌ 未找到料理風格")
            restaurant['cuisine_style'] = []  # 清空現有的
            failed_count += 1
        
        # 每處理 10 間保存一次
        if i % 10 == 0:
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
    print("✅ 處理完成！")
    print(f"\n統計：")
    print(f"  總餐廳數：{len(restaurants_to_process)} 間")
    print(f"  成功更新：{updated_count} 間")
    print(f"  失敗：{failed_count} 間")
    print(f"  無 URL：{no_url_count} 間")
    if len(restaurants_to_process) > 0:
        success_rate = (updated_count / len(restaurants_to_process)) * 100
        print(f"  成功率：{success_rate:.1f}%")
    print("=" * 80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="從 OpenRice 爬取餐廳料理風格")
    parser.add_argument('--test', action='store_true', help='測試模式：只處理前 10 間餐廳')
    parser.add_argument('--limit', type=int, default=10, help='測試模式下處理的餐廳數量（預設：10）')
    
    args = parser.parse_args()
    
    update_cuisine_styles('restaurants_database.json', test_mode=args.test, limit=args.limit)
