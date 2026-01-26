# LINE 分眾行銷 - 用戶標籤設計

## 可記錄的用戶標籤類型

### 1. 基本資料標籤（來自 LINE Profile）

#### 1.1 用戶識別
- `line_user_id`: LINE User ID（唯一識別碼）
- `display_name`: 顯示名稱
- `picture_url`: 大頭貼 URL
- `status_message`: 狀態訊息

#### 1.2 設備資訊
- `os`: 作業系統（iOS/Android/Web）
- `language`: 語言設定（zh-TW/en/ja 等）
- `liff_version`: LIFF SDK 版本

---

### 2. 使用行為標籤

#### 2.1 使用頻率
- `first_use_date`: 首次使用日期
- `last_use_date`: 最後使用日期
- `total_use_count`: 總使用次數
- `use_frequency`: 使用頻率（每日/每週/每月）
- `days_since_last_use`: 距離上次使用的天數

#### 2.2 使用時段
- `preferred_time`: 偏好使用時段（早上/中午/晚上/深夜）
- `weekday_usage`: 平日使用次數
- `weekend_usage`: 週末使用次數

#### 2.3 使用深度
- `avg_search_per_session`: 每次使用平均搜尋次數
- `avg_results_viewed`: 平均查看的餐廳數量
- `session_duration`: 平均使用時長

---

### 3. 偏好標籤（料理相關）

#### 3.1 料理風格偏好
- `favorite_cuisine_1`: 最常選擇的料理風格（例如：台式料理）
- `favorite_cuisine_2`: 第二常選擇的料理風格
- `favorite_cuisine_3`: 第三常選擇的料理風格
- `cuisine_diversity`: 料理風格多樣性（選擇過幾種不同風格）
- `cuisine_preference_score`: 各料理風格的偏好分數

**範例標籤：**
- `cuisine_台式料理_high`（選擇頻率 > 50%）
- `cuisine_日式料理_medium`（選擇頻率 20-50%）
- `cuisine_多樣化`（選擇過 5 種以上不同風格）

#### 3.2 餐廳類型偏好
- `favorite_type_1`: 最常選擇的餐廳類型（例如：燒肉）
- `favorite_type_2`: 第二常選擇的餐廳類型
- `favorite_type_3`: 第三常選擇的餐廳類型
- `type_diversity`: 餐廳類型多樣性

**範例標籤：**
- `type_燒肉_lover`（選擇頻率 > 50%）
- `type_火鍋_fan`（選擇頻率 30-50%）
- `type_咖啡廳_occasional`（選擇頻率 < 20%）

#### 3.3 預算偏好
- `preferred_budget_range`: 最常選擇的預算範圍
- `budget_tier`: 預算等級（低/中/高）
- `budget_consistency`: 預算選擇一致性

**範例標籤：**
- `budget_low`（200元內）
- `budget_medium`（200-1000元）
- `budget_high`（1000元以上）
- `budget_flexible`（預算選擇多樣）

---

### 4. 地理位置標籤

#### 4.1 使用位置模式
- `location_mode_preference`: 偏好的位置模式（附近餐廳/選擇地區）
- `uses_nearby_search`: 是否使用附近餐廳功能
- `uses_area_search`: 是否使用選擇地區功能

#### 4.2 地區偏好
- `favorite_city`: 最常搜尋的縣市
- `favorite_district`: 最常搜尋的行政區
- `location_diversity`: 搜尋地區多樣性
- `home_city`: 推測的居住城市（根據使用頻率）

**範例標籤：**
- `location_台北市_primary`
- `location_新北市_secondary`
- `location_multi_city`（搜尋過 3 個以上不同城市）

#### 4.3 交通方式偏好
- `transport_preference`: 偏好的交通方式（走路/開車）
- `walking_user`: 主要使用走路 10 分鐘
- `driving_user`: 主要使用開車 10 分鐘

---

### 5. 互動行為標籤

#### 5.1 搜尋行為
- `search_count`: 總搜尋次數
- `avg_filters_used`: 平均使用的篩選條件數量
- `prefers_specific_search`: 偏好使用特定篩選（vs 不限）
- `prefers_broad_search`: 偏好使用「不限」選項

#### 5.2 結果互動
- `clicks_booking`: 點擊訂位按鈕次數
- `clicks_navigation`: 點擊導航按鈕次數
- `views_restaurant_details`: 查看餐廳詳情次數
- `uses_refresh_button`: 使用「換一批」按鈕次數

#### 5.3 收藏行為
- `favorites_count`: 收藏餐廳數量
- `favorite_categories`: 收藏的餐廳類型分布
- `favorite_restaurants`: 收藏的餐廳列表

---

### 6. 轉換行為標籤

#### 6.1 行動轉換
- `high_booking_intent`: 高訂位意圖（點擊訂位 > 3 次）
- `high_navigation_intent`: 高導航意圖（點擊導航 > 3 次）
- `conversion_rate`: 轉換率（點擊訂位/搜尋次數）

#### 6.2 參與度
- `high_engagement`: 高參與度用戶（使用頻率高）
- `medium_engagement`: 中等參與度
- `low_engagement`: 低參與度
- `dormant_user`: 休眠用戶（30 天未使用）

---

### 7. 時間相關標籤

#### 7.1 使用時機
- `lunch_seeker`: 午餐時段使用者（11:00-14:00）
- `dinner_seeker`: 晚餐時段使用者（17:00-21:00）
- `late_night_seeker`: 宵夜時段使用者（21:00-02:00）
- `weekend_user`: 週末使用者
- `weekday_user`: 平日使用者

#### 7.2 季節性
- `seasonal_user`: 季節性用戶（特定月份使用）
- `consistent_user`: 持續使用用戶

---

### 8. 用戶生命週期標籤

#### 8.1 新用戶
- `new_user`: 新用戶（7 天內首次使用）
- `first_week_user`: 第一週用戶

#### 8.2 活躍用戶
- `active_user`: 活躍用戶（30 天內使用 > 5 次）
- `super_active_user`: 超級活躍（30 天內使用 > 15 次）

#### 8.3 流失風險
- `at_risk_user`: 流失風險用戶（7-14 天未使用）
- `churned_user`: 流失用戶（30 天未使用）

---

## 標籤記錄實現

### 資料結構設計

```javascript
// 用戶標籤資料結構
{
    line_user_id: "U1234567890...",
    
    // 基本資料
    profile: {
        display_name: "用戶名稱",
        picture_url: "https://...",
        language: "zh-TW",
        os: "iOS"
    },
    
    // 使用行為
    usage: {
        first_use_date: "2024-01-15",
        last_use_date: "2024-01-26",
        total_use_count: 25,
        total_search_count: 45,
        avg_session_duration: 180, // 秒
        preferred_time: "evening", // morning/afternoon/evening/late_night
        weekday_usage: 15,
        weekend_usage: 10
    },
    
    // 偏好標籤
    preferences: {
        cuisine: {
            "台式料理": { count: 15, percentage: 33.3 },
            "日式料理": { count: 10, percentage: 22.2 },
            "韓式料理": { count: 8, percentage: 17.8 }
        },
        type: {
            "燒肉": { count: 12, percentage: 26.7 },
            "火鍋": { count: 10, percentage: 22.2 }
        },
        budget: {
            preferred_range: "500-1000元",
            distribution: {
                "200元內": 5,
                "200-500元": 10,
                "500-1000元": 20,
                "1000-1500元": 8,
                "1500以上": 2
            }
        }
    },
    
    // 地理位置
    location: {
        mode_preference: "nearby", // nearby/area
        favorite_city: "台北市",
        favorite_district: "大安區",
        cities_searched: ["台北市", "新北市"],
        uses_nearby: true,
        uses_area: false
    },
    
    // 互動行為
    interactions: {
        clicks_booking: 12,
        clicks_navigation: 18,
        views_details: 35,
        uses_refresh: 8,
        favorites_count: 5
    },
    
    // 計算標籤
    tags: [
        "cuisine_台式料理_high",
        "type_燒肉_lover",
        "budget_medium",
        "location_台北市_primary",
        "transport_walking",
        "high_engagement",
        "active_user",
        "dinner_seeker",
        "weekend_user"
    ]
}
```

---

## 標籤計算邏輯

### 1. 偏好標籤計算

```javascript
function calculatePreferenceTags(userData) {
    const tags = [];
    
    // 料理風格偏好
    const cuisineStats = userData.preferences.cuisine;
    const topCuisine = Object.entries(cuisineStats)
        .sort((a, b) => b[1].percentage - a[1].percentage)[0];
    
    if (topCuisine[1].percentage > 50) {
        tags.push(`cuisine_${topCuisine[0]}_high`);
    } else if (topCuisine[1].percentage > 30) {
        tags.push(`cuisine_${topCuisine[0]}_medium`);
    }
    
    // 多樣性標籤
    const cuisineCount = Object.keys(cuisineStats).length;
    if (cuisineCount >= 5) {
        tags.push('cuisine_diverse');
    }
    
    // 餐廳類型偏好
    const typeStats = userData.preferences.type;
    const topType = Object.entries(typeStats)
        .sort((a, b) => b[1].percentage - a[1].percentage)[0];
    
    if (topType[1].percentage > 50) {
        tags.push(`type_${topType[0]}_lover`);
    }
    
    // 預算標籤
    const budgetRange = userData.preferences.budget.preferred_range;
    if (budgetRange.includes('200元內')) {
        tags.push('budget_low');
    } else if (budgetRange.includes('1000以上')) {
        tags.push('budget_high');
    } else {
        tags.push('budget_medium');
    }
    
    return tags;
}
```

### 2. 使用行為標籤計算

```javascript
function calculateUsageTags(userData) {
    const tags = [];
    const usage = userData.usage;
    
    // 參與度標籤
    const daysSinceFirstUse = Math.floor(
        (new Date() - new Date(usage.first_use_date)) / (1000 * 60 * 60 * 24)
    );
    const avgDailyUsage = usage.total_use_count / Math.max(daysSinceFirstUse, 1);
    
    if (avgDailyUsage > 0.5) {
        tags.push('high_engagement');
    } else if (avgDailyUsage > 0.2) {
        tags.push('medium_engagement');
    } else {
        tags.push('low_engagement');
    }
    
    // 用戶生命週期
    const daysSinceLastUse = Math.floor(
        (new Date() - new Date(usage.last_use_date)) / (1000 * 60 * 60 * 24)
    );
    
    if (daysSinceLastUse <= 7) {
        tags.push('active_user');
    } else if (daysSinceLastUse <= 14) {
        tags.push('at_risk_user');
    } else if (daysSinceLastUse <= 30) {
        tags.push('dormant_user');
    } else {
        tags.push('churned_user');
    }
    
    // 使用時段
    if (usage.preferred_time === 'evening') {
        tags.push('dinner_seeker');
    } else if (usage.preferred_time === 'late_night') {
        tags.push('late_night_seeker');
    }
    
    // 週末 vs 平日
    if (usage.weekend_usage > usage.weekday_usage) {
        tags.push('weekend_user');
    } else {
        tags.push('weekday_user');
    }
    
    return tags;
}
```

### 3. 地理位置標籤計算

```javascript
function calculateLocationTags(userData) {
    const tags = [];
    const location = userData.location;
    
    // 主要城市
    if (location.favorite_city) {
        tags.push(`location_${location.favorite_city}_primary`);
    }
    
    // 多城市用戶
    if (location.cities_searched.length >= 3) {
        tags.push('location_multi_city');
    }
    
    // 位置模式偏好
    if (location.mode_preference === 'nearby') {
        tags.push('location_nearby_preferred');
    } else {
        tags.push('location_area_preferred');
    }
    
    return tags;
}
```

---

## LINE 分眾行銷應用

### 標籤分組範例

#### 1. 料理偏好分眾
- `cuisine_台式料理_high` → 推播台式料理優惠
- `cuisine_日式料理_high` → 推播日式料理優惠
- `cuisine_diverse` → 推播多樣化優惠

#### 2. 預算分眾
- `budget_low` → 推播平價餐廳優惠
- `budget_high` → 推播高級餐廳優惠

#### 3. 地區分眾
- `location_台北市_primary` → 推播台北市餐廳優惠
- `location_新北市_primary` → 推播新北市餐廳優惠

#### 4. 參與度分眾
- `high_engagement` → 推播新功能、深度優惠
- `at_risk_user` → 推播回訪優惠、新餐廳
- `dormant_user` → 推播喚醒訊息、特別優惠

#### 5. 時段分眾
- `dinner_seeker` → 晚餐時段推播
- `late_night_seeker` → 宵夜時段推播

---

## 資料收集實現

### 事件追蹤設計

```javascript
// frontend/liff/pages/components/analytics.js

/**
 * 追蹤用戶行為
 */
export function trackEvent(eventType, eventData) {
    const profile = getLiffProfile();
    if (!profile || !profile.userId) {
        return;
    }
    
    const event = {
        line_user_id: profile.userId,
        event_type: eventType,
        event_data: eventData,
        timestamp: new Date().toISOString(),
        session_id: getSessionId()
    };
    
    // 發送到後端 API
    fetch(`${API_BASE_URL}/api/analytics/track`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(event)
    }).catch(err => console.error('追蹤事件失敗:', err));
}

// 使用範例
trackEvent('search', {
    cuisine_style: ['台式料理'],
    type: ['燒肉'],
    budget: '500-1000元',
    location_mode: 'nearby',
    city: '台北市'
});

trackEvent('click_booking', {
    restaurant_name: '餐廳名稱',
    restaurant_url: 'https://...'
});

trackEvent('click_navigation', {
    restaurant_name: '餐廳名稱',
    restaurant_address: '地址'
});
```

---

## 後端 API 設計

### 標籤更新 API

```javascript
// backend/routes/analytics.js

/**
 * 更新用戶標籤
 */
router.post('/update-tags', async (req, res) => {
    try {
        const { line_user_id } = req.body;
        
        // 取得用戶所有行為資料
        const userData = await getUserBehaviorData(line_user_id);
        
        // 計算標籤
        const tags = [
            ...calculatePreferenceTags(userData),
            ...calculateUsageTags(userData),
            ...calculateLocationTags(userData)
        ];
        
        // 更新用戶標籤
        await updateUserTags(line_user_id, tags);
        
        res.json({
            success: true,
            tags: tags
        });
        
    } catch (error) {
        console.error('更新標籤錯誤:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});

/**
 * 取得用戶標籤（供 LINE 分眾使用）
 */
router.get('/tags', async (req, res) => {
    try {
        const { line_user_id } = req.query;
        
        const tags = await getUserTags(line_user_id);
        
        res.json({
            line_user_id: line_user_id,
            tags: tags
        });
        
    } catch (error) {
        console.error('取得標籤錯誤:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});
```

---

## LINE 分眾行銷整合

### 匯出標籤到 LINE

```javascript
/**
 * 匯出用戶標籤到 LINE 分眾系統
 */
async function exportTagsToLine() {
    // 取得所有用戶標籤
    const allUsers = await getAllUsersWithTags();
    
    // 轉換為 LINE 分眾格式
    const segments = {};
    
    allUsers.forEach(user => {
        user.tags.forEach(tag => {
            if (!segments[tag]) {
                segments[tag] = [];
            }
            segments[tag].push(user.line_user_id);
        });
    });
    
    // 更新 LINE 分眾（使用 LINE Messaging API）
    for (const [tag, userIds] of Object.entries(segments)) {
        await updateLineAudience(tag, userIds);
    }
}
```

---

## 建議的標籤優先級

### 高優先級標籤（核心分眾）
1. **料理偏好**: `cuisine_*_high`
2. **預算等級**: `budget_low/medium/high`
3. **地區**: `location_*_primary`
4. **參與度**: `high/medium/low_engagement`

### 中優先級標籤（細分）
1. **餐廳類型**: `type_*_lover`
2. **使用時段**: `dinner_seeker`, `late_night_seeker`
3. **用戶生命週期**: `active_user`, `at_risk_user`

### 低優先級標籤（輔助）
1. **多樣性**: `cuisine_diverse`, `location_multi_city`
2. **交通方式**: `transport_walking`, `transport_driving`

---

## 總結

### 可記錄的標籤類型

1. ✅ **基本資料**: LINE User ID, 顯示名稱, 語言, OS
2. ✅ **使用行為**: 使用頻率, 時段, 深度
3. ✅ **偏好標籤**: 料理風格, 餐廳類型, 預算
4. ✅ **地理位置**: 城市, 行政區, 位置模式
5. ✅ **互動行為**: 點擊訂位, 導航, 收藏
6. ✅ **轉換行為**: 訂位意圖, 參與度
7. ✅ **時間相關**: 使用時機, 季節性
8. ✅ **生命週期**: 新用戶, 活躍, 流失風險

### 分眾行銷應用

- 根據料理偏好推播相關優惠
- 根據預算推播適合的餐廳
- 根據地區推播當地餐廳
- 根據參與度推播不同內容
- 根據使用時段推播適時訊息

需要我幫你實現標籤追蹤系統嗎？
