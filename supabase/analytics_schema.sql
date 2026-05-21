-- 用戶行為追蹤 events 表
-- 在 Supabase Dashboard → SQL Editor 執行

CREATE TABLE IF NOT EXISTS user_events (
  id BIGSERIAL PRIMARY KEY,
  -- 識別
  line_id TEXT,                       -- 可能為 NULL（dev 模式或外部開啟）
  session_id TEXT NOT NULL,           -- 本次開啟 LIFF 的 session（前端 uuid）
  -- 事件
  event_name TEXT NOT NULL,           -- app_open / submit_draw / result_shown / redraw / restaurant_click / navigation_click / ad_shown / ad_cta_click / share
  properties JSONB DEFAULT '{}'::jsonb, -- 結構化 props（or_id、餐廳名、廣告 id、filters 等）
  -- 環境
  is_in_line BOOLEAN,                 -- liff.isInClient()
  os TEXT,                            -- liff.getOS()
  language TEXT,
  user_agent TEXT,
  -- 時間
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 查詢用索引
CREATE INDEX IF NOT EXISTS idx_user_events_line_id ON user_events(line_id);
CREATE INDEX IF NOT EXISTS idx_user_events_session ON user_events(session_id);
CREATE INDEX IF NOT EXISTS idx_user_events_event_name ON user_events(event_name);
CREATE INDEX IF NOT EXISTS idx_user_events_created_at ON user_events(created_at DESC);

-- RLS：服務端寫入用 service_role，不需要 RLS
ALTER TABLE user_events DISABLE ROW LEVEL SECURITY;

-- 範例分析查詢：
--
-- -- 每日活躍用戶
-- SELECT DATE(created_at), COUNT(DISTINCT line_id) FROM user_events
-- WHERE event_name = 'app_open' GROUP BY 1 ORDER BY 1 DESC;
--
-- -- 抽 → 點訂位 漏斗
-- SELECT
--   COUNT(*) FILTER (WHERE event_name = 'result_shown') AS shown,
--   COUNT(*) FILTER (WHERE event_name = 'restaurant_click') AS clicked,
--   COUNT(*) FILTER (WHERE event_name = 'restaurant_click')::float
--     / NULLIF(COUNT(*) FILTER (WHERE event_name = 'result_shown'), 0) AS ctr
-- FROM user_events WHERE created_at > NOW() - INTERVAL '7 days';
--
-- -- 哪些餐廳最常被點進去
-- SELECT properties->>'name' AS restaurant, COUNT(*) FROM user_events
-- WHERE event_name = 'restaurant_click'
-- GROUP BY 1 ORDER BY 2 DESC LIMIT 20;
--
-- -- 用戶平均抽幾次才點訂位
-- WITH per_session AS (
--   SELECT session_id,
--     COUNT(*) FILTER (WHERE event_name = 'result_shown') AS draws,
--     COUNT(*) FILTER (WHERE event_name = 'restaurant_click') AS clicks
--   FROM user_events GROUP BY session_id
-- )
-- SELECT AVG(draws) FILTER (WHERE clicks > 0) AS avg_draws_before_click FROM per_session;
