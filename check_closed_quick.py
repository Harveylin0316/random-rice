import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import Optional, Dict

def check_restaurant_status(url: str) -> Dict:
    """
    快速檢查餐廳是否已結業
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        all_text = soup.get_text()
        
        # 檢查是否已結業
        is_closed = False
        title = soup.find('title')
        if title:
            title_text = title.text
            if any(keyword in title_text for keyword in ['已結業', '已歇業', '已停業', '結業', '歇業']):
                is_closed = True
        
        # 檢查頁面內容
        if not is_closed:
            closed_patterns = ['已結業', '已歇業', '已停業']
            for pattern in closed_patterns:
                if pattern in all_text:
                    # 簡單檢查，如果出現這些關鍵字就標記為已結業
                    is_closed = True
                    break
        
        return {
            'success': True,
            'is_closed': is_closed,
            'url': url
        }
        
    except Exception as e:
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
    total_to_process = 30  # 測試30間
    
    print(f"總共有 {len(no_budget_restaurants)} 間餐廳預算為 null。")
    print(f"快速檢查前 {total_to_process} 間餐廳是否已結業...\n")
    print("=" * 80)
    
    closed_restaurants = []
    
    # 處理前30間
    for i, restaurant in enumerate(no_budget_restaurants[:total_to_process], 1):
        print(f"[{i}/{total_to_process}] {restaurant['name']}", end=" ... ")
        
        url = restaurant.get('url')
        if not url:
            print("❌ 無URL")
            continue
        
        result = check_restaurant_status(url)
        
        if result['is_closed']:
            print("⚠️  已結業")
            closed_restaurants.append({
                'name': restaurant['name'],
                'address': restaurant['address'],
                'url': url
            })
        elif result['success']:
            print("✓ 正常營業")
        else:
            print(f"❌ 檢查失敗: {result.get('error', '未知錯誤')}")
        
        # 較短的延遲
        if i < total_to_process:
            time.sleep(0.5)
        
        # 每5間顯示一次進度摘要
        if i % 5 == 0:
            print(f"\n進度: {i}/{total_to_process} ({i*100//total_to_process}%) | 已結業: {len(closed_restaurants)} 間\n")
    
    # 輸出結果
    print("\n" + "=" * 80)
    print(f"\n✅ 處理完成！")
    print(f"總共檢查：{total_to_process} 間")
    print(f"已結業：{len(closed_restaurants)} 間")
    print(f"正常營業：{total_to_process - len(closed_restaurants)} 間")
    
    if closed_restaurants:
        print("\n" + "=" * 80)
        print(f"\n⚠️  已結業餐廳名單（共 {len(closed_restaurants)} 間）：\n")
        for i, rest in enumerate(closed_restaurants, 1):
            print(f"{i}. {rest['name']}")
            print(f"   地址：{rest['address']}")
            print(f"   URL: {rest['url']}\n")
    else:
        print("\n✓ 沒有發現已結業的餐廳。")
