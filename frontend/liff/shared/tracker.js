// 用戶行為追蹤 helper
// fire-and-forget POST 到 /api/track，失敗靜默不拖累主流程
//
// 用法：
//   import { track, setUserContext } from '../shared/tracker.js';
//   setUserContext({ line_id, is_in_line, os, language });
//   track('submit_draw', { filters: {...} });

const TRACK_ENDPOINT = '/api/track';

// 本次 session id（reload 換新）
const sessionId = (() => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
    return 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 10);
})();

// 用戶 context（LIFF init 後設一次）
let userContext = {
    line_id: null,
    is_in_line: null,
    os: null,
    language: null,
};

export function setUserContext(ctx) {
    userContext = { ...userContext, ...ctx };
}

export function getSessionId() {
    return sessionId;
}

export function track(eventName, properties = {}) {
    const payload = {
        event_name: eventName,
        properties,
        session_id: sessionId,
        ...userContext,
    };
    // fire-and-forget；用 sendBeacon 在 unload 時也能送出，否則用 fetch keepalive
    try {
        const body = JSON.stringify(payload);
        if (navigator.sendBeacon) {
            const blob = new Blob([body], { type: 'application/json' });
            navigator.sendBeacon(TRACK_ENDPOINT, blob);
        } else {
            fetch(TRACK_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body,
                keepalive: true,
            }).catch(() => { /* silent */ });
        }
    } catch (err) {
        // 不要影響主流程
        console.debug('[track] fail:', err);
    }
}
