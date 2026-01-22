import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import Dict, List

def check_restaurant_status(url: str) -> Dict:
    """
    檢查餐廳狀態：是否已結業或URL失效
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # 檢查是否為 404
        if response.status_code == 404:
            return {
                'success': True,
                'is_closed': False,
                'is_404': True,
                'url': url
            }
        
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
                    is_closed = True
                    break
        
        return {
            'success': True,
            'is_closed': is_closed,
            'is_404': False,
            'url': url
        }
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {
                'success': True,
                'is_closed': False,
                'is_404': True,
                'url': url
            }
        return {
            'success': False,
            'error': f"HTTP {e.response.status_code}",
            'is_closed': False,
            'is_404': False,
            'url': url
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'is_closed': False,
            'is_404': False,
            'url': url
        }

if __name__ == "__main__":
    # 載入餐廳資料
    print("載入餐廳資料...")
    with open('restaurants_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 找出預算為 null 的餐廳
    no_budget_restaurants = [r for r in data['restaurants'] if r.get('budget') is None]
    total = len(no_budget_restaurants)
    
    print(f"總共有 {total} 間餐廳預算為 null")
    print(f"開始檢查所有餐廳狀態...\n")
    print("=" * 80)
    
    closed_restaurants = []
    error_404_restaurants = []
    error_other_restaurants = []
    normal_restaurants = []
    
    # 處理所有餐廳
    for i, restaurant in enumerate(no_budget_restaurants, 1):
        print(f"[{i}/{total}] {restaurant['name'][:50]}", end=" ... ")
        
        url = restaurant.get('url')
        if not url:
            print("❌ 無URL")
            error_other_restaurants.append({
                'name': restaurant['name'],
                'address': restaurant['address'],
                'url': None,
                'error': '無URL'
            })
            continue
        
        result = check_restaurant_status(url)
        
        if result['is_404']:
            print("❌ URL失效(404)")
            error_404_restaurants.append({
                'name': restaurant['name'],
                'address': restaurant['address'],
                'url': url
            })
        elif result['is_closed']:
            print("⚠️  已結業")
            closed_restaurants.append({
                'name': restaurant['name'],
                'address': restaurant['address'],
                'url': url
            })
        elif result['success']:
            print("✓ 正常")
            normal_restaurants.append(restaurant['name'])
        else:
            print(f"❌ 檢查失敗: {result.get('error', '未知錯誤')}")
            error_other_restaurants.append({
                'name': restaurant['name'],
                'address': restaurant['address'],
                'url': url,
                'error': result.get('error', '未知錯誤')
            })
        
        # 較短的延遲
        if i < total:
            time.sleep(0.5)
        
        # 每50間顯示一次進度摘要
        if i % 50 == 0:
            print(f"\n進度: {i}/{total} ({i*100//total}%) | 已結業: {len(closed_restaurants)} | 404: {len(error_404_restaurants)} | 正常: {len(normal_restaurants)} | 其他錯誤: {len(error_other_restaurants)}\n")
    
    # 輸出最終結果
    print("\n" + "=" * 80)
    print("\n✅ 檢查完成！統計結果：")
    print(f"總共檢查：{total} 間")
    print(f"正常營業：{len(normal_restaurants)} 間")
    print(f"⚠️  已結業：{len(closed_restaurants)} 間")
    print(f"❌ URL失效(404)：{len(error_404_restaurants)} 間")
    print(f"❌ 其他錯誤（無URL或檢查失敗）：{len(error_other_restaurants)} 間")
    print(f"\n需要處理的餐廳總數：{len(closed_restaurants) + len(error_404_restaurants)} 間")
    
    # 保存結果到文件
    result_data = {
        'closed_restaurants': closed_restaurants,
        'error_404_restaurants': error_404_restaurants,
        'error_other_restaurants': error_other_restaurants,
        'summary': {
            'total': total,
            'normal': len(normal_restaurants),
            'closed': len(closed_restaurants),
            'error_404': len(error_404_restaurants),
            'error_other': len(error_other_restaurants)
        }
    }
    
    with open('restaurant_status_check.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n詳細結果已保存到：restaurant_status_check.json")
    
    # 輸出已結業餐廳名單
    if closed_restaurants:
        print("\n" + "=" * 80)
        print(f"\n⚠️  已結業餐廳名單（共 {len(closed_restaurants)} 間）：\n")
        for i, rest in enumerate(closed_restaurants, 1):
            print(f"{i}. {rest['name']}")
            print(f"   地址：{rest['address']}")
            print(f"   URL: {rest['url']}\n")
    
    # 輸出404餐廳名單
    if error_404_restaurants:
        print("\n" + "=" * 80)
        print(f"\n❌ URL失效(404)餐廳名單（共 {len(error_404_restaurants)} 間）：\n")
        for i, rest in enumerate(error_404_restaurants, 1):
            print(f"{i}. {rest['name']}")
            print(f"   地址：{rest['address']}")
            print(f"   URL: {rest['url']}\n")
