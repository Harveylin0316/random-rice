// Supabase 客戶端
// 用於 Netlify Functions

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.warn('Supabase 環境變數未設定，將使用文件系統後備方案');
}

/**
 * 執行 Supabase REST API 請求
 */
async function supabaseRequest(endpoint, options = {}) {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    throw new Error('Supabase 環境變數未設定');
  }

  const url = `${SUPABASE_URL}/rest/v1/${endpoint}`;
  const headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': `Bearer ${SUPABASE_KEY}`,
    'Content-Type': 'application/json',
    'Prefer': 'return=representation', // 返回插入/更新的資料
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Supabase API 錯誤: ${response.status} - ${error}`);
  }

  // 如果沒有內容，返回 null
  if (response.status === 204 || response.headers.get('content-length') === '0') {
    return null;
  }

  return await response.json();
}

/**
 * 用戶相關操作
 */
const users = {
  // 獲取或創建用戶
  async getOrCreate(lineId, profile = null) {
    try {
      // 嘗試獲取用戶
      const existing = await supabaseRequest(`users?line_id=eq.${encodeURIComponent(lineId)}&select=*`);
      
      if (existing && existing.length > 0) {
        // 如果存在，更新資料（如果有提供）
        if (profile) {
          return await users.update(lineId, {
            display_name: profile.displayName,
            picture_url: profile.pictureUrl,
          });
        }
        return existing[0];
      }

      // 創建新用戶
      const newUser = {
        line_id: lineId,
        display_name: profile?.displayName || '用戶',
        picture_url: profile?.pictureUrl || '',
        total_chances: 1,
        used_chances: 0,
        remaining_chances: 1,
        invited_count: 0,
      };

      const result = await supabaseRequest('users', {
        method: 'POST',
        body: JSON.stringify(newUser),
      });

      return Array.isArray(result) ? result[0] : result;
    } catch (error) {
      console.error('獲取或創建用戶失敗:', error);
      throw error;
    }
  },

  // 更新用戶
  async update(lineId, updates) {
    const result = await supabaseRequest(`users?line_id=eq.${encodeURIComponent(lineId)}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });

    return Array.isArray(result) ? result[0] : result;
  },

  // 獲取用戶
  async get(lineId) {
    const result = await supabaseRequest(`users?line_id=eq.${encodeURIComponent(lineId)}&select=*`);
    return result && result.length > 0 ? result[0] : null;
  },

  // 獲取所有用戶（分頁）
  async getAll(page = 1, limit = 50) {
    const from = (page - 1) * limit;
    const to = from + limit - 1;
    
    const result = await supabaseRequest(`users?select=*&order=created_at.desc&range=${from}-${to}`);
    const countResult = await supabaseRequest(`users?select=line_id`, {
      headers: { 'Prefer': 'count=exact' },
    });

    return {
      users: result || [],
      total: parseInt(countResult?.length || 0),
    };
  },
};

/**
 * 獎品相關操作
 */
const prizes = {
  // 獲取所有獎品
  async getAll() {
    return await supabaseRequest('prizes?select=*&order=created_at.asc');
  },

  // 獲取啟用的獎品
  async getEnabled() {
    return await supabaseRequest('prizes?select=*&enabled=eq.true&order=created_at.asc');
  },

  // 獲取單個獎品
  async get(id) {
    const result = await supabaseRequest(`prizes?id=eq.${encodeURIComponent(id)}&select=*`);
    return result && result.length > 0 ? result[0] : null;
  },

  // 創建獎品
  async create(prize) {
    const result = await supabaseRequest('prizes', {
      method: 'POST',
      body: JSON.stringify(prize),
    });
    return Array.isArray(result) ? result[0] : result;
  },

  // 更新獎品
  async update(id, updates) {
    const result = await supabaseRequest(`prizes?id=eq.${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
    return Array.isArray(result) ? result[0] : result;
  },

  // 刪除獎品
  async delete(id) {
    await supabaseRequest(`prizes?id=eq.${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
    return true;
  },
};

/**
 * 抽獎記錄相關操作
 */
const records = {
  // 創建記錄
  async create(record) {
    const result = await supabaseRequest('lottery_records', {
      method: 'POST',
      body: JSON.stringify(record),
    });
    return Array.isArray(result) ? result[0] : result;
  },

  // 獲取用戶的抽獎記錄
  async getByUser(lineId) {
    return await supabaseRequest(
      `lottery_records?line_id=eq.${encodeURIComponent(lineId)}&type=eq.draw&select=*&order=created_at.desc`
    );
  },

  // 獲取統計資料
  async getStatistics() {
    // 總抽獎數
    const totalDraws = await supabaseRequest('lottery_records?type=eq.draw&select=id', {
      headers: { 'Prefer': 'count=exact' },
    });

    // 總邀請數
    const totalInvites = await supabaseRequest('lottery_records?type=eq.invite&select=id', {
      headers: { 'Prefer': 'count=exact' },
    });

    // 獎品統計（需要手動查詢，因為 Supabase 的 count 有限制）
    const allRecords = await supabaseRequest('lottery_records?type=eq.draw&select=prize_id,prize_name');
    const prizeStats = {};
    if (allRecords) {
      allRecords.forEach(record => {
        if (record.prize_id) {
          prizeStats[record.prize_id] = (prizeStats[record.prize_id] || 0) + 1;
        }
      });
    }

    return {
      totalDraws: parseInt(totalDraws?.length || 0),
      totalInvites: parseInt(totalInvites?.length || 0),
      prizeStats: Object.entries(prizeStats).map(([prizeId, count]) => ({
        prizeId,
        count,
      })),
    };
  },
};

module.exports = {
  users,
  prizes,
  records,
  supabaseRequest,
};
