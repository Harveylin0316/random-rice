# Supabase 設置指南

## 步驟 1：創建 Supabase 專案

1. 訪問 [Supabase](https://supabase.com/)
2. 註冊/登入帳號
3. 點擊 "New Project"
4. 填寫專案資訊：
   - **Name**: random-rice-lottery（或你喜歡的名稱）
   - **Database Password**: 設定一個強密碼（記下來，之後會用到）
   - **Region**: 選擇離你最近的區域（例如：Southeast Asia (Singapore)）
5. 點擊 "Create new project"
6. 等待專案創建完成（約 2 分鐘）

## 步驟 2：執行 SQL 腳本建立資料表

1. 在 Supabase Dashboard 中，點擊左側選單的 **SQL Editor**
2. 點擊 **New query**
3. 打開專案中的 `supabase/schema.sql` 文件
4. 複製整個 SQL 腳本內容
5. 貼上到 Supabase SQL Editor
6. 點擊 **Run** 執行
7. 確認執行成功（應該會看到 "Success. No rows returned"）

## 步驟 3：獲取 API 憑證

1. 在 Supabase Dashboard 中，點擊左側選單的 **Settings** → **API**
2. 找到以下資訊：
   - **Project URL**: 例如 `https://xxxxx.supabase.co`
   - **anon/public key**: 這是你的 API Key（公開的，用於前端和 Functions）

## 步驟 4：設定 Netlify 環境變數

1. 進入 Netlify Dashboard → Site settings → Environment variables
2. 新增以下環境變數：

   **SUPABASE_URL**
   - Key: `SUPABASE_URL`
   - Value: 你的 Project URL（例如：`https://xxxxx.supabase.co`）
   - Secret: 勾選
   - Scopes: All scopes

   **SUPABASE_KEY**
   - Key: `SUPABASE_KEY`
   - Value: 你的 anon/public key
   - Secret: 勾選
   - Scopes: All scopes

3. 點擊 "Create variable" 完成設定

## 步驟 5：重新部署

環境變數設定後需要重新部署：

1. 在 Netlify Dashboard 點擊 "Trigger deploy" → "Deploy site"
2. 或推送一個空 commit：
   ```bash
   git commit --allow-empty -m "觸發重新部署以載入 Supabase 環境變數"
   git push origin main
   ```

## 步驟 6：測試

1. 訪問後台管理頁面：`https://your-site.netlify.app/admin`
2. 使用 API Key 登入
3. 新增一個獎品
4. 確認獎品出現在列表中
5. 重新整理頁面，確認資料持久化

## 步驟 7：驗證資料庫

在 Supabase Dashboard 中：

1. 點擊左側選單的 **Table Editor**
2. 應該可以看到三個表：
   - `users` - 用戶資料
   - `prizes` - 獎品設定
   - `lottery_records` - 抽獎記錄
3. 點擊 `prizes` 表，應該可以看到預設的 3 個獎品
4. 在後台新增獎品後，應該可以在這裡看到新獎品

## 安全性設定（可選）

### 啟用 Row Level Security (RLS)

如果需要更嚴格的安全性，可以啟用 RLS：

1. 在 Supabase Dashboard → SQL Editor 執行：
   ```sql
   -- 啟用 RLS
   ALTER TABLE users ENABLE ROW LEVEL SECURITY;
   ALTER TABLE prizes ENABLE ROW LEVEL SECURITY;
   ALTER TABLE lottery_records ENABLE ROW LEVEL SECURITY;
   
   -- 允許所有人讀取（因為我們使用 API Key 認證）
   CREATE POLICY "Allow public read" ON users FOR SELECT USING (true);
   CREATE POLICY "Allow public read" ON prizes FOR SELECT USING (true);
   CREATE POLICY "Allow public read" ON lottery_records FOR SELECT USING (true);
   
   -- 允許所有人寫入（因為我們使用 API Key 認證）
   CREATE POLICY "Allow public write" ON users FOR ALL USING (true);
   CREATE POLICY "Allow public write" ON prizes FOR ALL USING (true);
   CREATE POLICY "Allow public write" ON lottery_records FOR ALL USING (true);
   ```

**注意**：由於我們在 Netlify Functions 中使用 API Key 認證，RLS 可以設為公開。如果需要更嚴格的控制，可以設置更複雜的策略。

## 故障排除

### 問題：API 返回 401 錯誤

**解決方案**：
- 檢查 `SUPABASE_URL` 和 `SUPABASE_KEY` 是否正確設定
- 確認使用的是 `anon/public` key，不是 `service_role` key
- 確認環境變數已重新部署

### 問題：資料表不存在

**解決方案**：
- 確認 SQL 腳本已正確執行
- 在 Supabase Dashboard → Table Editor 檢查表是否存在
- 如果不存在，重新執行 `supabase/schema.sql`

### 問題：無法插入資料

**解決方案**：
- 檢查資料表結構是否正確
- 檢查欄位名稱是否匹配（Supabase 使用 snake_case）
- 查看 Supabase Dashboard → Logs 查看錯誤訊息

### 問題：查詢返回空結果

**解決方案**：
- 確認資料已正確插入
- 檢查查詢條件是否正確
- 在 Supabase Dashboard → Table Editor 手動檢查資料

## 免費方案限制

Supabase 免費方案包含：
- ✅ 500MB 資料庫空間
- ✅ 2GB 頻寬/月
- ✅ 50,000 月活躍用戶
- ✅ 2GB 文件存儲

對於抽獎系統來說，免費方案應該足夠初期使用。如果超過限制，可以升級到付費方案。

## 下一步

設置完成後，系統會自動使用 Supabase 作為資料庫。所有資料都會持久化保存，即使重新部署也不會丟失。

如果需要遷移現有資料：
1. 從舊的 JSON 文件導出資料
2. 在 Supabase Dashboard → Table Editor 手動插入
3. 或使用 Supabase 的 Import 功能
