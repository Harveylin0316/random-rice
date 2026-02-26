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
  const dbPath = getDatabasePath(filename);
  try {
    if (fs.existsSync(dbPath)) {
      const data = fs.readFileSync(dbPath, 'utf-8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.error(`Error loading ${filename}:`, err);
  }
  
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
    
    fs.writeFileSync(dbPath, JSON.stringify(data, null, 2), 'utf-8');
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
                 (event.body ? JSON.parse(event.body).apiKey : null);
  
  // 這裡可以設置環境變數 ADMIN_API_KEY
  const validApiKey = process.env.ADMIN_API_KEY || 'default_admin_key_change_me';
  
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
    const path = event.path.replace('/.netlify/functions/admin', '');
    const method = event.httpMethod;
    
    console.log(`Admin API: ${method} ${path}`);
    
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
        const db = loadDatabase('prizes_database.json');
        return {
          statusCode: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          body: JSON.stringify({ success: true, prizes: db.prizes }),
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
        saveDatabase('prizes_database.json', db);
        
        return {
          statusCode: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          body: JSON.stringify({ success: true, prize: newPrize }),
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
        
        saveDatabase('prizes_database.json', db);
        
        return {
          statusCode: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          body: JSON.stringify({ success: true, prize }),
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
        saveDatabase('prizes_database.json', db);
        
        return {
          statusCode: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          body: JSON.stringify({ success: true }),
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
