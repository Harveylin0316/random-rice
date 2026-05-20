#!/usr/bin/env python3
"""
用 Gemini 為餐廳生成個性化 slogan（替代 OpenRice 標籤雜訊太多的規則式生成）

用法:
  python3 _rebuild/generate_slogans.py --spike     # 只跑 spike 2-3 家看效果
  python3 _rebuild/generate_slogans.py --all       # 跑全部 enabled 餐廳並寫入 DB

依賴：環境變數 GEMINI_API_KEY（沿用 line-menu-photo-bot 的 key + CF Worker proxy）
"""
import os
import json
import argparse
import time
import requests
from pathlib import Path

# 從 line-menu-photo-bot 的 .env 借用設定
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    env_file = Path.home() / 'Desktop/Claude-workspace/projects/line-menu-photo-bot/.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith('GEMINI_API_KEY='):
                GEMINI_API_KEY = line.split('=', 1)[1].strip()
                break

# 本機跑直接打 Google API；如要在 Render Singapore 跑改回 worker proxy
GEMINI_BASE = os.environ.get('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com')
MODEL = 'gemini-2.5-flash'

SYSTEM_PROMPT = """你是台灣餐廳文案專家，為「隨機抽餐廳」App 卡片頂部寫趣味 slogan。

【判斷餐廳類型的優先序】
1. 真實食客評論摘錄（如有提供）← 最高優先
2. 餐廳名稱（OpenRice 標籤常常錯：例鐵板燒被標義大利料理、肉舖被標咖啡廳）
3. OpenRice 標籤（最低優先，僅供交叉驗證）

【絕對禁止 — 違反就重寫】
1. **任何台灣地名／街道／商圈／夜市／景點／行政區一律禁用**。包含但不限於：永康街、東門、信義區、西門町、寧夏夜市、五分埔、士林、安和路、忠孝東路、敦化、台中草悟道、高雄駁二、宜蘭冬山……。即使你從訓練資料「知道」這家店在哪，也不可寫地名。
   - 反例：「永康街小店」「冬山質感選擇」「東門名店」← 都禁止
   - 正例（如要描述地點）：「市區轉角」「街邊小店」「鬧區裡的」
2. 不可寫廣告腔：歡迎光臨、美食推薦、天選之人、運氣爆棚、人品大爆發、味蕾旅行、療癒你的胃
3. 不可寫具體菜名（除非食記反覆提到，且是該店真招牌）
4. 不可五條都用「想吃 X」「今晚 X」「下班 X」這類同句型開頭
5. 不可寫「下班怒吃」「犒賞自己」「療癒你身心」這種濫用詞

【五條 slogan 必須分五種角度】
- 第 1 條：實際特色（從名稱／食記判斷的真實類型，例：鐵板燒、肉舖、餐酒館、咖啡廳）
- 第 2 條：適合的場景（聚餐／小酌／一個人吃／聚會）
- 第 3 條：呼應「隨機抽到」的趣味（命運、骰子、就決定是你）
- 第 4 條：氛圍／口感／價位的描述
- 第 5 條：短金句（5-8 字）

【長度】每條 8-13 字（含標點）；短金句條 5-8 字。繁體中文。

【良好範例】
- 鐵板秀今晚就看你
- 想小酌就找這家
- 抽到肉食控的命運
- 平價也吃得開心
- 就決定是它了

輸出格式：嚴格五行，每行一句，無編號、無引號、無解釋、無 markdown。"""

USER_PROMPT_TEMPLATE = """餐廳資料：
- 名稱：{name}
- 地址：{address}
- 區域：{region} / {district}
- 預算：{budget}
- OpenRice 標籤（僅供交叉驗證、可能不準）：料理={cuisines}，類型={types}
{reviews_section}
請生五條 slogan。"""

REVIEWS_SECTION_TEMPLATE = """- 真實食客評論摘錄（重要參考）：
{reviews}
"""


def generate_for_restaurant(r, reviews_excerpts=None):
    """reviews_excerpts: list[str]，每條為食記摘錄。沒給就只用結構化資料。"""
    name = r.get('name', '')
    address = r.get('address', '')
    region = r.get('region', '')
    district = r.get('district', '')
    budget = r.get('budget') or '未標示'
    cuisines = ', '.join(r.get('cuisine_style') or []) or '無'
    types = ', '.join(r.get('type') or []) or '無'

    if reviews_excerpts:
        # 限制總長度避免 prompt 過長
        joined = '\n'.join(f'  · 「{e}」' for e in reviews_excerpts[:3])
        reviews_section = REVIEWS_SECTION_TEMPLATE.format(reviews=joined)
    else:
        reviews_section = ''

    user_prompt = USER_PROMPT_TEMPLATE.format(
        name=name, address=address, region=region, district=district,
        budget=budget, cuisines=cuisines, types=types,
        reviews_section=reviews_section,
    )

    payload = {
        'systemInstruction': {'parts': [{'text': SYSTEM_PROMPT}]},
        'contents': [{'role': 'user', 'parts': [{'text': user_prompt}]}],
        'generationConfig': {'temperature': 0.7, 'maxOutputTokens': 600, 'thinkingConfig': {'thinkingBudget': 0}},
    }
    url = f'{GEMINI_BASE}/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}'
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    text = data['candidates'][0]['content']['parts'][0]['text']
    # parse 5 行，去 emoji / 編號 / 過長
    import re as _re
    lines = []
    for l in text.strip().splitlines():
        l = l.strip().lstrip('-•').strip()
        # 去掉開頭數字編號 「1.」「1、」「1)」
        l = _re.sub(r'^\d+[.、。\):、]\s*', '', l)
        # 去引號
        l = l.strip('「」"\'""''')
        if not l or l.startswith('#'):
            continue
        # 長度過濾（保守一點：4-16 字）
        if len(l) < 4 or len(l) > 16:
            continue
        lines.append(l)
    return lines[:5]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spike', action='store_true', help='只跑 2-3 家看效果，不寫 DB')
    ap.add_argument('--all', action='store_true', help='跑全部 enabled 餐廳並寫入 DB')
    ap.add_argument('--target', default='restaurants_database.json')
    ap.add_argument('--limit', type=int)
    args = ap.parse_args()

    if not GEMINI_API_KEY:
        print('❌ 找不到 GEMINI_API_KEY')
        return

    with open(args.target, encoding='utf-8') as f:
        data = json.load(f)
    db = data['restaurants']

    if args.spike:
        # 之前 sample 看到的「問題店」 + 對照組
        target_names = [
            '犇鐵板燒 安和本館',           # OR 標日法義料理但實際鐵板燒
            'Butcher Restaurant by EZ-MEAT 一極肉舖',  # OR 標咖啡廳實際肉舖餐酒
            'mo labo 墨拿',                # OR 標籤空、之前 LLM 編出永康街
            '金豬食堂',                    # OR 標籤空、之前 LLM 猜韓式
            '日光私廚',                    # 義式但之前「私廚約會」調性怪
            '椰糖 Coconut Sugar 南洋餐事', # 對照組
        ]
        targets = []
        for name in target_names:
            for r in db:
                if r.get('name') == name:
                    targets.append(r); break
        print(f'Spike: {len(targets)} 家')
        for r in targets:
            print(f'\n--- {r["name"]} ---')
            print(f'  region={r.get("region")} budget={r.get("budget")}')
            print(f'  OR cuisines={r.get("cuisine_style")} types={r.get("type")}')
            try:
                slogans = generate_for_restaurant(r)
                print(f'  Gemini 生成 {len(slogans)} 條 slogan:')
                for s in slogans:
                    print(f'    - {s}')
            except Exception as e:
                print(f'  ❌ {e}')
            time.sleep(0.5)
        return

    if args.all:
        targets = [r for r in db if r.get('enabled') and not r.get('slogans')]
        if args.limit:
            targets = targets[:args.limit]
        print(f'全量目標: {len(targets)} 家')
        ok, fail = 0, 0
        for i, r in enumerate(targets, 1):
            try:
                slogans = generate_for_restaurant(r)
                if slogans:
                    r['slogans'] = slogans
                    ok += 1
                    if i % 30 == 0 or i == 1:
                        print(f'  [{i}/{len(targets)}] {r["name"][:25]} → {len(slogans)} 條')
                        print(f'    範例: {slogans[0]}')
                else:
                    fail += 1
            except Exception as e:
                fail += 1
                print(f'  [{i}] ❌ {r["name"]}: {e}')
            # 每 30 筆暫存
            if i % 30 == 0:
                with open(args.target, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f'    --- 已存 {i}/{len(targets)}（ok={ok} fail={fail}）---')
            time.sleep(0.3)  # 0.3s 間隔避免被 rate limit

        # 最終寫入
        with open(args.target, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # 同步 netlify
        netlify_path = 'netlify/functions/restaurants_database.json'
        if os.path.exists(netlify_path):
            with open(netlify_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'\n完成：ok={ok} fail={fail}')
        return

    ap.print_help()


if __name__ == '__main__':
    main()
