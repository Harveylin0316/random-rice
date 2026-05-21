# Random Rice — LIFF 用戶行為資料 接入指南

> 給「LINE CRM 後台」整合用。本文目的：讓 CRM 系統從同一個 Supabase 表讀取 Random Rice LIFF 的用戶行為資料，做即時觀察、漏斗分析、留存追蹤。

## 1. 系統概覽

**Random Rice** 是一個 LINE LIFF App「今天吃什麼？」，使用者打開 LIFF → 篩選條件 → 擲骰子隨機抽到一家餐廳 → 點查看餐廳 / 訂位（跳轉 OpenRice）。每抽 4 次會插入一張「OpenRice 小知識」廣告卡（4 個輪播：獨家優惠 / 訂位回饋 / 冷門折扣 / IG 追蹤）。

**用戶旅程的主要轉換點**：`submit_draw → result_shown → restaurant_click`（從抽到的店點進 OpenRice 訂位）。

## 2. 資料源

### Supabase 表：`user_events`

```sql
CREATE TABLE user_events (
  id BIGSERIAL PRIMARY KEY,
  -- 識別
  line_id TEXT,                       -- LINE userId，dev 模式為 NULL
  session_id TEXT NOT NULL,           -- 本次 LIFF 開啟的 session uuid（前端生成）
  -- 事件
  event_name TEXT NOT NULL,           -- 見下方事件清單
  properties JSONB DEFAULT '{}',      -- 事件參數（or_id、餐廳名、廣告 id 等）
  -- 環境
  is_in_line BOOLEAN,                 -- 是否在 LINE webview 內
  os TEXT,                            -- liff.getOS()
  language TEXT,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);
```

### 連接方式

- **Supabase URL**：`SUPABASE_URL`（與 Random Rice 同個 project）
- **權限**：CRM 用 `service_role` key 讀取（後端用）；前端勿暴露
- **REST API**：`GET {SUPABASE_URL}/rest/v1/user_events?...`
- 索引：`line_id`、`session_id`、`event_name`、`created_at` 都有

## 3. 事件清單（共 9 種）

| event_name | 觸發時機 | properties 主要欄位 |
|---|---|---|
| `app_open` | LIFF 初始化完成、進入頁面 | `logged_in: bool`，`dev: bool`（dev 旁路模式） |
| `submit_draw` | 使用者首次按下「擲骰子，抽一家」 | `cuisine_style`, `budget`, `diningTime`, `city`, `district`, `location_mode` (nearby/area), `transport` (walking/driving) |
| `result_shown` | 餐廳卡渲染出來 | `or_id` (OpenRice 餐廳 ID), `name`, `draw_count` (本 session 第幾次) |
| `redraw` | 使用者按「再抽一次」 | `current_draw_count` (按下時已抽的次數) |
| `ad_shown` | 廣告卡顯示（每 4 次抽自動觸發） | `ad_title` (獨家優惠 / 訂位現金回饋 / 冷門時段折扣 / 追蹤 OpenRice IG), `ad_icon` |
| `ad_cta_click` | 廣告卡 CTA 按鈕點擊（目前只有 IG 廣告有） | `ad_title`, `url` |
| `share_click` | 餐廳卡分享按鈕點擊 | `or_id`, `name` |
| `restaurant_click` | **點「查看 / 訂位」按鈕**（核心轉換點） | `or_id`, `name`, `url`, `draw_count` |
| `navigation_click` | 點「導航」按鈕（Google Maps） | `or_id`, `name` |

**識別建議**：
- 同一個 LIFF 開啟期間共用一個 `session_id`
- 同一個 LINE 用戶跨 session 用 `line_id` 串聯
- `restaurant_click` 是 OpenRice 賺佣金的關鍵 → 主要 KPI

## 4. 推薦的 CRM 後台 dashboard 視圖

### 4.1 即時概覽（單張卡）
- 今日 DAU（distinct `line_id`）
- 今日總抽次數（`submit_draw` + `redraw`）
- 今日點進餐廳訂位次數（`restaurant_click`）
- 今日抽 → 點訂位 轉換率（`restaurant_click` / `result_shown`）

### 4.2 核心轉換漏斗（柱狀圖）

```
app_open → submit_draw → result_shown → restaurant_click
```
每一步顯示人數與流失率。

### 4.3 趨勢圖（折線）
- 過去 7/30 天的 DAU、總抽次數、轉換率

### 4.4 廣告效果（表格）
- 各 ad_title 的 `ad_shown` / `ad_cta_click` 計數
- IG 廣告 CTR（重點觀察）

### 4.5 熱門餐廳（表格）
- `restaurant_click` 數最多的 top 20 餐廳
- 與 `result_shown` 比對得到「被抽到時的轉換率」

### 4.6 用戶細節頁（依 `line_id` 查詢）
- 該用戶總開啟次數、總抽次數、點過幾家
- 旅程時間軸（按 `created_at` 排序所有事件）
- 喜好分析（從 `submit_draw` properties 看常選的料理/預算）

## 5. 常用 SQL 查詢

### 每日 DAU
```sql
SELECT DATE(created_at) AS day, COUNT(DISTINCT line_id) AS dau
FROM user_events
WHERE event_name = 'app_open' AND line_id IS NOT NULL
GROUP BY 1 ORDER BY 1 DESC LIMIT 30;
```

### 抽 → 點訂位 轉換漏斗（近 7 天）
```sql
SELECT
  COUNT(*) FILTER (WHERE event_name = 'submit_draw') AS submitted,
  COUNT(*) FILTER (WHERE event_name = 'result_shown') AS shown,
  COUNT(*) FILTER (WHERE event_name = 'restaurant_click') AS clicked,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE event_name = 'restaurant_click')
    / NULLIF(COUNT(*) FILTER (WHERE event_name = 'result_shown'), 0),
    2
  ) AS click_through_rate_pct
FROM user_events
WHERE created_at > NOW() - INTERVAL '7 days';
```

### 哪些餐廳最常被點進去
```sql
SELECT properties->>'name' AS restaurant,
       properties->>'or_id' AS or_id,
       COUNT(*) AS clicks
FROM user_events
WHERE event_name = 'restaurant_click'
GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 20;
```

### 每個用戶平均抽幾次才點訂位（session 維度）
```sql
WITH per_session AS (
  SELECT session_id,
    COUNT(*) FILTER (WHERE event_name = 'result_shown') AS draws,
    COUNT(*) FILTER (WHERE event_name = 'restaurant_click') AS clicks
  FROM user_events
  WHERE created_at > NOW() - INTERVAL '30 days'
  GROUP BY session_id
)
SELECT
  AVG(draws) FILTER (WHERE clicks > 0) AS avg_draws_before_click,
  AVG(draws) FILTER (WHERE clicks = 0) AS avg_draws_no_click,
  COUNT(*) FILTER (WHERE clicks > 0)::float / COUNT(*) AS session_conversion_rate
FROM per_session;
```

### 廣告 CTR
```sql
SELECT
  properties->>'ad_title' AS ad,
  COUNT(*) FILTER (WHERE event_name = 'ad_shown') AS shown,
  COUNT(*) FILTER (WHERE event_name = 'ad_cta_click') AS clicked,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE event_name = 'ad_cta_click')
    / NULLIF(COUNT(*) FILTER (WHERE event_name = 'ad_shown'), 0),
    2
  ) AS ctr_pct
FROM user_events
WHERE event_name IN ('ad_shown', 'ad_cta_click')
  AND created_at > NOW() - INTERVAL '30 days'
GROUP BY 1;
```

### 篩選條件偏好（什麼料理 / 預算最受歡迎）
```sql
SELECT
  properties->>'cuisine_style' AS cuisine,
  COUNT(*) AS picks
FROM user_events
WHERE event_name = 'submit_draw'
  AND properties->>'cuisine_style' IS NOT NULL
GROUP BY 1 ORDER BY 2 DESC;
```

### 留存：7 日後回訪
```sql
WITH first_open AS (
  SELECT line_id, MIN(DATE(created_at)) AS first_day
  FROM user_events
  WHERE event_name = 'app_open' AND line_id IS NOT NULL
  GROUP BY line_id
),
return_7d AS (
  SELECT DISTINCT u.line_id
  FROM user_events u
  JOIN first_open f ON f.line_id = u.line_id
  WHERE u.event_name = 'app_open'
    AND DATE(u.created_at) BETWEEN f.first_day + 7 AND f.first_day + 13
)
SELECT
  COUNT(*) AS total_users,
  COUNT(r.line_id) AS retained_7d,
  ROUND(100.0 * COUNT(r.line_id) / COUNT(*), 2) AS retention_7d_pct
FROM first_open f
LEFT JOIN return_7d r ON r.line_id = f.line_id;
```

### 單一用戶旅程（CRM 個資頁用）
```sql
SELECT created_at, event_name, properties
FROM user_events
WHERE line_id = $1
ORDER BY created_at DESC
LIMIT 200;
```

## 6. CRM 整合建議

### 6.1 串到既有用戶資料
Random Rice 跟 LINE OA 共用 LINE userId (`line_id`)。CRM 後台應該已有用戶 master 表，把 `user_events.line_id` 當外鍵 join 即可。

### 6.2 即時 vs 批次
- 即時觀察（最近 30 分鐘）：直接 query `user_events`，已有 `idx_user_events_created_at` 索引
- 批次報表：建議每天清晨 ETL 一次，做成 materialized view 或 daily snapshot 表

### 6.3 警示建議（後續加值）
- DAU 突然下跌 30% → 告警
- 轉換率連續 3 天下跌 → 告警
- 某個餐廳訂位點擊突然激增 → 可能熱門事件，通知運營

### 6.4 跟其他渠道串接
- LINE OA 推播效果：把推播 ID 寫進 `app_open` 的 properties，可以追蹤「哪則推播帶來最多抽選」
- Rich Menu 點擊：未來可加 `app_open` properties 區分入口

## 7. 注意事項

- **隱私**：`line_id` 是 LINE userId，是 PII。CRM 內顯示時遵循公司隱私政策（脫敏 / 權限分級）
- **dev 模式**：URL 帶 `?dev=1` 跳過 LIFF init，`line_id` 為 NULL。生產環境分析時可加 `WHERE line_id IS NOT NULL` 過濾
- **資料正在累積中**：本系統 2026-05-21 剛上線，前期樣本小，趨勢需要 7-14 天才有意義
- **事件 schema 可能擴增**：未來新增事件會持續更新本文件。CRM 接入時建議使用 `properties JSONB` 的靈活查詢，避免 hard-code 欄位

## 8. 聯絡

Random Rice repo: https://github.com/Harveylin0316/random-rice
追蹤實作：`netlify/functions/track.js` + `frontend/shared/tracker.js`
Schema 變更：見 `supabase/analytics_schema.sql`
