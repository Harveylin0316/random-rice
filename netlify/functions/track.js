// Netlify Function：接收前端事件、寫入 Supabase user_events
// 端點：POST /api/track
// payload: { event_name, properties, session_id, line_id?, is_in_line?, os?, language? }

let supabaseRequest = null;
try {
  ({ supabaseRequest } = require('./supabase/client'));
} catch (err) {
  console.log('[track] Supabase client 未找到:', err.message);
}

exports.handler = async (event) => {
  // 只接受 POST
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
  };

  let payload;
  try {
    payload = JSON.parse(event.body || '{}');
  } catch {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'invalid JSON' }) };
  }

  const {
    event_name, properties = {}, session_id,
    line_id = null, is_in_line = null, os = null, language = null,
  } = payload;

  if (!event_name || !session_id) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'event_name and session_id required' }) };
  }

  // 沒有 Supabase（本機開發 / 缺環境變數），靜默 ack 不拖累前端
  if (!supabaseRequest) {
    console.log('[track] no supabase, dropping:', event_name);
    return { statusCode: 202, headers, body: JSON.stringify({ ok: true, dropped: true }) };
  }

  try {
    const userAgent = event.headers['user-agent'] || event.headers['User-Agent'] || null;
    await supabaseRequest('user_events', {
      method: 'POST',
      body: JSON.stringify({
        line_id,
        session_id,
        event_name,
        properties,
        is_in_line,
        os,
        language,
        user_agent: userAgent,
      }),
    });
    return { statusCode: 200, headers, body: JSON.stringify({ ok: true }) };
  } catch (err) {
    console.error('[track] insert failed:', err);
    return { statusCode: 500, headers, body: JSON.stringify({ error: err.message }) };
  }
};
