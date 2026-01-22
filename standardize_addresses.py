#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
標準化餐廳地址，提取並統一縣市和行政區
"""

import json
import re
from typing import Dict, Optional

# 縣市名稱對照表（統一格式）
CITY_NORMALIZATION = {
    '臺北市': '台北市',
    '台灣台北市': '台北市',
    '臺中市': '台中市',
    '臺南市': '台南市',
    '新北市': '新北市',
    '高雄市': '高雄市',
    '台灣高雄市': '高雄市',
    '桃園市': '桃園市',
    '新竹市': '新竹市',
    '基隆市': '基隆市',
    '嘉義市': '嘉義市',
    '宜蘭縣': '宜蘭縣',
    '新竹縣': '新竹縣',
    '苗栗縣': '苗栗縣',
    '彰化縣': '彰化縣',
    '南投縣': '南投縣',
    '雲林縣': '雲林縣',
    '嘉義縣': '嘉義縣',
    '屏東縣': '屏東縣',
    '屏東市': '屏東縣',  # 屏東市屬於屏東縣
    '花蓮縣': '花蓮縣',
    '花蓮市': '花蓮縣',  # 花蓮市屬於花蓮縣
    '台東縣': '台東縣',
    '澎湖縣': '澎湖縣',
    '金門縣': '金門縣',
    '連江縣': '連江縣',
    '員林市': '彰化縣',  # 員林市屬於彰化縣
    '竹北市': '新竹縣',  # 竹北市屬於新竹縣
    '松山區市': '台北市',  # 錯誤格式，應該是台北市
}

def parse_address(address: str) -> Dict[str, Optional[str]]:
    """
    解析地址，提取標準化的縣市和行政區
    
    Args:
        address: 餐廳地址字串
        
    Returns:
        {
            'city': str or None,      # 標準化的縣市名稱
            'district': str or None   # 行政區名稱
        }
    """
    if not address:
        return {'city': None, 'district': None}
    
    # 行政區到縣市的對照表（處理只有行政區的情況）
    DISTRICT_TO_CITY = {
        # 台北市
        '大安區': '台北市',
        '信義區': '台北市',
        '中正區': '台北市',
        '中山區': '台北市',
        '松山區': '台北市',
        '萬華區': '台北市',
        '士林區': '台北市',
        '內湖區': '台北市',
        '南港區': '台北市',
        '文山區': '台北市',
        '北投區': '台北市',
        '大同區': '台北市',
        # 新北市
        '板橋區': '新北市',
        '三重區': '新北市',
        '中和區': '新北市',
        '永和區': '新北市',
        '新店區': '新北市',
        '新莊區': '新北市',
        '土城區': '新北市',
        '樹林區': '新北市',
        '淡水區': '新北市',
        '汐止區': '新北市',
        '蘆洲區': '新北市',
        '三峽區': '新北市',
        '林口區': '新北市',
        '泰山區': '新北市',
        '橋區': '新北市',  # 可能是「板橋區」的簡寫
        # 台中市
        '西區': '台中市',
        '北區': '台中市',
        '南區': '台中市',
        '東區': '台中市',
        '中區': '台中市',
        '西屯區': '台中市',
        '南屯區': '台中市',
        '北屯區': '台中市',
        '豐原區': '台中市',
        '大甲區': '台中市',
        '沙鹿區': '台中市',
        '龍井區': '台中市',
        '烏日區': '台中市',
        '后里區': '台中市',
        '大里區': '台中市',
        # 高雄市
        '左營區': '高雄市',
        '苓雅區': '高雄市',
        '前金區': '高雄市',
        '前鎮區': '高雄市',
        '鹽埕區': '高雄市',
        '三民區': '高雄市',
        '新興區': '高雄市',
        '小港區': '高雄市',
        '楠梓區': '高雄市',
        '鼓山區': '高雄市',
        '岡山區': '高雄市',
        '鳥松區': '高雄市',
        # 桃園市
        '中壢區': '桃園市',
        '桃園區': '桃園市',
        '八德區': '桃園市',
        '龜山區': '桃園市',
        '蘆竹區': '桃園市',
        '大園區': '桃園市',
        '楊梅區': '桃園市',
        # 台南市
        '中西區': '台南市',
        '東區': '台南市',
        '北區': '台南市',
        '安平區': '台南市',
        '安南區': '台南市',
        '永康區': '台南市',
        '新化區': '台南市',
        '新市區': '台南市',
        '平安區': '台南市',
        # 基隆市
        '中正區': '基隆市',  # 注意：基隆市也有中正區
        '仁愛區': '基隆市',
        '信義區': '基隆市',
        # 新竹市
        '北區': '新竹市',
        '東區': '新竹市',
        '香山區': '新竹市',
        # 嘉義市
        '西區': '嘉義市',
        # 其他縣市（鄉鎮市區）
        '竹北市': '新竹縣',
        '員林市': '彰化縣',
        '鹿港鎮': '彰化縣',
        '羅東鎮': '宜蘭縣',
        '礁溪鄉': '宜蘭縣',
        '宜蘭市': '宜蘭縣',
        '冬山鄉': '宜蘭縣',
        '頭城鎮': '宜蘭縣',
        '五結鄉': '宜蘭縣',
        '花蓮市': '花蓮縣',
        '新城鄉': '花蓮縣',
        '秀林鄉': '花蓮縣',
        '東港鎮': '屏東縣',
        '琉球鄉': '屏東縣',
        '恆春鎮': '屏東縣',
        '屏東市': '屏東縣',
        '馬公市': '澎湖縣',
        '五德里': '澎湖縣',  # 澎湖縣馬公市五德里
        '南投市': '南投縣',
        '苗栗市': '苗栗縣',
        '斗六市': '雲林縣',
        '尖石鄉': '新竹縣',
    }
    
    # 先嘗試匹配：郵遞區號 + 行政區（例如：231新店區）
    pattern0 = r'^\d{3}([^區]+區)'
    match = re.search(pattern0, address)
    if match:
        district = match.group(1).strip()
        city = DISTRICT_TO_CITY.get(district)
        if city:
            return {'city': city, 'district': district}
    
    # 先嘗試匹配：郵遞區號 + 縣市 + 行政區
    # 改進：更精確的匹配，先移除郵遞區號
    pattern1 = r'(?:^\d{0,6})?([^市縣]+[市縣])([^區]+區)'
    match = re.search(pattern1, address)
    
    if match:
        city_raw = match.group(1).strip()
        district = match.group(2).strip()
        
        # 標準化縣市名稱（移除郵遞區號前綴）
        # 處理格式：'100台北市' -> '台北市'
        city_clean = re.sub(r'^\d+', '', city_raw).strip()
        city = CITY_NORMALIZATION.get(city_clean, city_clean)
        
        return {'city': city, 'district': district}
    
    # 如果沒有匹配到，嘗試只匹配縣市（移除郵遞區號）
    pattern2 = r'(?:^\d{0,6})?([^市縣]+[市縣])'
    match = re.search(pattern2, address)
    
    if match:
        city_raw = match.group(1).strip()
        # 移除郵遞區號前綴
        city_clean = re.sub(r'^\d+', '', city_raw).strip()
        city = CITY_NORMALIZATION.get(city_clean, city_clean)
        
        # 嘗試在縣市後面找行政區
        district_match = re.search(city + r'([^區]+區)', address)
        if district_match:
            district = district_match.group(1).strip()
            return {'city': city, 'district': district}
        
        # 嘗試匹配鄉鎮市區（例如：竹北市、員林市、羅東鎮等）
        # 這些通常緊跟在縣市名稱後面
        town_match = re.search(city + r'([^市鎮鄉]+[市鎮鄉])', address)
        if town_match:
            town = town_match.group(1).strip()
            # 檢查是否是已知的鄉鎮市區
            if DISTRICT_TO_CITY.get(town) == city:
                return {'city': city, 'district': town}
        
        return {'city': city, 'district': None}
    
    # 如果都沒有，嘗試只匹配行政區（處理只有行政區的情況）
    # 先匹配「區」
    pattern3 = r'([^區]+區)'
    match = re.search(pattern3, address)
    
    if match:
        district = match.group(1).strip()
        # 根據行政區推斷縣市
        city = DISTRICT_TO_CITY.get(district)
        if city:
            return {'city': city, 'district': district}
        return {'city': None, 'district': district}
    
    # 嘗試匹配「市」、「鎮」、「鄉」（處理鄉鎮市區）
    pattern4 = r'([^市鎮鄉]+[市鎮鄉])'
    match = re.search(pattern4, address)
    
    if match:
        location = match.group(1).strip()
        # 檢查是否是已知的鄉鎮市區
        city = DISTRICT_TO_CITY.get(location)
        if city:
            return {'city': city, 'district': location}
        # 檢查是否是縣市名稱
        city_normalized = CITY_NORMALIZATION.get(location, location)
        if city_normalized.endswith('市') or city_normalized.endswith('縣'):
            return {'city': city_normalized, 'district': None}
    
    # 處理特殊情況：地址開頭有郵遞區號但沒有縣市名稱
    # 例如：「231新店區」-> 應該是「新北市新店區」
    postal_code_match = re.match(r'^(\d{3})([^區]+區)', address)
    if postal_code_match:
        postal_code = postal_code_match.group(1)
        district = postal_code_match.group(2).strip()
        # 根據郵遞區號和行政區推斷縣市
        city = DISTRICT_TO_CITY.get(district)
        if city:
            return {'city': city, 'district': district}
    
    return {'city': None, 'district': None}

def standardize_addresses(json_file: str):
    """
    標準化所有餐廳的地址，添加 city 和 district 欄位
    """
    print("=" * 80)
    print("開始標準化餐廳地址...")
    print("=" * 80)
    
    # 載入資料庫
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    restaurants = data['restaurants']
    total = len(restaurants)
    
    updated_count = 0
    no_city_count = 0
    no_district_count = 0
    
    print(f"\n總餐廳數：{total} 間")
    print(f"開始處理...\n")
    
    # 統計縣市和行政區
    city_district_map = {}
    
    for i, restaurant in enumerate(restaurants, 1):
        address = restaurant.get('address', '')
        
        # 如果已經有 city 和 district，且都不為空，跳過
        existing_city = restaurant.get('city')
        existing_district = restaurant.get('district')
        
        # 只處理缺失的資料
        if not existing_city or (existing_city and not existing_district):
            result = parse_address(address)
            
            city = result['city']
            district = result['district']
            
            # 更新餐廳資料（只更新缺失的部分）
            if not existing_city and city:
                restaurant['city'] = city
            if existing_city and not existing_district and district:
                restaurant['district'] = district
            elif not existing_city and city and district:
                restaurant['city'] = city
                restaurant['district'] = district
        else:
            # 已經有完整資料，使用現有資料
            city = existing_city
            district = existing_district
        
        if city:
            updated_count += 1
            if city not in city_district_map:
                city_district_map[city] = set()
            if district:
                city_district_map[city].add(district)
                no_district_count += 1
        else:
            no_city_count += 1
        
        if i % 100 == 0:
            print(f"[{i}/{total}] 已處理...")
    
    # 保存更新後的資料庫
    print("\n" + "=" * 80)
    print("保存更新後的資料庫...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 統計結果
    print("\n" + "=" * 80)
    print("✅ 處理完成！")
    print(f"\n統計：")
    print(f"  總餐廳數：{total} 間")
    print(f"  有縣市：{updated_count} 間 ({updated_count/total*100:.1f}%)")
    print(f"  無縣市：{no_city_count} 間 ({no_city_count/total*100:.1f}%)")
    print(f"  有行政區：{no_district_count} 間 ({no_district_count/total*100:.1f}%)")
    
    print(f"\n縣市分布：")
    for city in sorted(city_district_map.keys()):
        districts = sorted(city_district_map[city])
        print(f"  {city}: {len(districts)} 個行政區")
        if len(districts) <= 10:
            print(f"    {districts}")
        else:
            print(f"    {districts[:10]}... (共{len(districts)}個)")
    
    print("=" * 80)

if __name__ == "__main__":
    standardize_addresses('restaurants_database.json')
