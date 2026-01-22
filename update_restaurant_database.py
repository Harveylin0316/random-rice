import json
from typing import List, Dict, Set

def load_status_check_results(status_file: str) -> Dict:
    """載入檢查結果"""
    with open(status_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_restaurant_database(db_file: str) -> Dict:
    """載入餐廳資料庫"""
    with open(db_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_restaurants_to_remove(status_data: Dict) -> Set[str]:
    """獲取需要移除的餐廳 URL 集合"""
    to_remove = set()
    
    # 已結業的餐廳
    for rest in status_data.get('closed_restaurants', []):
        if rest.get('url'):
            to_remove.add(rest['url'])
    
    # URL失效(404)的餐廳
    for rest in status_data.get('error_404_restaurants', []):
        if rest.get('url'):
            to_remove.add(rest['url'])
    
    # 其他錯誤的餐廳（有URL的）
    for rest in status_data.get('error_other_restaurants', []):
        if rest.get('url'):
            to_remove.add(rest['url'])
    
    return to_remove

def remove_restaurants(db_data: Dict, urls_to_remove: Set[str]) -> tuple[Dict, List[Dict]]:
    """從資料庫中移除指定URL的餐廳"""
    original_count = len(db_data['restaurants'])
    removed_restaurants = []
    remaining_restaurants = []
    
    for restaurant in db_data['restaurants']:
        restaurant_url = restaurant.get('url')
        if restaurant_url and restaurant_url in urls_to_remove:
            removed_restaurants.append(restaurant)
        else:
            remaining_restaurants.append(restaurant)
    
    db_data['restaurants'] = remaining_restaurants
    new_count = len(remaining_restaurants)
    
    return db_data, removed_restaurants

def save_restaurant_database(db_data: Dict, output_file: str):
    """保存更新後的餐廳資料庫"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

def main():
    print("=" * 80)
    print("開始更新餐廳資料庫...")
    print("=" * 80)
    
    # 載入檢查結果
    print("\n1. 載入檢查結果...")
    status_data = load_status_check_results('restaurant_status_check.json')
    summary = status_data.get('summary', {})
    print(f"   檢查結果摘要：")
    print(f"   - 已結業：{summary.get('closed', 0)} 間")
    print(f"   - URL失效(404)：{summary.get('error_404', 0)} 間")
    print(f"   - 其他錯誤：{summary.get('error_other', 0)} 間")
    
    # 獲取需要移除的餐廳URL
    print("\n2. 識別需要移除的餐廳...")
    urls_to_remove = get_restaurants_to_remove(status_data)
    print(f"   需要移除的餐廳：{len(urls_to_remove)} 間")
    
    # 載入餐廳資料庫
    print("\n3. 載入餐廳資料庫...")
    db_data = load_restaurant_database('restaurants_database.json')
    original_count = len(db_data['restaurants'])
    print(f"   原始餐廳數量：{original_count} 間")
    
    # 移除餐廳
    print("\n4. 移除已結業和URL失效的餐廳...")
    updated_db, removed_list = remove_restaurants(db_data, urls_to_remove)
    new_count = len(updated_db['restaurants'])
    print(f"   移除餐廳數量：{len(removed_list)} 間")
    print(f"   更新後餐廳數量：{new_count} 間")
    
    # 保存備份
    print("\n5. 創建備份...")
    backup_file = 'restaurants_database_backup.json'
    save_restaurant_database(db_data, backup_file)
    print(f"   備份已保存到：{backup_file}")
    
    # 保存更新後的資料庫
    print("\n6. 保存更新後的資料庫...")
    save_restaurant_database(updated_db, 'restaurants_database.json')
    print(f"   更新後的資料庫已保存到：restaurants_database.json")
    
    # 顯示移除的餐廳名單
    print("\n" + "=" * 80)
    print(f"\n✅ 更新完成！")
    print(f"\n統計：")
    print(f"   - 原始餐廳數：{original_count} 間")
    print(f"   - 移除餐廳數：{len(removed_list)} 間")
    print(f"   - 更新後餐廳數：{new_count} 間")
    
    if removed_list:
        print(f"\n已移除的餐廳名單（前10間）：")
        for i, rest in enumerate(removed_list[:10], 1):
            print(f"   {i}. {rest['name']}")
        if len(removed_list) > 10:
            print(f"   ... 還有 {len(removed_list) - 10} 間餐廳")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
