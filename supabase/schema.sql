-- 抽獎系統 Supabase 資料庫結構
-- 在 Supabase Dashboard → SQL Editor 中執行此腳本

-- 1. 用戶資料表
CREATE TABLE IF NOT EXISTS users (
  line_id TEXT PRIMARY KEY,
  display_name TEXT,
  picture_url TEXT,
  total_chances INTEGER DEFAULT 1 NOT NULL,
  used_chances INTEGER DEFAULT 0 NOT NULL,
  remaining_chances INTEGER DEFAULT 1 NOT NULL,
  invited_count INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 2. 獎品設定表
CREATE TABLE IF NOT EXISTS prizes (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  probability REAL NOT NULL CHECK (probability >= 0 AND probability <= 1),
  image TEXT,
  enabled BOOLEAN DEFAULT true NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 3. 抽獎記錄表
CREATE TABLE IF NOT EXISTS lottery_records (
  id TEXT PRIMARY KEY,
  line_id TEXT NOT NULL,
  prize_id TEXT,
  prize_name TEXT NOT NULL,
  prize_description TEXT,
  type TEXT NOT NULL CHECK (type IN ('draw', 'invite')),
  inviter_line_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  FOREIGN KEY (line_id) REFERENCES users(line_id) ON DELETE CASCADE,
  FOREIGN KEY (prize_id) REFERENCES prizes(id) ON DELETE SET NULL
);

-- 建立索引以提升查詢效能
CREATE INDEX IF NOT EXISTS idx_lottery_records_line_id ON lottery_records(line_id);
CREATE INDEX IF NOT EXISTS idx_lottery_records_created_at ON lottery_records(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_prizes_enabled ON prizes(enabled) WHERE enabled = true;

-- 建立更新時間的自動更新函數
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 為 users 表添加自動更新 updated_at 的觸發器
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 為 prizes 表添加自動更新 updated_at 的觸發器
CREATE TRIGGER update_prizes_updated_at
  BEFORE UPDATE ON prizes
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 插入預設獎品（可選）
INSERT INTO prizes (id, name, description, probability, enabled) VALUES
  ('prize_1', '100元折價券', '可於指定餐廳使用', 0.5, true),
  ('prize_2', '500元折價券', '可於指定餐廳使用', 0.3, true),
  ('prize_3', '謝謝參與', '感謝您的參與', 0.2, true)
ON CONFLICT (id) DO NOTHING;
