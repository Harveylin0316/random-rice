# 廣告影片放置目錄

## 命名規則
- 檔名 = `<or_id>.mp4`（建議 1080×1920 直式，5-15 秒 loop，≤ 3MB）
- Poster（封面圖，可選）= `<or_id>.jpg`

例：濟安鮨 or_id=526998 → `526998.mp4` + `526998.jpg`

## 部署後存取路徑
`https://random-rice.netlify.app/liff/videos/526998.mp4`

## 註冊到 DB
在 `_rebuild/restaurant_videos.csv` 加一列，然後跑 `python3 _rebuild/13_apply_videos.py`。
