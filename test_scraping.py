#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試從 OpenRice URL 爬取餐廳價格資訊
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time

def get_restaurant_price_from_openrice(url: str) -> dict:
    """從 OpenRice URL 爬取餐廳價格資訊"""
    
    print(f"\n正在爬取：{url}")
    
    try:
        # 設定 headers 模擬瀏覽器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        }
        
        # 發送請求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"  狀態碼：{response.status_code}")
        print(f"  網頁長度：{len(response.text)} bytes")
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 先看看網頁結構，尋找價格相關資訊
        # OpenRice 通常在特定位置顯示價格
        
        # 方法1: 尋找價格標籤（可能是 "人均消費"、"平均消費" 等）
        price_texts = []
        
        # 查找包含價格的文字
        # 常見模式：$300-$600, NT$500-800, 300-600元 等
        price_patterns = [
            r'人均[消費]*[：:]?\s*[\$NT]*\s*(\d+)\s*[-~至]\s*[\$NT]*\s*(\d+)',  # 人均消費：$300-$600
            r'平均[消費]*[：:]?\s*[\$NT]*\s*(\d+)\s*[-~至]\s*[\$NT]*\s*(\d+)',  # 平均消費：$300-$600
            r'[\$NT]*\s*(\d+)\s*[-~至]\s*[\$NT]*\s*(\d+)\s*[元]*',              # $300-$600元
            r'消費[：:]?\s*[\$NT]*\s*(\d+)\s*[-~至]\s*[\$NT]*\s*(\d+)',          # 消費：$300-$600
            r'價格[：:]?\s*[\$NT]*\s*(\d+)\s*[-~至]\s*[\$NT]*\s*(\d+)',          # 價格：$300-$600
        ]
        
        # 方法1: 查找 OpenRice 特有的價格格式 |NT$XXX| 或 |NT$XXX以上| 或 |NT$XXX-XXX|
        # 通常在餐廳標題附近，可能是 h1, h2, span 或其他元素
        all_text = soup.get_text()
        
        # 優先查找 |NT$XXX-XXX| 範圍格式
        pipe_range_match = re.search(r'\|NT\$(\d+)\s*[-~至]\s*NT\$(\d+)\|', all_text)
        if not pipe_range_match:
            pipe_range_match = re.search(r'\|NT\$(\d+)\s*[-~至]\s*(\d+)\|', all_text)
        if pipe_range_match:
            min_price = int(pipe_range_match.group(1))
            max_price = int(pipe_range_match.group(2))
            price_texts.append(f"NT${min_price}-{max_price}")
        
        # 查找 |NT$XXX以上| 格式
        pipe_above_match = re.search(r'\|NT\$(\d+)以上\|', all_text)
        if pipe_above_match:
            price_num = int(pipe_above_match.group(1))
            price_texts.append(f"NT${price_num}以上")
        
        # 查找 |NT$XXX| 單一價格格式
        pipe_single_match = re.search(r'\|NT\$(\d+)\|', all_text)
        if pipe_single_match:
            price_num = int(pipe_single_match.group(1))
            price_texts.append(f"NT${price_num}")
        
        # 查找所有可能包含價格的元素
        text_elements = soup.find_all(['p', 'div', 'span', 'td', 'li', 'h1', 'h2', 'h3'])
        
        for element in text_elements:
            if element.text:
                # 優先查找 NT$XXX-XXX 範圍格式
                nt_range_match = re.search(r'NT\$(\d+)\s*[-~至]\s*NT\$(\d+)', element.text)
                if not nt_range_match:
                    nt_range_match = re.search(r'NT\$(\d+)\s*[-~至]\s*(\d+)', element.text)
                if nt_range_match:
                    min_price = int(nt_range_match.group(1))
                    max_price = int(nt_range_match.group(2))
                    price_texts.append(f"NT${min_price}-{max_price}")
                    continue
                
                # 查找 NT$XXX以上 格式
                nt_above_match = re.search(r'NT\$(\d+)以上', element.text)
                if nt_above_match:
                    price_num = int(nt_above_match.group(1))
                    price_texts.append(f"NT${price_num}以上")
                    continue
                
                # 查找 NT$XXX 單一價格格式（最後才匹配，避免優先匹配到範圍的一部分）
                nt_single_match = re.search(r'NT\$(\d+)(?!\s*[-~至])', element.text)
                if nt_single_match:
                    price_num = int(nt_single_match.group(1))
                    price_texts.append(f"NT${price_num}")
                
                # 查找其他格式
                for pattern in price_patterns:
                    match = re.search(pattern, element.text)
                    if match:
                        price_texts.append(element.text.strip())
                        break
        
        # 方法2: 查找特定的 class 或 id（需要檢查實際網頁結構）
        # 先檢查網頁的 title 確認是否正確載入
        title = soup.find('title')
        print(f"  網頁標題：{title.text if title else '未找到'}")
        
        # 輸出找到的價格相關文字（前10個）
        print(f"\n  找到的價格相關文字（前10個）：")
        for i, text in enumerate(price_texts[:10], 1):
            print(f"    {i}. {text}")
        
        # 嘗試從文字中提取價格範圍
        price_range = None
        
        # 優先處理 NT$ 格式的價格
        for text in price_texts:
            # 優先處理 NT$XXX-XXX 範圍格式（例如 NT$501-1000）
            nt_range_match = re.search(r'NT\$(\d+)\s*[-~至]\s*(\d+)', text)
            if nt_range_match:
                min_price = int(nt_range_match.group(1))
                max_price = int(nt_range_match.group(2))
                # 使用範圍的中間值來判斷預算區間（更準確）
                avg_price = (min_price + max_price) / 2
                if avg_price >= 2000:
                    price_range = "2000以上"
                elif avg_price >= 1250:  # 1250-1999 -> 1000-1500
                    price_range = "1000-1500"
                elif avg_price >= 650:  # 650-1249 -> 500-800
                    price_range = "500-800"
                elif avg_price >= 300:  # 300-649 -> 200-400
                    price_range = "200-400"
                else:  # < 300
                    price_range = "200以下"
                break
            
            # 處理 NT$XXX以上 格式
            nt_above_match = re.search(r'NT\$(\d+)以上', text)
            if nt_above_match:
                price_num = int(nt_above_match.group(1))
                # 轉換為預算區間
                if price_num >= 2000:
                    price_range = "2000以上"
                elif price_num >= 1500:
                    price_range = "1000-1500"
                elif price_num >= 800:
                    price_range = "500-800"
                elif price_num >= 400:
                    price_range = "200-400"
                else:
                    price_range = "200以下"
                break
            
            # 處理 NT$XXX 格式（單一價格）
            nt_single_match = re.search(r'NT\$(\d+)', text)
            if nt_single_match:
                price_num = int(nt_single_match.group(1))
                # 轉換為預算區間（根據價格值判斷）
                if price_num >= 1500:
                    price_range = "1000-1500"
                elif price_num >= 800:
                    price_range = "500-800"
                elif price_num >= 400:
                    price_range = "200-400"
                else:
                    price_range = "200以下"
                break
        
        # 如果沒有找到 NT$ 格式，嘗試找數字範圍
        if not price_range:
            for text in price_texts:
                # 提取數字範圍
                match = re.search(r'(\d+)\s*[-~至]\s*(\d+)', text)
                if match:
                    min_price = int(match.group(1))
                    max_price = int(match.group(2))
                    
                    # 判斷價格範圍（應該在合理範圍內，比如 100-5000）
                    if 100 <= min_price <= 5000 and 100 <= max_price <= 5000 and min_price < max_price:
                        # 轉換為我們的預算區間格式
                        if max_price <= 400:
                            price_range = "200-400"
                        elif max_price <= 800:
                            price_range = "500-800"
                        elif max_price <= 1500:
                            price_range = "1000-1500"
                        else:
                            price_range = "2000以上"
                        break
        
        # 方法3: 保存網頁內容到檔案以便檢查結構
        with open('test_openrice_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n  網頁內容已保存到 test_openrice_page.html（可檢查結構）")
        
        return {
            'success': True,
            'price_range': price_range,
            'price_texts_found': price_texts[:5],
            'url': url
        }
        
    except requests.exceptions.RequestException as e:
        print(f"  請求錯誤：{str(e)}")
        return {
            'success': False,
            'error': str(e),
            'url': url
        }
    except Exception as e:
        print(f"  處理錯誤：{str(e)}")
        return {
            'success': False,
            'error': str(e),
            'url': url
        }

if __name__ == "__main__":
    # 讀取資料庫
    with open('restaurants_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data.get('restaurants', [])
    
    # 找出無預算的餐廳
    no_budget_restaurants = [r for r in restaurants if r.get('budget') is None]
    
    print(f"無預算餐廳總數：{len(no_budget_restaurants)}")
    print(f"\n測試前 5 間餐廳...")
    print("=" * 60)
    
    # 測試前5間
    for i, restaurant in enumerate(no_budget_restaurants[:5], 1):
        print(f"\n第 {i} 間餐廳：")
        print(f"名稱：{restaurant['name']}")
        print(f"地址：{restaurant['address']}")
        
        url = restaurant.get('url', '')
        if url:
            result = get_restaurant_price_from_openrice(url)
            
            print(f"\n結果：")
            if result['success']:
                if result['price_range']:
                    print(f"  ✓ 找到價格區間：{result['price_range']} 元")
                else:
                    print(f"  ✗ 未找到價格區間")
                    print(f"  找到的價格相關文字：{result.get('price_texts_found', [])}")
            else:
                print(f"  ✗ 爬取失敗：{result.get('error', 'Unknown error')}")
        
        # 避免請求過快
        if i < 5:
            time.sleep(2)
