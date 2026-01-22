#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試從 OpenRice 頁面爬取預算資訊
測試餐廳：小滿苑燒肉
"""

import requests
from bs4 import BeautifulSoup

# 測試餐廳 URL
TEST_URL = "https://s.openrice.com/cHRSm02Q2m700"

# priceRangeId 對應關係
PRICE_RANGE_MAP = {
    '1': '100以下',      # 100元以內
    '2': '100-200',      # 100-200元
    '3': '200-500',      # 200-500元
    '4': '500-1000',     # 500-1000元
    '5': '1000-1500',    # 1000-1500元
    '6': '1500以上'      # 1500元以上
}

def scrape_budget_from_openrice(url: str) -> str:
    """
    從 OpenRice URL 爬取預算資訊
    
    Args:
        url: OpenRice 餐廳頁面 URL
        
    Returns:
        預算字串，例如 "200-500" 或 None
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
            return None
        
        print("✅ 找到 pdhs-filter-tags-section")
        
        # 在該 section 中查找所有 <a> 元素
        links = filter_section.find_all('a', href=True)
        print(f"   找到 {len(links)} 個 <a> 元素")
        
        # 查找包含 priceRangeId= 的連結
        price_range_id = None
        for link in links:
            href = link.get('href', '')
            if 'priceRangeId=' in href:
                # 提取 priceRangeId 的值
                try:
                    # 從 href 中提取 priceRangeId=後面的數字
                    parts = href.split('priceRangeId=')
                    if len(parts) > 1:
                        price_range_id = parts[1].split('&')[0].split('#')[0]
                        print(f"   ✅ 找到 priceRangeId={price_range_id}")
                        print(f"   完整連結：{href[:100]}...")
                        break
                except Exception as e:
                    print(f"   ⚠️  解析 priceRangeId 時出錯：{e}")
                    continue
        
        if not price_range_id:
            print("❌ 找不到包含 priceRangeId= 的連結")
            # 輸出所有連結供調試
            print("\n所有找到的連結：")
            for i, link in enumerate(links[:10], 1):
                print(f"   {i}. {link.get('href', '')[:80]}")
            return None
        
        # 轉換為預算範圍
        budget = PRICE_RANGE_MAP.get(price_range_id)
        
        if budget:
            print(f"✅ 預算範圍：{budget} 元")
            return budget
        else:
            print(f"❌ 未知的 priceRangeId：{price_range_id}")
            return None
        
    except Exception as e:
        print(f"❌ 錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("測試爬取小滿苑燒肉的預算資訊")
    print("=" * 60)
    print()
    
    budget = scrape_budget_from_openrice(TEST_URL)
    
    print()
    print("=" * 60)
    if budget:
        print(f"✅ 測試成功！預算：{budget} 元")
    else:
        print("❌ 測試失敗，無法獲取預算資訊")
    print("=" * 60)
