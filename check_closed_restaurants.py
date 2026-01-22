import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import Optional, Dict

def scrape_openrice_price_and_status(url: str) -> Dict:
    """
    從 OpenRice 頁面爬取價格區間資訊和餐廳狀態（是否已結業）。
    返回包含 success, price_range, is_closed 等資訊的字典。
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"正在爬取：{url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        all_text = soup.get_text()
        
        # 檢查是否已結業 - 更精確的檢測
        is_closed = False
        
        # 方法1: 檢查標題
        title = soup.find('title')
        if title:
            title_text = title.text
            if any(keyword in title_text for keyword in ['已結業', '已歇業', '已停業', '結業', '歇業']):
                is_closed = True
        
        # 方法2: 檢查頁面中的關鍵字（在特定上下文中）
        if not is_closed:
            # 查找包含"已結業"、"已歇業"等關鍵字的元素
            closed_patterns = [
                re.compile(r'已結業', re.IGNORECASE),
                re.compile(r'已歇業', re.IGNORECASE),
                re.compile(r'已停業', re.IGNORECASE),
                re.compile(r'餐廳.*已.*結業', re.IGNORECASE),
                re.compile(r'餐廳.*已.*歇業', re.IGNORECASE),
            ]
            
            for pattern in closed_patterns:
                if pattern.search(all_text):
                    # 進一步確認上下文
                    matches = pattern.findall(all_text)
                    if matches:
                        is_closed = True
                        break
        
        # 如果已結業，就不需要提取價格了
        if is_closed:
            return {
                'success': True,
                'price_range': None,
                'is_closed': True,
                'url': url
            }
        
        # 提取價格資訊（只有在未結業時才執行）
        price_texts = []
        price_patterns = [
            r'NT\$(\d+)(以上)?',
            r'(\d+)\s*[-~至]\s*(\d+)',
            r'(\d+)\s*元',
            r'NT\$(\d+)\s*[-~至]\s*NT\$(\d+)',
            r'NT\$(\d+)\s*[-~至]\s*(\d+)',
        ]
        
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
                
                # 查找 NT$XXX 單一價格格式
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
        
        # 去重
        price_texts = list(set(price_texts))
        
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
                        # 使用平均值轉換為我們的預算區間格式
                        avg_price = (min_price + max_price) / 2
                        if avg_price >= 2000:
                            price_range = "2000以上"
                        elif avg_price >= 1250:
                            price_range = "1000-1500"
                        elif avg_price >= 650:
                            price_range = "500-800"
                        elif avg_price >= 300:
                            price_range = "200-400"
                        else:
                            price_range = "200以下"
                        break
        
        return {
            'success': True,
            'price_range': price_range,
            'is_closed': False,
            'url': url
        }
        
    except requests.exceptions.RequestException as e:
        print(f"  請求錯誤：{str(e)}")
        return {
            'success': False,
            'error': str(e),
            'is_closed': False,
            'url': url
        }
    except Exception as e:
        print(f"  處理錯誤：{str(e)}")
        return {
            'success': False,
            'error': str(e),
            'is_closed': False,
            'url': url
        }

if __name__ == "__main__":
    # 載入餐廳資料
    with open('restaurants_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 找出預算為 null 的餐廳
    no_budget_restaurants = [r for r in data['restaurants'] if r.get('budget') is None]
    print(f"總共有 {len(no_budget_restaurants)} 間餐廳預算為 null。")
    print(f"處理前 100 間餐廳（這會需要一些時間，每間約2-3秒）...\n")
    print("=" * 80)
    
    closed_restaurants = []
    processed_count = 0
    success_count = 0
    closed_count = 0
    no_price_count = 0
    
    # 處理前100間
    for i, restaurant in enumerate(no_budget_restaurants[:100], 1):
        print(f"\n第 {i} 間餐廳：")
        print(f"名稱：{restaurant['name']}")
        print(f"地址：{restaurant['address']}")
        
        url = restaurant.get('url')
        if not url:
            print(f"  ✗ 沒有 URL，跳過")
            continue
        
        result = scrape_openrice_price_and_status(url)
        processed_count += 1
        
        if result['is_closed']:
            print(f"  ⚠️  餐廳已結業！")
            closed_restaurants.append({
                'name': restaurant['name'],
                'address': restaurant['address'],
                'url': url
            })
            closed_count += 1
        elif result['success'] and result.get('price_range'):
            print(f"  ✓ 找到價格區間：{result['price_range']} 元")
            success_count += 1
        elif result['success']:
            print(f"  ✗ 未找到價格區間")
            no_price_count += 1
        else:
            print(f"  ✗ 爬取失敗：{result.get('error', '未知錯誤')}")
            no_price_count += 1
        
        # 避免請求過快（減少延遲以提高速度）
        if i < 100:
            time.sleep(1)  # 減少到1秒
    
    # 輸出統計結果
    print("\n" + "=" * 80)
    print("\n處理完成！統計結果：")
    print(f"總共處理：{processed_count} 間")
    print(f"已結業：{closed_count} 間")
    print(f"成功找到價格：{success_count} 間")
    print(f"未找到價格：{no_price_count} 間")
    
    # 輸出已結業餐廳名單
    if closed_restaurants:
        print("\n" + "=" * 80)
        print(f"\n⚠️  已結業餐廳名單（共 {len(closed_restaurants)} 間）：\n")
        for i, rest in enumerate(closed_restaurants, 1):
            print(f"{i}. {rest['name']}")
            print(f"   地址：{rest['address']}")
            print(f"   URL: {rest['url']}")
            print()
    else:
        print("\n✓ 沒有發現已結業的餐廳。")
