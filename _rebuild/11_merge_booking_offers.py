#!/usr/bin/env python3
"""
把 booking_offers.xlsx「餐廳彙總」merge 進主 DB。
標記每家有訂位優惠的餐廳：booking_offers (list of titles), booking_offer_count, has_booking_offer
"""
import openpyxl
import json
import os

SRC = '/Users/harveylin/Desktop/Claude-workspace/projects/openrice-crawler/exports/booking_offers.xlsx'
MAIN_DB = 'restaurants_database.json'
NETLIFY_DB = 'netlify/functions/restaurants_database.json'


def load_offers():
    """讀「餐廳彙總」sheet。
    結構：row 0 是 super-header「按餐廳彙總 (17 家)」/ row 1 是 真實 header / row 2+ 是 data
    """
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb['餐廳彙總']
    rows = list(ws.iter_rows(values_only=True))
    header = rows[1]  # 真實 header
    idx = {h: i for i, h in enumerate(header) if h}
    records = []
    for r in rows[2:]:
        if not r[0]: continue  # 空 row 跳過
        poi_id = int(r[idx['POI ID']])
        titles_raw = r[idx['優惠標題彙總']] or ''
        # 優惠標題用換行分隔
        titles = [t.strip() for t in str(titles_raw).split('\n') if t.strip()]
        records.append({
            'or_id': poi_id,
            'name': r[idx['餐廳']],
            'offer_count': r[idx['優惠數']] or len(titles),
            'offer_titles': titles,
        })
    return records


def main():
    offers = load_offers()
    print(f'讀到 {len(offers)} 家有訂位優惠的餐廳')
    offers_by_id = {o['or_id']: o for o in offers}

    with open(MAIN_DB, encoding='utf-8') as f:
        data = json.load(f)
    restaurants = data['restaurants']

    matched = 0
    not_found = []
    for r in restaurants:
        oid = r.get('or_id')
        if oid in offers_by_id:
            o = offers_by_id[oid]
            r['has_booking_offer'] = True
            r['booking_offers'] = o['offer_titles']
            r['booking_offer_count'] = int(o['offer_count'])
            matched += 1
        else:
            # 確保未匹配的也乾淨
            r.pop('has_booking_offer', None)
            r.pop('booking_offers', None)
            r.pop('booking_offer_count', None)

    not_found = [o for o in offers if o['or_id'] not in {r.get('or_id') for r in restaurants}]
    print(f'  matched: {matched}/{len(offers)}')
    if not_found:
        print(f'  NOT FOUND in DB:')
        for o in not_found:
            print(f'    [{o["or_id"]}] {o["name"]}')

    # 寫回
    with open(MAIN_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(NETLIFY_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'\n寫入 {MAIN_DB}  ({os.path.getsize(MAIN_DB)//1024} KB)')

    # 樣本
    print(f'\n樣本（有優惠的店）：')
    for r in restaurants[:3000]:
        if r.get('has_booking_offer'):
            print(f"  [{r['or_id']}] {r['name']}: {r['booking_offer_count']} 項")
            for t in r['booking_offers'][:2]:
                print(f"    - {t[:60]}")
            print()
            if matched > 5: break


if __name__ == '__main__':
    main()
