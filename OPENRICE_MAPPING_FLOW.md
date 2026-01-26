# OpenRice 會員對應流程設計

## 流程 1：已經是 OpenRice 會員 - LINE ID Mapping

### 方案 A：Email 驗證對應（推薦）

#### 流程步驟：

```
1. 用戶在 LIFF App 中點擊「連結 OpenRice 帳號」
   ↓
2. 顯示輸入框，要求輸入 OpenRice 註冊 Email
   ↓
3. 後端發送驗證碼到該 Email
   ↓
4. 用戶輸入驗證碼
   ↓
5. 驗證成功後，建立 LINE User ID 與 OpenRice 會員的對應
   ↓
6. 完成連結，載入用戶資料
```

#### 實現細節：

**前端 UI：**
```javascript
// 顯示連結帳號的彈窗
function showLinkAccountModal() {
    const modal = `
        <div class="link-account-modal">
            <h3>連結 OpenRice 帳號</h3>
            <p>請輸入您的 OpenRice 註冊 Email</p>
            <input type="email" id="openriceEmail" placeholder="your@email.com">
            <button onclick="sendVerificationCode()">發送驗證碼</button>
            <div id="verificationCodeSection" style="display: none;">
                <input type="text" id="verificationCode" placeholder="請輸入驗證碼">
                <button onclick="verifyAndLink()">驗證並連結</button>
            </div>
        </div>
    `;
    // 顯示模態框
}
```

**後端 API：**

```javascript
// 1. 發送驗證碼
POST /api/users/send-verification-code
Body: {
    line_user_id: "U1234567890...",
    email: "user@example.com"
}
Response: {
    success: true,
    message: "驗證碼已發送到您的 Email"
}

// 2. 驗證並連結
POST /api/users/verify-and-link
Body: {
    line_user_id: "U1234567890...",
    email: "user@example.com",
    verification_code: "123456"
}
Response: {
    success: true,
    openrice_member_id: "OR123456",
    message: "帳號連結成功"
}
```

---

### 方案 B：手機號碼驗證對應

#### 流程步驟：

```
1. 用戶輸入 OpenRice 註冊手機號碼
   ↓
2. 後端發送簡訊驗證碼
   ↓
3. 用戶輸入驗證碼
   ↓
4. 驗證成功後建立對應
```

**優點**：手機號碼通常更準確
**缺點**：需要簡訊服務（成本）

---

### 方案 C：OpenRice 登入頁面整合（最安全）

#### 流程步驟：

```
1. 用戶點擊「連結 OpenRice 帳號」
   ↓
2. 使用 liff.openWindow() 打開 OpenRice 登入頁面
   ↓
3. 用戶在 OpenRice 登入頁面登入
   ↓
4. OpenRice 登入後重定向回 LIFF App，帶回 Token
   ↓
5. 後端驗證 Token，建立對應關係
```

**優點**：最安全，使用 OpenRice 官方認證
**缺點**：需要 OpenRice 提供 OAuth 整合

---

## 流程 2：不是 OpenRice 會員 - 建立會員流程

### 方案 A：簡化註冊流程（推薦）

#### 流程步驟：

```
1. 檢測到用戶沒有 OpenRice 帳號
   ↓
2. 顯示「建立 OpenRice 帳號」提示
   ↓
3. 使用 LINE 資料預填表單
   ↓
4. 用戶只需補充必要資訊（Email、手機）
   ↓
5. 發送驗證碼驗證
   ↓
6. 完成註冊並自動連結
```

#### 實現細節：

**前端 UI：**

```javascript
// 顯示註冊表單
function showRegistrationModal() {
    const profile = getLiffProfile();
    const modal = `
        <div class="registration-modal">
            <h3>建立 OpenRice 帳號</h3>
            <p>使用您的 LINE 資料快速註冊</p>
            
            <form id="registrationForm">
                <div class="form-group">
                    <label>顯示名稱</label>
                    <input type="text" id="displayName" 
                           value="${profile?.displayName || ''}" 
                           readonly>
                    <small>來自您的 LINE 資料</small>
                </div>
                
                <div class="form-group">
                    <label>Email <span class="required">*</span></label>
                    <input type="email" id="email" 
                           placeholder="your@email.com" required>
                </div>
                
                <div class="form-group">
                    <label>手機號碼 <span class="required">*</span></label>
                    <input type="tel" id="phone" 
                           placeholder="0912345678" required>
                </div>
                
                <div class="form-group">
                    <label>密碼 <span class="required">*</span></label>
                    <input type="password" id="password" 
                           placeholder="至少 8 個字元" required>
                </div>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="agreeTerms" required>
                        我同意 OpenRice 服務條款和隱私政策
                    </label>
                </div>
                
                <button type="submit">建立帳號</button>
            </form>
        </div>
    `;
    // 顯示模態框
}
```

**後端 API：**

```javascript
// 建立 OpenRice 會員並連結 LINE
POST /api/users/register-and-link
Body: {
    line_user_id: "U1234567890...",
    display_name: "用戶名稱",
    picture_url: "https://...",
    email: "user@example.com",
    phone: "0912345678",
    password: "hashed_password"
}
Response: {
    success: true,
    openrice_member_id: "OR123456",
    message: "註冊成功，已自動連結 LINE 帳號"
}
```

---

### 方案 B：跳轉到 OpenRice 註冊頁面

#### 流程步驟：

```
1. 檢測到用戶沒有 OpenRice 帳號
   ↓
2. 顯示提示：「您還沒有 OpenRice 帳號，是否要註冊？」
   ↓
3. 用戶點擊「前往註冊」
   ↓
4. 使用 liff.openWindow() 打開 OpenRice 註冊頁面
   ↓
5. 用戶完成註冊後，回到 LIFF App
   ↓
6. 提示用戶連結帳號（使用流程 1）
```

**優點**：使用 OpenRice 官方註冊流程
**缺點**：用戶體驗較不流暢

---

## 完整流程設計

### 用戶首次使用 LIFF App

```
用戶打開 LIFF App
    ↓
取得 LINE User ID
    ↓
呼叫 /api/users/check-account
    ↓
檢查是否有對應的 OpenRice 會員
    ├─ 有 → 載入用戶資料 → 正常使用
    └─ 沒有 → 顯示選擇畫面
            ├─ 「我已有 OpenRice 帳號」→ 流程 1（Email 驗證）
            └─ 「建立新帳號」→ 流程 2（簡化註冊）
    ↓
完成連結/註冊
    ↓
載入用戶偏好、收藏等
    ↓
個人化體驗
```

---

## 實現範例

### 1. 檢查帳號狀態 API

```javascript
// backend/routes/users.js

/**
 * 檢查用戶是否有 OpenRice 帳號
 */
router.get('/check-account', async (req, res) => {
    try {
        const { line_user_id } = req.query;
        
        if (!line_user_id) {
            return res.status(400).json({ error: 'LINE User ID 是必需的' });
        }
        
        // 查詢是否有對應的 OpenRice 會員
        const user = await db.query(
            'SELECT * FROM openrice_members WHERE line_user_id = ?',
            [line_user_id]
        );
        
        if (user.length > 0) {
            // 已有對應的帳號
            return res.json({
                has_account: true,
                openrice_member_id: user[0].openrice_member_id,
                display_name: user[0].display_name,
                email: user[0].email
            });
        }
        
        // 沒有對應的帳號
        return res.json({
            has_account: false,
            message: '請連結或建立 OpenRice 帳號'
        });
        
    } catch (error) {
        console.error('檢查帳號狀態錯誤:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});
```

### 2. Email 驗證 API

```javascript
/**
 * 發送驗證碼到 Email
 */
router.post('/send-verification-code', async (req, res) => {
    try {
        const { line_user_id, email } = req.body;
        
        if (!line_user_id || !email) {
            return res.status(400).json({ error: 'LINE User ID 和 Email 是必需的' });
        }
        
        // 檢查 Email 是否屬於 OpenRice 會員
        const member = await db.query(
            'SELECT * FROM openrice_members WHERE email = ?',
            [email]
        );
        
        if (member.length === 0) {
            return res.status(404).json({ 
                error: '此 Email 未註冊 OpenRice 帳號',
                suggestion: '請確認 Email 是否正確，或選擇「建立新帳號」'
            });
        }
        
        // 檢查該會員是否已經連結了其他 LINE 帳號
        if (member[0].line_user_id && member[0].line_user_id !== line_user_id) {
            return res.status(409).json({ 
                error: '此 OpenRice 帳號已連結其他 LINE 帳號'
            });
        }
        
        // 生成 6 位數驗證碼
        const verificationCode = Math.floor(100000 + Math.random() * 900000).toString();
        
        // 儲存驗證碼（設定 10 分鐘過期）
        await db.query(
            'INSERT INTO verification_codes (line_user_id, email, code, expires_at) VALUES (?, ?, ?, DATE_ADD(NOW(), INTERVAL 10 MINUTE))',
            [line_user_id, email, verificationCode]
        );
        
        // 發送 Email（使用你的 Email 服務）
        await sendVerificationEmail(email, verificationCode);
        
        res.json({
            success: true,
            message: '驗證碼已發送到您的 Email',
            expires_in: 600 // 10 分鐘
        });
        
    } catch (error) {
        console.error('發送驗證碼錯誤:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});

/**
 * 驗證並連結帳號
 */
router.post('/verify-and-link', async (req, res) => {
    try {
        const { line_user_id, email, verification_code } = req.body;
        
        if (!line_user_id || !email || !verification_code) {
            return res.status(400).json({ error: '所有欄位都是必需的' });
        }
        
        // 驗證驗證碼
        const codeRecord = await db.query(
            'SELECT * FROM verification_codes WHERE line_user_id = ? AND email = ? AND code = ? AND expires_at > NOW() AND used = 0',
            [line_user_id, email, verification_code]
        );
        
        if (codeRecord.length === 0) {
            return res.status(400).json({ error: '驗證碼無效或已過期' });
        }
        
        // 標記驗證碼為已使用
        await db.query(
            'UPDATE verification_codes SET used = 1 WHERE id = ?',
            [codeRecord[0].id]
        );
        
        // 取得 OpenRice 會員資料
        const member = await db.query(
            'SELECT * FROM openrice_members WHERE email = ?',
            [email]
        );
        
        if (member.length === 0) {
            return res.status(404).json({ error: '找不到 OpenRice 會員' });
        }
        
        // 建立連結
        await db.query(
            'UPDATE openrice_members SET line_user_id = ? WHERE openrice_member_id = ?',
            [line_user_id, member[0].openrice_member_id]
        );
        
        res.json({
            success: true,
            message: '帳號連結成功',
            openrice_member_id: member[0].openrice_member_id,
            display_name: member[0].display_name
        });
        
    } catch (error) {
        console.error('驗證並連結錯誤:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});
```

### 3. 註冊並連結 API

```javascript
/**
 * 建立 OpenRice 會員並連結 LINE
 */
router.post('/register-and-link', async (req, res) => {
    try {
        const { 
            line_user_id, 
            display_name, 
            picture_url, 
            email, 
            phone, 
            password 
        } = req.body;
        
        // 驗證必填欄位
        if (!line_user_id || !email || !phone || !password) {
            return res.status(400).json({ error: '必填欄位未填寫' });
        }
        
        // 檢查 Email 是否已被使用
        const existingEmail = await db.query(
            'SELECT * FROM openrice_members WHERE email = ?',
            [email]
        );
        
        if (existingEmail.length > 0) {
            return res.status(409).json({ 
                error: '此 Email 已被註冊',
                suggestion: '請使用「連結現有帳號」功能'
            });
        }
        
        // 檢查手機號碼是否已被使用
        const existingPhone = await db.query(
            'SELECT * FROM openrice_members WHERE phone = ?',
            [phone]
        );
        
        if (existingPhone.length > 0) {
            return res.status(409).json({ error: '此手機號碼已被註冊' });
        }
        
        // 生成 OpenRice 會員 ID
        const openrice_member_id = 'OR' + Date.now() + Math.floor(Math.random() * 1000);
        
        // 加密密碼（使用 bcrypt）
        const hashedPassword = await bcrypt.hash(password, 10);
        
        // 建立新會員
        await db.query(
            `INSERT INTO openrice_members 
             (openrice_member_id, line_user_id, display_name, picture_url, email, phone, password, created_at) 
             VALUES (?, ?, ?, ?, ?, ?, ?, NOW())`,
            [openrice_member_id, line_user_id, display_name, picture_url, email, phone, hashedPassword]
        );
        
        res.json({
            success: true,
            message: '註冊成功，已自動連結 LINE 帳號',
            openrice_member_id: openrice_member_id,
            display_name: display_name
        });
        
    } catch (error) {
        console.error('註冊並連結錯誤:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});
```

---

## 前端實現範例

### 檢查帳號狀態並顯示對應 UI

```javascript
// frontend/liff/pages/components/user-integration.js

/**
 * 檢查帳號狀態並處理
 */
export async function checkAndHandleAccount() {
    const profile = getLiffProfile();
    if (!profile || !profile.userId) {
        return;
    }
    
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/users/check-account?line_user_id=${profile.userId}`
        );
        
        const data = await response.json();
        
        if (data.has_account) {
            // 已有帳號，載入用戶資料
            console.log('用戶已有 OpenRice 帳號:', data);
            return { hasAccount: true, memberData: data };
        } else {
            // 沒有帳號，顯示選擇畫面
            showAccountChoiceModal();
            return { hasAccount: false };
        }
    } catch (error) {
        console.error('檢查帳號狀態錯誤:', error);
        return null;
    }
}

/**
 * 顯示帳號選擇畫面
 */
function showAccountChoiceModal() {
    const modal = document.createElement('div');
    modal.className = 'account-choice-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>連結 OpenRice 帳號</h3>
            <p>為了提供更好的個人化體驗，請連結或建立 OpenRice 帳號</p>
            
            <div class="choice-buttons">
                <button class="choice-btn" onclick="showLinkAccountModal()">
                    <span class="icon">🔗</span>
                    <span class="text">我已有 OpenRice 帳號</span>
                    <span class="subtext">使用 Email 驗證連結</span>
                </button>
                
                <button class="choice-btn" onclick="showRegistrationModal()">
                    <span class="icon">✨</span>
                    <span class="text">建立新帳號</span>
                    <span class="subtext">快速註冊 OpenRice</span>
                </button>
            </div>
            
            <button class="skip-btn" onclick="skipAccountLink()">
                稍後再說
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// 在首頁初始化時調用
export async function initUserAccount() {
    const accountStatus = await checkAndHandleAccount();
    
    if (accountStatus && accountStatus.hasAccount) {
        // 載入用戶偏好設定
        const preferences = await getUserPreferences();
        if (preferences) {
            // 應用偏好到表單
            applyUserPreferences(preferences);
        }
    }
}
```

---

## 資料庫設計

### 驗證碼表

```sql
CREATE TABLE verification_codes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    line_user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL,
    expires_at DATETIME NOT NULL,
    used TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_line_user_email (line_user_id, email),
    INDEX idx_expires (expires_at)
);
```

---

## 總結

### 流程 1：已有 OpenRice 帳號
1. 用戶輸入 Email
2. 發送驗證碼到 Email
3. 用戶輸入驗證碼
4. 驗證成功後建立對應

### 流程 2：沒有 OpenRice 帳號
1. 顯示簡化註冊表單
2. 使用 LINE 資料預填
3. 用戶補充必要資訊
4. 完成註冊並自動連結

### 建議
- **優先使用 Email 驗證**：簡單、安全、成本低
- **提供簡化註冊**：提升用戶體驗
- **允許稍後連結**：不要強制，讓用戶選擇

需要我幫你實現這些功能嗎？
