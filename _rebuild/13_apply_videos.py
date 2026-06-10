#!/usr/bin/env python3
"""
讀 _rebuild/restaurant_videos.csv，把廣告影片資訊 merge 進主 DB。

每家有影片的餐廳會加上：
  video_url:       MP4 路徑（必填）
  video_poster:    封面圖（可選；空白則前端 fallback 用第一張 image）
  video_reel_url:  IG Reel 連結（可選；點影片時跳轉）
  has_video:       true（方便 query）

加完後同步寫到 netlify/functions/restaurants_database.json。
"""
import csv
import json
import os

CSV_PATH = '_rebuild/restaurant_videos.csv'
MAIN_DB = 'restaurants_database.json'
NETLIFY_DB = 'netlify/functions/restaurants_database.json'


def load_video_manifest():
    """讀 manifest CSV，忽略 # 開頭的註解行。"""
    if not os.path.exists(CSV_PATH):
        print(f'!! manifest 不存在: {CSV_PATH}')
        return []
    records = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        # 過濾掉註解行
        lines = [ln for ln in f if not ln.lstrip().startswith('#')]
    reader = csv.DictReader(lines)
    for row in reader:
        if not row.get('or_id') or not row['or_id'].strip().isdigit():
            continue
        records.append({
            'or_id': int(row['or_id']),
            'video_url': (row.get('video_url') or '').strip(),
            'video_poster': (row.get('video_poster') or '').strip(),
            'video_reel_url': (row.get('video_reel_url') or '').strip(),
        })
    return records


def main():
    videos = load_video_manifest()
    print(f'讀到 {len(videos)} 筆影片 manifest')

    with open(MAIN_DB, 'r', encoding='utf-8') as f:
        db = json.load(f)

    by_id = {r['or_id']: r for r in db['restaurants']}

    # 先把舊的 video_* 欄位清掉（避免移除後 manifest 沒同步）
    cleared = 0
    for r in db['restaurants']:
        if any(k in r for k in ('video_url', 'video_poster', 'video_reel_url', 'has_video')):
            for k in ('video_url', 'video_poster', 'video_reel_url', 'has_video'):
                r.pop(k, None)
            cleared += 1
    if cleared:
        print(f'  清除 {cleared} 家舊 video_* 欄位')

    matched = 0
    missed = []
    for v in videos:
        r = by_id.get(v['or_id'])
        if not r:
            missed.append(v['or_id'])
            continue
        if not v['video_url']:
            continue
        r['video_url'] = v['video_url']
        r['has_video'] = True
        if v['video_poster']:
            r['video_poster'] = v['video_poster']
        if v['video_reel_url']:
            r['video_reel_url'] = v['video_reel_url']
        matched += 1

    print(f'  matched: {matched}/{len(videos)}')
    if missed:
        print(f'  !! 在主 DB 找不到的 or_id: {missed}')

    # 寫主 DB
    with open(MAIN_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f'寫入 {MAIN_DB}')

    # 同步 netlify 副本
    os.makedirs(os.path.dirname(NETLIFY_DB), exist_ok=True)
    with open(NETLIFY_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f'寫入 {NETLIFY_DB}')

    # 顯示樣本
    print('\n樣本（有影片的店）：')
    sample_count = 0
    for r in db['restaurants']:
        if r.get('has_video'):
            print(f"  [{r['or_id']}] {r['name']}: {r['video_url']}")
            sample_count += 1
            if sample_count >= 5: break


if __name__ == '__main__':
    main()
