# 版本歷史記錄

## 版本標籤說明

### v1.0.0-web
**標籤**: `v1.0.0-web`  
**日期**: 2024-01-26  
**說明**: Web App 版本 1.0.0 - 完成餐廳推薦功能

**功能包含：**
- ✅ 餐廳推薦功能（今天吃什麼）
- ✅ 料理風格、餐廳類型、預算篩選
- ✅ 地理位置功能（附近餐廳/選擇地區）
- ✅ 餐廳卡片顯示（圖片輪播、訂位、導航）
- ✅ 響應式設計（移動端優化）
- ✅ 共享模組架構（api.js, constants.js, utils.js）

**Git Commit**: 查看標籤對應的 commit

---

### v1.0.0-liff
**標籤**: `v1.0.0-liff`  
**日期**: 2024-01-26  
**說明**: LIFF App 版本 1.0.0 - 完成餐廳推薦功能和 LINE 整合

**功能包含：**
- ✅ 所有 Web App 功能
- ✅ LINE LIFF SDK 整合
- ✅ LINE 用戶認證（取得 LINE User ID）
- ✅ LINE 特定功能（分享、關閉按鈕）
- ✅ 路由系統架構（支持多頁面擴展）
- ✅ UI/UX 優化（LINE 內瀏覽器適配）
- ✅ LIFF ID 配置：`2008944358-649rLhGj`

**Git Commit**: 查看標籤對應的 commit

---

## 如何查看版本

### 查看標籤
```bash
git tag -l
```

### 查看特定版本的代碼
```bash
git checkout v1.0.0-web
git checkout v1.0.0-liff
```

### 回到最新版本
```bash
git checkout main
```

### 查看版本差異
```bash
git diff v1.0.0-web v1.0.0-liff
```

---

## 版本對應的檔案結構

### Web App (v1.0.0-web)
```
frontend/web/
├── index.html
├── app.js
├── style.css
└── shared/
    ├── api.js
    ├── constants.js
    └── utils.js
```

### LIFF App (v1.0.0-liff)
```
frontend/liff/
├── index.html
├── app.js
├── style.css
├── pages/
│   ├── router.js
│   ├── home.js
│   └── components/
│       └── liff-features.js
└── shared/
    ├── api.js
    ├── constants.js
    └── utils.js
```

---

## 未來版本規劃

### v1.1.0（計劃中）
- [ ] OpenRice 會員整合
- [ ] 用戶偏好設定
- [ ] 收藏餐廳功能

### v1.2.0（計劃中）
- [ ] 好友一起選餐廳功能
- [ ] 推薦碼系統
- [ ] LINE 裂變行銷功能

### v2.0.0（計劃中）
- [ ] 餐廳投票競賽
- [ ] 挑戰任務系統
- [ ] 完整的數據分析

---

## 備註

- 所有版本都已經推送到 GitHub
- 使用 `git tag` 可以隨時回到特定版本
- 建議在重大功能更新時創建新版本標籤
