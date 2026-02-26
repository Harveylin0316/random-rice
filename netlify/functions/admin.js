// Netlify Function for admin API
const fs = require('fs');
const path = require('path');

// 資料庫文件路徑（與 lottery.js 相同邏輯）
function getDatabasePath(filename) {
  const possiblePaths = [
    path.join(__dirname, filename),
    path.join(__dirname, '../../data', filename),
    path.join(process.cwd(), 'data', filename),
    path.join('/opt/build/repo', 'data', filename),
  ];
  
  for (const dbPath of possiblePaths) {
    if (fs.existsSync(dbPath)) {
      return dbPath;
    }
  }
  
  return path.join(__dirname, '../../data', filename);
}

// 載入資料庫
function loadDatabase(filename) {
  // 嘗試多個可能的路徑（包括保存路徑）
  const possiblePaths = [
    path.join(__dirname, 'data', filename), // Functions 目錄下的 data 子目錄
    path.join(__dirname, filename), // Functions 目錄
    path.join(process.cwd(), 'data', filename), // 當前工作目錄
    path.join('/tmp', filename), // Netlify Functions 的臨時目錄
    getDatabasePath(filename), // 原始路徑
  ];
  
  for (const dbPath of possiblePaths) {
    try {
      if (fs.existsSync(dbPath)) {
        const data = fs.readFileSync(dbPath, 'utf-8');
        const parsed = JSON.parse(data);
        console.log(`資料庫已從 ${dbPath} 載入`);
        return parsed;
      }
    } catch (err) {
      console.log(`嘗試從 ${dbPath} 載入失敗:`, err.message);
      continue;
    }
  }
  
  // 如果都找不到，返回空資料結構
  console.log(`找不到 ${filename}，使用空資料結構`);
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
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    // 在 Netlify Functions 中，嘗試多個可能的路徑
    const possiblePaths = [
      path.join(__dirname, 'data', filename), // Functions 目錄下的 data 子目錄
      path.join(__dirname, filename), // Functions 目錄
      path.join(process.cwd(), 'data', filename), // 當前工作目錄
      path.join('/tmp', filename), // Netlify Functions 的臨時目錄（可寫）
      dbPath, // 原始路徑
    ];
    
    let saved = false;
    let savedPath = null;
    
    for (const savePath of possiblePaths) {
      try {
        const saveDir = path.dirname(savePath);
        if (!fs.existsSync(saveDir)) {
          fs.mkdirSync(saveDir, { recursive: true });
        }
        
        fs.writeFileSync(savePath, JSON.stringify(data, null, 2), 'utf-8');
        saved = true;
        savedPath = savePath;
        console.log(`資料庫已保存到: ${savePath}`);
        break;
      } catch (err) {
        console.log(`嘗試保存到 ${savePath} 失敗:`, err.message);
        continue;
      }
    }
    
    if (!saved) {
      console.error(`無法保存 ${filename} 到任何路徑`);
      return false;
    }
    
    return true;
  } catch (err) {
    console.error(`Error saving ${filename}:`, err);
    return false;
  }
}

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
};

// 簡單的認證檢查（可以改為更安全的認證方式）
function checkAuth(event) {
  // 從查詢參數或請求頭獲取 API Key
  const apiKey = event.queryStringParameters?.apiKey || 
                 event.headers['x-api-key'] || 
                 (event.body ? (() => {
                   try {
                     return JSON.parse(event.body).apiKey;
                   } catch (e) {
                     return null;
                   }
                 })() : null);
  
  // 這裡可以設置環境變數 ADMIN_API_KEY
  const validApiKey = process.env.ADMIN_API_KEY || 'default_admin_key_change_me';
  
  // 調試日誌（僅在開發環境）
  if (process.env.NETLIFY_DEV) {
    console.log('API Key 檢查:', {
      provided: apiKey ? '已提供' : '未提供',
      validKey: validApiKey ? '已設定' : '未設定',
      match: apiKey === validApiKey
    });
  }
  
  return apiKey === validApiKey;
}

exports.handler = async (event, context) => {
  // 處理 OPTIONS 請求
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: corsHeaders,
      body: '',
    };
  }

  // 檢查認證
  if (!checkAuth(event)) {
    return {
      statusCode: 401,
      headers: corsHeaders,
      body: JSON.stringify({ error: 'Unauthorized' }),
    };
  }

  try {
    // 從 event.path 提取路徑，處理不同的路徑格式
    let path = event.path || '';
    
    // 移除 Netlify Functions 前綴和查詢參數
    if (path.includes('/.netlify/functions/admin')) {
      path = path.replace('/.netlify/functions/admin', '');
    } else if (path.includes('/api/admin')) {
      path = path.replace('/api/admin', '');
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
    
    console.log(`Admin API: ${method} ${path} (原始路徑: ${event.path})`);
    
    // 解析請求體
    let body = {};
    if (event.body) {
      try {
        body = JSON.parse(event.body);
      } catch (e) {
        // 忽略解析錯誤
      }
    }
    
    const queryParams = event.queryStringParameters || {};
    
    // 獎品管理
    if (path.startsWith('/prizes')) {
      if (path === '/prizes' && method === 'GET') {
        // 獲取所有獎品
        // 優先從環境變數讀取（如果有的話）
        let db = null;
        const envPrizes = process.env.PRIZES_DATABASE;
        if (envPrizes) {
          try {
            db = JSON.parse(envPrizes);
            console.log('從環境變數載入獎品資料');
          } catch (err) {
            console.log('環境變數解析失敗，使用文件載入:', err.message);
          }
        }
        
        // 如果環境變數沒有，從文件載入
        if (!db) {
          db = loadDatabase('prizes_database.json');
        }
        
        return {
          statusCode: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          body: JSON.stringify({ success: true, prizes: db.prizes || [] }),
        };
      }
      
      if (path === '/prizes' && method === 'POST') {
        // 新增獎品
        const db = loadDatabase('prizes_database.json');
        const now = new Date().toISOString();
        const newPrize = {
          id: `prize_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          name: body.name || '未命名獎品',
          description: body.description || '',
          probability: parseFloat(body.probability) || 0,
          image: body.image || '',
          enabled: body.enabled !== undefined ? body.enabled : true,
          createdAt: now,
          updatedAt: now,
        };
        
        db.prizes.push(newPrize);
        
        // 嘗試保存到文件
        const saved = saveDatabase('prizes_database.json', db);
        
        // 同時嘗試保存到環境變數（通過返回提示用戶手動更新）
        // 注意：Netlify Functions 無法直接修改環境變數，需要通過 Netlify API 或 Dashboard
        const dbJson = JSON.stringify(db, null, 2);
        const dbSize = Buffer.byteLength(dbJson, 'utf8');
        const maxEnvSize = 64 * 1024; // Netlify 環境變數最大約 64KB
        
        let envWarning = null;
        if (dbSize > maxEnvSize) {
          envWarning = '資料量過大，無法使用環境變數存儲。建議使用外部資料庫服務。';
        } else {
          envWarning = `請在 Netlify Dashboard 的環境變數中設定 PRIZES_DATABASE 為以下 JSON（不含換行）:\n${dbJson.replace(/\n/g, '')}`;
        }
        
        if (!saved) {
          console.error('保存獎品失敗 - 可能是文件系統只讀限制');
          console.warn('警告：資料庫保存失敗。請手動更新環境變數 PRIZES_DATABASE 以持久化資料。');
        } else {
          console.log('獎品已保存到文件:', newPrize.id);
        }
        
        return {
          statusCode: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            success: true, 
            prize: newPrize,
            prizes: db.prizes, // 返回完整的獎品列表
            warning: saved ? null : '資料庫保存失敗，但獎品已添加。請手動更新環境變數以持久化資料。',
            envUpdate: saved ? null : envWarning
          }),
        };
      }
      
      if (path.startsWith('/prizes/') && method === 'PUT') {
        // 更新獎品
        const prizeId = path.replace('/prizes/', '');
        const db = loadDatabase('prizes_database.json');
        const prizeIndex = db.prizes.findIndex(p => p.id === prizeId);
        
        if (prizeIndex === -1) {
          return {
            statusCode: 404,
            headers: corsHeaders,
            body: JSON.stringify({ error: '獎品不存在' }),
          };
        }
        
        const prize = db.prizes[prizeIndex];
        if (body.name !== undefined) prize.name = body.name;
        if (body.description !== undefined) prize.description = body.description;
        if (body.probability !== undefined) prize.probability = parseFloat(body.probability);
        if (body.image !== undefined) prize.image = body.image;
        if (body.enabled !== undefined) prize.enabled = body.enabled;
        prize.updatedAt = new Date().toISOString();
        
        const saved = saveDatabase('prizes_database.json', db);
        if (!saved) {
          console.warn('更新獎品時保存失敗，但資料已更新到內存中');
        }
        
        return {
          statusCode: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            success: true, 
            prize,
            warning: saved ? null : '資料庫保存失敗，但獎品已更新。建議使用外部資料庫服務以持久化資料。'
          }),
        };
      }
      
      if (path.startsWith('/prizes/') && method === 'DELETE') {
        // 刪除獎品
        const prizeId = path.replace('/prizes/', '');
        const db = loadDatabase('prizes_database.json');
        const prizeIndex = db.prizes.findIndex(p => p.id === prizeId);
        
        if (prizeIndex === -1) {
          return {
            statusCode: 404,
            headers: corsHeaders,
            body: JSON.stringify({ error: '獎品不存在' }),
          };
        }
        
        db.prizes.splice(prizeIndex, 1);
        const saved = saveDatabase('prizes_database.json', db);
        if (!saved) {
          console.warn('刪除獎品時保存失敗，但資料已從內存中刪除');
        }
        
        return {
          statusCode: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            success: true,
            warning: saved ? null : '資料庫保存失敗，但獎品已刪除。建議使用外部資料庫服務以持久化資料。'
          }),
        };
      }
    }
    
    // 用戶管理
    if (path.startsWith('/users')) {
      if (path === '/users' && method === 'GET') {
        // 獲取所有用戶
        const db = loadDatabase('users_database.json');
        const page = parseInt(queryParams.page) || 1;
        const limit = parseInt(queryParams.limit) || 50;
        const start = (page - 1) * limit;
        const end = start + limit;
        
        const users = db.users.slice(start, end);
        
        return {
          statusCode: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            success: true,
            users,
            pagination: {
              page,
              limit,
              total: db.users.length,
              totalPages: Math.ceil(db.users.length / limit),
            },
          }),
        };
      }
    }
    
    // 統計資料
    if (path === '/statistics' && method === 'GET') {
      const usersDb = loadDatabase('users_database.json');
      const prizesDb = loadDatabase('prizes_database.json');
      const recordsDb = loadDatabase('lottery_records.json');
      
      // 計算統計
      const totalUsers = usersDb.users.length;
      const totalDraws = recordsDb.records.filter(r => r.type !== 'invite').length;
      const totalInvites = recordsDb.records.filter(r => r.type === 'invite').length;
      
      // 獎品統計
      const prizeStats = {};
      recordsDb.records
        .filter(r => r.type !== 'invite' && r.prizeId)
        .forEach(r => {
          prizeStats[r.prizeId] = (prizeStats[r.prizeId] || 0) + 1;
        });
      
      const prizeStatsWithNames = Object.entries(prizeStats).map(([prizeId, count]) => {
        const prize = prizesDb.prizes.find(p => p.id === prizeId);
        return {
          prizeId,
          prizeName: prize?.name || '未知',
          count,
        };
      });
      
      return {
        statusCode: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          success: true,
          statistics: {
            totalUsers,
            totalDraws,
            totalInvites,
            prizeStats: prizeStatsWithNames,
          },
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
    console.error('Admin API Error:', error);
    console.error('Error stack:', error.stack);
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({
        error: 'Internal server error',
        message: error.message,
        stack: process.env.NETLIFY_DEV ? error.stack : undefined, // 只在開發環境顯示 stack
      }),
    };
  }
};
