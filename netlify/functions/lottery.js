// Netlify Function for lottery API
const fs = require('fs');
const path = require('path');

// 嘗試導入 Supabase 客戶端
// 注意：Netlify Functions 在打包時會分析所有 require，所以只使用構建後的正確路徑
let supabase = null;
try {
  // 構建腳本會將 supabase 複製到 netlify/functions/supabase/
  // 所以這裡使用相對路徑 ./supabase/client
  supabase = require('./supabase/client');
} catch (err) {
  // 如果導入失敗，使用文件系統後備方案
  console.log('Supabase 客戶端未找到，將使用文件系統後備方案:', err.message);
}

// 資料庫文件路徑
function getDatabasePath(filename) {
  const possiblePaths = [
    path.join(__dirname, filename), // 函數目錄
    path.join(__dirname, '../../data', filename), // 項目根目錄的 data 目錄
    path.join(process.cwd(), 'data', filename), // 當前工作目錄
    path.join('/opt/build/repo', 'data', filename), // Netlify 構建目錄
  ];
  
  for (const dbPath of possiblePaths) {
    if (fs.existsSync(dbPath)) {
      return dbPath;
    }
  }
  
  // 如果找不到，返回預期路徑（用於創建新文件）
  return path.join(__dirname, '../../data', filename);
}

// 載入資料庫
function loadDatabase(filename) {
  const dbPath = getDatabasePath(filename);
  try {
    if (fs.existsSync(dbPath)) {
      const data = fs.readFileSync(dbPath, 'utf-8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.error(`Error loading ${filename}:`, err);
  }
  
  // 返回空資料結構
  if (filename === 'users_database.json') {
    return { users: [] };
  } else if (filename === 'prizes_database.json') {
    return { prizes: [] };
  } else if (filename === 'lottery_records.json') {
    return { records: [] };
  }
  return {};
}

// 保存資料庫
function saveDatabase(filename, data) {
  const dbPath = getDatabasePath(filename);
  try {
    // 確保目錄存在
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    fs.writeFileSync(dbPath, JSON.stringify(data, null, 2), 'utf-8');
    return true;
  } catch (err) {
    console.error(`Error saving ${filename}:`, err);
    return false;
  }
}

// 獲取或創建用戶
function getOrCreateUser(lineId, profile = null) {
  const db = loadDatabase('users_database.json');
  let user = db.users.find(u => u.lineId === lineId);
  
  if (!user) {
    // 創建新用戶
    const now = new Date().toISOString();
    user = {
      lineId: lineId,
      displayName: profile?.displayName || '用戶',
      pictureUrl: profile?.pictureUrl || '',
      totalChances: 1,
      usedChances: 0,
      remainingChances: 1,
      invitedCount: 0,
      createdAt: now,
      lastUpdated: now
    };
    
    db.users.push(user);
    saveDatabase('users_database.json', db);
  } else if (profile) {
    // 更新用戶資料
    user.displayName = profile.displayName || user.displayName;
    user.pictureUrl = profile.pictureUrl || user.pictureUrl;
    user.lastUpdated = new Date().toISOString();
    saveDatabase('users_database.json', db);
  }
  
  return user;
}

// 抽獎邏輯
async function drawLottery() {
  try {
    let enabledPrizes = [];
    
    if (supabase) {
      // 使用 Supabase
      console.log('從 Supabase 獲取啟用的獎品...');
      try {
        enabledPrizes = await supabase.prizes.getEnabled();
        console.log('獲取到的啟用獎品數量:', enabledPrizes ? enabledPrizes.length : 0);
      } catch (supabaseError) {
        console.error('Supabase 查詢啟用獎品失敗:', supabaseError);
        throw new Error(`獲取獎品列表失敗: ${supabaseError.message}`);
      }
    } else {
      // 後備方案：使用文件系統
      const db = loadDatabase('prizes_database.json');
      enabledPrizes = db.prizes.filter(p => p.enabled);
    }
    
    if (!enabledPrizes || enabledPrizes.length === 0) {
      throw new Error('沒有可用的獎品');
    }
    
    // 過濾出有剩餘數量的獎品（如果設定了數量上限）
    const availablePrizes = enabledPrizes.filter(prize => {
      // 如果沒有設定總數量（total_quantity 為 NULL），則無限制
      if (prize.total_quantity === null || prize.total_quantity === undefined) {
        return true;
      }
      // 計算剩餘數量
      const remaining = prize.total_quantity - (prize.used_quantity || 0);
      return remaining > 0;
    });
    
    console.log('可用獎品數量（考慮數量限制）:', availablePrizes.length);
    
    if (availablePrizes.length === 0) {
      throw new Error('所有獎品都已抽完，沒有可用的獎品');
    }
    
    // 計算總機率（只計算可用獎品的機率）
    const totalProbability = availablePrizes.reduce((sum, p) => sum + (p.probability || 0), 0);
    
    if (totalProbability <= 0) {
      throw new Error('獎品機率設定錯誤：總機率必須大於 0');
    }
    
    console.log('總機率:', totalProbability);
    
    // 生成隨機數
    const random = Math.random() * totalProbability;
    console.log('隨機數:', random);
    
    // 根據機率分配獎品
    let cumulative = 0;
    for (const prize of availablePrizes) {
      cumulative += (prize.probability || 0);
      if (random <= cumulative) {
        console.log('抽中獎品:', prize.name, 'ID:', prize.id);
        return prize;
      }
    }
    
    // 預設返回最後一個獎品
    console.log('返回最後一個獎品:', availablePrizes[availablePrizes.length - 1].name);
    return availablePrizes[availablePrizes.length - 1];
  } catch (error) {
    console.error('抽獎邏輯失敗:', error);
    console.error('錯誤詳情:', error.message);
    console.error('錯誤堆疊:', error.stack);
    throw error;
  }
}

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
};

exports.handler = async (event, context) => {
  // 處理 OPTIONS 請求
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: corsHeaders,
      body: '',
    };
  }

  try {
    // 從 event.path 提取路徑，處理不同的路徑格式
    let path = event.path || '';
    
    // 移除 Netlify Functions 前綴和查詢參數
    if (path.includes('/.netlify/functions/lottery')) {
      path = path.replace('/.netlify/functions/lottery', '');
    } else if (path.includes('/api/lottery')) {
      path = path.replace('/api/lottery', '');
    }
    
    // 移除查詢參數部分
    if (path.includes('?')) {
      path = path.split('?')[0];
    }
    
    // 如果路徑為空，設為根路徑
    if (!path) {
      path = '/';
    }
    
    const method = event.httpMethod;
    
    console.log(`Lottery API: ${method} ${path} (原始路徑: ${event.path})`);
    
    // 解析請求體
    let body = {};
    if (event.body) {
      try {
        body = JSON.parse(event.body);
      } catch (e) {
        // 如果不是 JSON，可能是查詢參數
      }
    }
    
    // 解析查詢參數
    const queryParams = event.queryStringParameters || {};
    
    // 路由處理
    if (path === '/user' && method === 'GET') {
      // 獲取用戶資料
      const lineId = queryParams.lineId || body.lineId;
      
      if (!lineId) {
        return {
          statusCode: 400,
          headers: corsHeaders,
          body: JSON.stringify({ error: '缺少 lineId 參數' }),
        };
      }
      
      try {
        const user = await getOrCreateUser(lineId);
        
        return {
          statusCode: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          body: JSON.stringify({ success: true, user }),
        };
      } catch (error) {
        console.error('獲取用戶資料失敗:', error);
        return {
          statusCode: 500,
          headers: corsHeaders,
          body: JSON.stringify({ error: '獲取用戶資料失敗', message: error.message }),
        };
      }
    }
    
    if (path === '/draw' && method === 'POST') {
      // 執行抽獎
      const lineId = body.lineId;
      
      if (!lineId) {
        return {
          statusCode: 400,
          headers: corsHeaders,
          body: JSON.stringify({ error: '缺少 lineId 參數' }),
        };
      }
      
      try {
        // 獲取用戶資料
        const user = await getOrCreateUser(lineId);
        
        // 檢查是否有剩餘次數
        if (user.remainingChances <= 0) {
          return {
            statusCode: 400,
            headers: corsHeaders,
            body: JSON.stringify({ error: '沒有剩餘抽獎次數' }),
          };
        }
        
        // 執行抽獎
        const prize = await drawLottery();
        
        // 更新獎品的已使用數量（如果設定了數量上限）
        if (prize.total_quantity !== null && prize.total_quantity !== undefined) {
          const newUsedQuantity = (prize.used_quantity || 0) + 1;
          
          if (supabase) {
            await supabase.prizes.update(prize.id, {
              used_quantity: newUsedQuantity
            });
          } else {
            // 後備方案：更新文件系統
            const db = loadDatabase('prizes_database.json');
            const prizeIndex = db.prizes.findIndex(p => p.id === prize.id);
            if (prizeIndex !== -1) {
              db.prizes[prizeIndex].used_quantity = newUsedQuantity;
              saveDatabase('prizes_database.json', db);
            }
          }
        }
        
        // 記錄抽獎結果
        const recordId = `record_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const record = {
          id: recordId,
          line_id: lineId,
          prize_id: prize.id,
          prize_name: prize.name,
          prize_description: prize.description || '',
          type: 'draw',
        };
        
        if (supabase) {
          await supabase.records.create(record);
        } else {
          const recordsDb = loadDatabase('lottery_records.json');
          recordsDb.records.push({
            ...record,
            lineId: record.line_id,
            prizeId: record.prize_id,
            prizeName: record.prize_name,
            prizeDescription: record.prize_description,
            drawnAt: new Date().toISOString(),
          });
          saveDatabase('lottery_records.json', recordsDb);
        }
        
        // 更新用戶資料
        const updatedUser = {
          used_chances: user.usedChances + 1,
          remaining_chances: user.remainingChances - 1,
        };
        
        if (supabase) {
          await supabase.users.update(lineId, updatedUser);
          // 重新獲取用戶資料
          const freshUser = await supabase.users.get(lineId);
          return {
            statusCode: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            body: JSON.stringify({
              success: true,
              prize: {
                id: prize.id,
                name: prize.name,
                description: prize.description,
                image: prize.image,
              },
              user: {
                remainingChances: freshUser.remaining_chances,
                usedChances: freshUser.used_chances,
                totalChances: freshUser.total_chances,
              },
            }),
          };
        } else {
          user.usedChances += 1;
          user.remainingChances -= 1;
          user.lastUpdated = new Date().toISOString();
          
          const usersDb = loadDatabase('users_database.json');
          const userIndex = usersDb.users.findIndex(u => u.lineId === lineId);
          if (userIndex !== -1) {
            usersDb.users[userIndex] = user;
            saveDatabase('users_database.json', usersDb);
          }
          
          return {
            statusCode: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            body: JSON.stringify({
              success: true,
              prize: {
                id: prize.id,
                name: prize.name,
                description: prize.description,
                image: prize.image,
              },
              user: {
                remainingChances: user.remainingChances,
                usedChances: user.usedChances,
                totalChances: user.totalChances,
              },
            }),
          };
        }
      } catch (error) {
        console.error('抽獎失敗:', error);
        console.error('錯誤詳情:', error.message);
        console.error('錯誤堆疊:', error.stack);
        return {
          statusCode: 500,
          headers: corsHeaders,
          body: JSON.stringify({ 
            error: '抽獎失敗', 
            message: error.message,
            details: process.env.NODE_ENV === 'development' ? error.stack : undefined
          }),
        };
      }
    }
    
    if (path === '/invite' && method === 'POST') {
      // 記錄邀請（當好友加入時）
      const inviterLineId = body.inviterLineId;
      const newUserLineId = body.newUserLineId;
      
      if (!inviterLineId || !newUserLineId) {
        return {
          statusCode: 400,
          headers: corsHeaders,
          body: JSON.stringify({ error: '缺少必要參數' }),
        };
      }
      
      // 不能邀請自己
      if (inviterLineId === newUserLineId) {
        return {
          statusCode: 400,
          headers: corsHeaders,
          body: JSON.stringify({ error: '不能邀請自己' }),
        };
      }
      
      try {
        // 獲取邀請者資料
        const inviter = await getOrCreateUser(inviterLineId);
        
        // 檢查是否已達到最大邀請次數
        if (inviter.invitedCount >= 2) {
          return {
            statusCode: 400,
            headers: corsHeaders,
            body: JSON.stringify({ error: '已達到最大邀請次數' }),
          };
        }
        
        // 檢查是否已經邀請過這個用戶（防止重複）
        let existingInvite = false;
        if (supabase) {
          existingInvite = await supabase.records.checkInvite(newUserLineId, inviterLineId);
        } else {
          const recordsDb = loadDatabase('lottery_records.json');
          existingInvite = recordsDb.records.some(
            r => r.lineId === newUserLineId && r.inviterLineId === inviterLineId
          );
        }
        
        if (existingInvite) {
          return {
            statusCode: 400,
            headers: corsHeaders,
            body: JSON.stringify({ error: '該用戶已被邀請過' }),
          };
        }
        
        // 增加邀請次數和抽獎次數
        const updates = {
          invited_count: inviter.invitedCount + 1,
          total_chances: inviter.totalChances + 1,
          remaining_chances: inviter.remainingChances + 1,
        };
        
        if (supabase) {
          await supabase.users.update(inviterLineId, updates);
          
          // 記錄邀請記錄
          const inviteRecord = {
            id: `invite_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            line_id: newUserLineId,
            inviter_line_id: inviterLineId,
            type: 'invite',
            prize_name: '邀請獎勵',
            prize_description: '',
          };
          await supabase.records.create(inviteRecord);
          
          // 重新獲取用戶資料
          const freshUser = await supabase.users.get(inviterLineId);
          return {
            statusCode: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            body: JSON.stringify({
              success: true,
              user: {
                invitedCount: freshUser.invited_count,
                remainingChances: freshUser.remaining_chances,
                totalChances: freshUser.total_chances,
              },
            }),
          };
        } else {
          inviter.invitedCount += 1;
          inviter.totalChances += 1;
          inviter.remainingChances += 1;
          inviter.lastUpdated = new Date().toISOString();
          
          const usersDb = loadDatabase('users_database.json');
          const userIndex = usersDb.users.findIndex(u => u.lineId === inviterLineId);
          if (userIndex !== -1) {
            usersDb.users[userIndex] = inviter;
          } else {
            usersDb.users.push(inviter);
          }
          saveDatabase('users_database.json', usersDb);
          
          // 記錄邀請記錄
          const recordsDb = loadDatabase('lottery_records.json');
          const inviteRecord = {
            id: `invite_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            lineId: newUserLineId,
            inviterLineId: inviterLineId,
            type: 'invite',
            createdAt: new Date().toISOString(),
          };
          recordsDb.records.push(inviteRecord);
          saveDatabase('lottery_records.json', recordsDb);
          
          return {
            statusCode: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            body: JSON.stringify({
              success: true,
              user: {
                invitedCount: inviter.invitedCount,
                remainingChances: inviter.remainingChances,
                totalChances: inviter.totalChances,
              },
            }),
          };
        }
      } catch (error) {
        console.error('記錄邀請失敗:', error);
        return {
          statusCode: 500,
          headers: corsHeaders,
          body: JSON.stringify({ error: '記錄邀請失敗', message: error.message }),
        };
      }
    }
    
    if (path === '/records' && method === 'GET') {
      // 獲取用戶抽獎記錄
      const lineId = queryParams.lineId || body.lineId;
      
      if (!lineId) {
        return {
          statusCode: 400,
          headers: corsHeaders,
          body: JSON.stringify({ error: '缺少 lineId 參數' }),
        };
      }
      
      const recordsDb = loadDatabase('lottery_records.json');
      const userRecords = recordsDb.records
        .filter(r => r.lineId === lineId && r.type !== 'invite')
        .sort((a, b) => new Date(b.drawnAt) - new Date(a.drawnAt));
      
      return {
        statusCode: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          success: true,
          records: userRecords,
        }),
      };
    }
    
    // 404
    return {
      statusCode: 404,
      headers: corsHeaders,
      body: JSON.stringify({ error: 'Not found' }),
    };
    
  } catch (error) {
    console.error('Lottery API Error:', error);
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({
        error: 'Internal server error',
        message: error.message,
      }),
    };
  }
};
