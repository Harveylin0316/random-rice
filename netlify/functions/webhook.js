// Netlify Function for LINE Webhook
// 處理 LINE Messaging API 的 Webhook 事件

const crypto = require('crypto');

// 資料庫文件路徑（與 lottery.js 相同邏輯）
function getDatabasePath(filename) {
  const path = require('path');
  const possiblePaths = [
    path.join(__dirname, filename),
    path.join(__dirname, '../../data', filename),
    path.join(process.cwd(), 'data', filename),
    path.join('/opt/build/repo', 'data', filename),
  ];
  
  for (const dbPath of possiblePaths) {
    const fs = require('fs');
    if (fs.existsSync(dbPath)) {
      return dbPath;
    }
  }
  
  return path.join(__dirname, '../../data', filename);
}

// 載入資料庫
function loadDatabase(filename) {
  const fs = require('fs');
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
  } else if (filename === 'lottery_records.json') {
    return { records: [] };
  }
  return {};
}

// 保存資料庫
function saveDatabase(filename, data) {
  const fs = require('fs');
  const path = require('path');
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

// 驗證 LINE Webhook 簽名
function verifySignature(body, signature, channelSecret) {
  const hash = crypto
    .createHmac('sha256', channelSecret)
    .update(body)
    .digest('base64');
  
  return hash === signature;
}

// 處理好友加入事件
async function handleFollowEvent(event, inviterLineId) {
  const newUserLineId = event.source.userId;
  
  if (!newUserLineId) {
    return;
  }
  
  // 如果有邀請者，增加邀請者的抽獎次數
  if (inviterLineId && inviterLineId !== newUserLineId) {
    const usersDb = loadDatabase('users_database.json');
    const inviter = usersDb.users.find(u => u.lineId === inviterLineId);
    
    if (inviter && inviter.invitedCount < 2) {
      // 檢查是否已經邀請過這個用戶
      const recordsDb = loadDatabase('lottery_records.json');
      const existingInvite = recordsDb.records.find(
        r => r.lineId === newUserLineId && r.inviterLineId === inviterLineId
      );
      
      if (!existingInvite) {
        // 增加邀請次數和抽獎次數
        inviter.invitedCount += 1;
        inviter.totalChances += 1;
        inviter.remainingChances += 1;
        inviter.lastUpdated = new Date().toISOString();
        
        const userIndex = usersDb.users.findIndex(u => u.lineId === inviterLineId);
        if (userIndex !== -1) {
          usersDb.users[userIndex] = inviter;
        } else {
          usersDb.users.push(inviter);
        }
        saveDatabase('users_database.json', usersDb);
        
        // 記錄邀請記錄
        const inviteRecord = {
          id: `invite_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          lineId: newUserLineId,
          inviterLineId: inviterLineId,
          type: 'invite',
          createdAt: new Date().toISOString(),
        };
        recordsDb.records.push(inviteRecord);
        saveDatabase('lottery_records.json', recordsDb);
        
        console.log(`User ${inviterLineId} invited ${newUserLineId}, added chance`);
      }
    }
  }
}

exports.handler = async (event, context) => {
  // LINE Webhook 驗證
  const channelSecret = process.env.LINE_CHANNEL_SECRET;
  if (!channelSecret) {
    console.error('LINE_CHANNEL_SECRET not set');
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Server configuration error' }),
    };
  }
  
  // 驗證簽名
  const signature = event.headers['x-line-signature'];
  if (signature) {
    const body = event.body;
    if (!verifySignature(body, signature, channelSecret)) {
      console.error('Invalid signature');
      return {
        statusCode: 401,
        body: JSON.stringify({ error: 'Invalid signature' }),
      };
    }
  }
  
  try {
    const body = JSON.parse(event.body);
    
    // LINE Webhook 會發送多個事件
    if (body.events && Array.isArray(body.events)) {
      for (const webhookEvent of body.events) {
        // 處理 follow 事件（好友加入）
        if (webhookEvent.type === 'follow') {
          // 從 event.source 獲取用戶 ID
          const newUserLineId = webhookEvent.source?.userId;
          
          // 嘗試從 LIFF URL 參數或 state 獲取邀請者 ID
          // 注意：LINE Webhook 的 follow 事件不直接包含邀請者資訊
          // 需要通過其他方式追蹤（例如：使用 LIFF URL 參數或 LINE Login state）
          // 這裡我們先處理基本的好友加入事件
          
          console.log(`New user followed: ${newUserLineId}`);
          
          // 創建新用戶（如果不存在）
          const usersDb = loadDatabase('users_database.json');
          let user = usersDb.users.find(u => u.lineId === newUserLineId);
          
          if (!user) {
            const now = new Date().toISOString();
            user = {
              lineId: newUserLineId,
              displayName: '用戶',
              pictureUrl: '',
              totalChances: 1,
              usedChances: 0,
              remainingChances: 1,
              invitedCount: 0,
              createdAt: now,
              lastUpdated: now,
            };
            
            usersDb.users.push(user);
            saveDatabase('users_database.json', usersDb);
          }
          
          // 如果有邀請者資訊（需要通過其他方式傳遞，例如 LIFF URL 參數）
          // 這裡暫時不處理，因為 follow 事件不包含邀請者資訊
          // 實際應用中，可以通過以下方式追蹤：
          // 1. 使用 LIFF URL 參數：https://your-site.netlify.app/liff/lottery?inviter=U123...
          // 2. 使用 LINE Login 的 state 參數
          // 3. 在用戶首次訪問 LIFF 時檢查 URL 參數並記錄
        }
      }
    }
    
    return {
      statusCode: 200,
      body: JSON.stringify({ success: true }),
    };
    
  } catch (error) {
    console.error('Webhook Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Internal server error',
        message: error.message,
      }),
    };
  }
};
