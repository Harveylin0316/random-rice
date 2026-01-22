#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新餐廳料理風格（分批處理）
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List

def scrape_cuisine_style_from_openrice(url: str) -> List[str]:
    """從 OpenRice URL 爬取餐廳料理風格"""
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
        
        # 標準化的料理風格映射
        cuisine_keywords_map = {
            # 台式
            '台式': ['台', '台灣', 'Taiwanese', '台菜'],
            # 中式
            '中式': ['中', '中國', 'Chinese', '中菜', '中華', '粵', '川', '湘', '港式'],
            # 日式
            '日式': ['日', '日本', 'Japanese', '日料', '和食', '居酒屋', 'Izakaya'],
            # 韓式
            '韓式': ['韓', '韓國', 'Korean', '韓料'],
            # 美式
            '美式': ['美', '美國', 'American', '美式'],
            # 義式
            '義式': ['義', '義大利', 'Italian', '義大利菜'],
            # 法式
            '法式': ['法', '法國', 'French', '法國菜'],
            # 泰式
            '泰式': ['泰', '泰國', 'Thai', '泰國菜'],
            # 印度
            '印度': ['印度', 'Indian', '印度菜'],
            # 越南
            '越南': ['越南', 'Vietnamese', '越南菜'],
            # 新加坡
            '新加坡': ['新加坡', 'Singaporean', '新加坡菜'],
            # 馬來西亞
            '馬來西亞': ['馬來', 'Malaysian', '馬來菜'],
            # 素食
            '素食': ['素食', '蔬食', 'Vegan', 'Vegetarian', '素'],
        }
        
        # 方法1: 查找 JSON-LD 結構化資料
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                script_content = script.string
                if script_content:
                    json_data = json.loads(script_content)
                    if isinstance(json_data, dict):
                        if 'servesCuisine' in json_data:
                            cuisine = json_data['servesCuisine']
                            if isinstance(cuisine, str):
                                cuisine_styles.append(cuisine)
                            elif isinstance(cuisine, list):
                                cuisine_styles.extend(cuisine)
                    elif isinstance(json_data, list):
                        for item in json_data:
                            if isinstance(item, dict) and 'servesCuisine' in item:
                                cuisine = item['servesCuisine']
                                if isinstance(cuisine, str):
                                    cuisine_styles.append(cuisine)
                                elif isinstance(cuisine, list):
                                    cuisine_styles.extend(cuisine)
            except:
                pass
        
        # 方法2: 查找頁面中的關鍵字模式
        # 查找 "菜式："、"料理：" 等明確標示
        patterns = [
            r'菜式[：:]\s*([^，,。\n、\s]+)',
            r'料理[：:]\s*([^，,。\n、\s]+)',
            r'菜系[：:]\s*([^，,。\n、\s]+)',
            r'菜餚[：:]\s*([^，,。\n、\s]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, all_text)
            for match in matches:
                match = match.strip()
                # 直接檢查匹配的文字是否包含關鍵字
                for style, keywords in cuisine_keywords_map.items():
                    if any(kw in match for kw in keywords):
                        if style not in cuisine_styles:
                            cuisine_styles.append(style)
                    # 也檢查匹配的文字本身是否就是標準風格
                    if match in ['台式', '中式', '日式', '韓式', '美式', '義式', '法式', '泰式', '印度', '越南', '新加坡', '馬來西亞', '素食']:
                        if match not in cuisine_styles:
                            cuisine_styles.append(match)
        
        # 方法3: 在標題和描述中查找（降低權重，只在其他方法沒找到時使用）
        if len(cuisine_styles) == 0:
            title = soup.find('title')
            meta_description = soup.find('meta', attrs={'name': 'description'})
            
            search_texts = []
            if title:
                search_texts.append(title.text)
            if meta_description:
                search_texts.append(meta_description.get('content', ''))
            
            for text in search_texts:
                for style, keywords in cuisine_keywords_map.items():
                    # 更嚴格的匹配：確保關鍵字在合理的上下文中
                    for kw in keywords:
                        if kw in text:
                            # 檢查前後文，避免誤判
                            idx = text.find(kw)
                            context = text[max(0, idx-10):min(len(text), idx+len(kw)+10)]
                            if any(ctx in context for ctx in ['菜', '料理', '式', 'cuisine', 'food']):
                                if style not in cuisine_styles:
                                    cuisine_styles.append(style)
                                    break
        
        # 方法4: 查找特定的 HTML 元素（降低權重）
        if len(cuisine_styles) < 2:
            cuisine_elements = soup.find_all(['div', 'span', 'a', 'li'], 
                                            class_=re.compile(r'cuisine|food-type|category|tag|label', re.I))
            for element in cuisine_elements:
                text = element.get_text().strip()
                # 只接受較短的文字（避免誤判）
                if len(text) < 50:
                    for style, keywords in cuisine_keywords_map.items():
                        if any(kw in text for kw in keywords):
                            if style not in cuisine_styles:
                                cuisine_styles.append(style)
                                break
        
        # 標準化料理風格名稱
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
            '日式料理': '日式',
            '韓料': '韓式',
            '韓國': '韓式',
            '韓國料理': '韓式',
            '義大利': '義式',
            'Italian': '義式',
            '義大利菜': '義式',
            '意大利菜': '義式',
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
        
        # 標準化的料理風格列表（只接受這些）
        valid_styles = ['台式', '中式', '日式', '韓式', '美式', '義式', '法式', '泰式', '印度', '越南', '新加坡', '馬來西亞', '素食']
        
        # 標準化和過濾
        standardized = []
        for style in cuisine_styles:
            # 映射到標準名稱
            mapped = style_mapping.get(style, style)
            # 只保留有效的標準風格
            if mapped in valid_styles and mapped not in standardized:
                standardized.append(mapped)
        
        # 優先級排序
        priority_order = ['台式', '日式', '韓式', '中式', '美式', '義式', '法式', '泰式', '印度', '越南', '新加坡', '馬來西亞', '素食']
        def get_priority(style):
            try:
                return priority_order.index(style)
            except ValueError:
                return 999
        
        standardized.sort(key=get_priority)
        
        # 最多返回3個
        return standardized[:3]
        
    except Exception as e:
        return []

def update_cuisine_styles_batch(file_path: str, batch_size: int = 50, start_index: int = 0):
    """批量更新餐廳料理風格"""
    print("=" * 80)
    print("開始批量更新餐廳料理風格...")
    print("=" * 80)
    
    # 載入資料庫
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data['restaurants']
    
    print(f"\n總共餐廳數：{len(restaurants)} 間")
    print(f"本次處理：從第 {start_index + 1} 間開始，處理 {batch_size} 間\n")
    
    # 處理指定範圍的餐廳
    end_index = min(start_index + batch_size, len(restaurants))
    restaurants_to_process = restaurants[start_index:end_index]
    
    updated_count = 0
    failed_count = 0
    no_url_count = 0
    
    for idx, restaurant in enumerate(restaurants_to_process, 1):
        name = restaurant.get('name', '未知餐廳')
        url = restaurant.get('url', '')
        
        current_num = start_index + idx
        print(f"[{current_num}/{len(restaurants)}] {name[:50]}")
        
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
    print(f"  無 URL：{no_url_count} 間")
    if len(restaurants_to_process) > 0:
        success_rate = (updated_count / len(restaurants_to_process)) * 100
        print(f"  成功率：{success_rate:.1f}%")
    print("=" * 80)
    
    # 提示下一批次
    if end_index < len(restaurants):
        print(f"\n💡 提示：還有 {len(restaurants) - end_index} 間餐廳待處理")
        print(f"   下次運行：python3 update_cuisine_styles_batch.py --start {end_index}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="批量更新餐廳料理風格")
    parser.add_argument('--batch-size', type=int, default=50, help='每批處理的餐廳數量（預設：50）')
    parser.add_argument('--start', type=int, default=0, help='從第幾間開始處理（預設：0）')
    
    args = parser.parse_args()
    
    update_cuisine_styles_batch(
        'restaurants_database.json',
        batch_size=args.batch_size,
        start_index=args.start
    )
