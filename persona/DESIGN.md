# DESIGN.md — GhostUsers

> このファイルは AI エージェントが正確な日本語 UI を生成するためのデザイン仕様書です。
> セクションヘッダーは英語、値の説明は日本語で記述しています。
> プロジェクト: GhostUsers — AI仮想ユーザー群によるプロダクト事前 UX 検証ダッシュボード

---

## 0. About GhostUsers

GhostUsers は、URL を渡すと **多様な属性を持つAI仮想ユーザー（ペルソナ）の群れ** が同時にアプリを操作し、迷い・つまずき・離脱を自動レポート化する UX 事前検証ツール。

- **Dynamic（動）**：検証実行中。ペルソナの群れが画面上で動き、思考ログ／メトリクスがストリームで流れる
- **Static（静）**：検証完了後。Scan & Override 演出で静止し、編集的なレポート画面へ切り替わる

デザインの目的は、この **「動 → 静」の鮮やかなコントラスト** を支えること。

---

## 1. Visual Theme & Atmosphere

- **デザイン方針**: クリーン、ミニマル、編集的（editorial）。Bloomberg / The Pudding 系の "データジャーナリズム" 美学を SaaS に持ち込む
- **密度**: 3カラムダッシュボードは情報量はあるが、各セルには余白を残す。詰めない
- **キーワード**: 白基調、編集的、テック、データ、動と静のコントラスト、ペルソナ群、Mono ラベル
- **トーン**: 派手な演出に頼らず、**タイポグラフィとマイクロアニメーション** で「動いている感」を作る
- **ダークモード**: 作らない。**明るいことが商標**

### 動 / 静 の二相性（最重要）

| Phase | 状態 | アニメーション | 役割 |
|---|---|---|---|
| Dynamic | 検証実行中 | ペルソナ swarm、ログのスクロール、グリッチ風破線 | プロセスの可視化、エンタメ性 |
| Transition | Scan & Override | 上→下にスキャンライン、画面が "上書き" される | 1セッションに1度の演出 |
| Static | レポート表示 | ほぼ静止、数字 reveal とパルスのみ | 説得力、編集的説得 |

---

## 2. Color Palette & Roles

### Primary（ブランドカラー）

- **Phantom Coral** (`#ff4d2c`): GhostUsers のシグネチャーアクセント。CTA ハイライト、Critical なリンク、Confusion Score 高領域、Scan ライン
- **Phantom Mist** (`#fff5f2`): Coral 系の薄い背景（Alert カードの surface、ホバー状態）

### Neutral（ニュートラル）

- **Text Primary** (`#1a1a1a`): 本文テキスト。純黒は使わない
- **Text Secondary** (`#707070`): 補足テキスト、ラベル、メタ情報
- **Text Tertiary** (`#a8a8a8`): 注釈、無効状態、控えめなメタ
- **Background** (`#ffffff`): ページ背景
- **Surface Light** (`#f7f7f7`): カード背景、セクション区切り
- **Surface Lighter** (`#fafafa`): サブセクション
- **CTA Surface** (`#1a1a1a`): プライマリ CTA 背景
- **Border / Hairline** (`#e8e8e8`): ハイラインボーダー
- **Border Strong** (`#d4d4d4`): ホバー時のボーダー強調

### Semantic（意味的な色）

- **Success / Calm** (`#3fb069`): タスク完了、低 Confusion Score、Live インジケータ
- **Warning / Alert** (`#ff4d2c`): 高 Confusion、Critical issue（Phantom Coral と同色）
- **Info / Neutral state** (`#707070`): 進行中、ニュートラル状態

### Accent 代替案（採用時に1つだけ選ぶこと）

Phantom Coral 以外の選択肢を保持する場合：

- **Spectral Indigo** (`#5b4cff`): ゴーストらしい神秘感、クールな印象
- **Phantom Violet** (`#7c5bff`): やや明るく、AI らしい未来感
- **Pure Mono**: アクセントなし、`#1a1a1a` と `#ffffff` のみで構成

> **採用ルール**: アクセント色は1つだけ。複数の色相を混ぜない。

---

## 3. Typography Rules

### 3.1 和文フォント

- **ゴシック体**: Noto Sans JP（Google Fonts、weight 400 / 500 / 600）

### 3.2 欧文フォント

- **サンセリフ**: Inter（Google Fonts、weight 400 / 500 / 600）
- **等幅 (Mono)**: IBM Plex Mono（Google Fonts、weight 400 / 500）

> **役割分担**: Inter / Noto Sans JP は本文・見出し用。IBM Plex Mono は **技術ラベル・データ・タイムスタンプ・ID** 専用。これにより "技術的な信頼性" を視覚的に与える。

### 3.3 font-family 指定

```css
/* メイン（欧文優先の和欧混植） */
font-family: Inter, "Noto Sans JP", sans-serif;

/* モノスペース（テクニカルラベル、データ表示、ID、タイムスタンプ） */
font-family: "IBM Plex Mono", monospace;

/* 数字（データテーブル等）— Mono と同じだが tabular-nums 必須 */
font-family: "IBM Plex Mono", monospace;
font-variant-numeric: tabular-nums;
```

### 3.4 文字サイズ・ウェイト階層

| Role | Font | Size | Weight | Line Height | Letter Spacing | 備考 |
|---|---|---|---|---|---|---|
| Hero Number | IBM Plex Mono | 96–128px | 500 | 1.0 | -0.04em | Confusion Score 等のヒーロー数字 |
| Hero H1 | Inter, Noto Sans JP | 36px | 600 | 1.2 | -0.01em | ページ見出し |
| Section H2 | Inter, Noto Sans JP | 28px | 600 | 1.25 | -0.005em | セクション見出し |
| Card Title | Inter, Noto Sans JP | 18px | 600 | 1.3 | -0.005em | カード見出し |
| Body | Inter, Noto Sans JP | 15px | 400 | 1.7 | normal | 本文（#1a1a1a） |
| Body small | Inter, Noto Sans JP | 13px | 400 | 1.5 | -0.005em | 補足本文（#707070） |
| Nav | Inter, Noto Sans JP | 14px | 500 | 1.0 | -0.28px | ナビゲーション |
| CTA Label | Inter | 13px | 500 | 1.2 | -0.26px | ボタン文字 |
| Mono Label | IBM Plex Mono | 11–12px | 500 | 1.2 | -0.36px | 技術ラベル、ステータス |
| Mono Tag | IBM Plex Mono | 11px | 500 | 1.2 | -0.44px | タグ・バッジ |
| Mono Data | IBM Plex Mono | 13–15px | 400 | 1.5 | normal | データテーブルの中身 |
| Tabular Number | IBM Plex Mono | varies | 500 | 1.0 | tabular-nums | データ表示の数字 |

### 3.5 行間・字間

- **本文の行間**: 1.7（日本語として適切な行間）
- **見出しの行間**: 1.2–1.3
- **小さなテキスト（11–14px）**: 負の letter-spacing（-0.26 〜 -0.48px、Apple 的に詰める）
- **Mono ラベル**: 負の letter-spacing で詰め、密度を上げる
- **見出し**: weight 600 で存在感を出す（700 = bold は使わない）

### 3.6 大文字／小文字ルール

- **本文・見出し**: sentence case のみ（Title Case 禁止）
- **Mono ラベル**: ALL CAPS 許可（例: `LIVE`, `RUN #248`, `STUCK`）
  - これは STUDIO の "FOR BUSINESS" と同じ "技術ラベルだけは例外" ルール
  - Mono フォント＋負の letter-spacing と組み合わせることでバランスを取る
- **Mono タイムスタンプ**: 全て数字＋区切り記号（例: `00:14:32`、`2026-06-27`）

### 3.7 OpenType 機能

```css
/* palt は使用しない */
font-feature-settings: normal;

/* 数字は等幅で揃える */
font-variant-numeric: tabular-nums;
```

### 3.8 縦書き

該当なし。

### 3.9 禁則処理・改行ルール

```css
word-break: break-all;
overflow-wrap: break-word;
line-break: strict;
```

- 句読点（、 。）が行頭にこないようにする（行頭禁則）
- 開きカッコ（「 (）が行末にこない、閉じカッコ（」 )）が行頭にこない
- `line-break: strict` でブラウザの厳格な禁則処理を有効化
- 英単語の途中改行は許容するが、UI ラベルでは `white-space: nowrap` で短く保つ

### 3.10 和欧混植（JP/EN mixing）

- `font-family: Inter, "Noto Sans JP", sans-serif` の指定順により、欧文は Inter、和文は Noto Sans JP が自動的に分担描画される
- **和文と欧文の境目には半角スペースを1つ入れる**
  - 良い: `田中健 42 years old`、`P-001 田中健`、`Confusion Score 42 です`
  - 悪い: `田中健42yearsold`、`P-001田中健`
- ASCII の括弧・引用符（`()` `""`）は欧文表記に、日本語の `「」` `（）` は和文表記に使う
- 表記揺れを避けるため UI 全体でルールを統一すること

### 3.11 句読点・記号

| 用途 | 使う | 使わない |
|---|---|---|
| 文末 | 。 | . |
| 文中区切り | 、 | , |
| 引用・内的発言 | 「...」 | "..." |
| 三点リーダ | …… (2文字繰り返し) または … (U+2026) | ... (中黒3つ) |
| 長音 | ー (U+30FC) | - (ハイフン) |
| 中黒・並列 | ・ | - |
| 区切り | / または ・ | \| (基本的に使わない) |

### 3.12 数字・単位・日付

- **数字**: 常に Arabic（半角）。漢数字は固有名詞のみ使用可
- **桁区切り**: `1,000`（3桁ごとカンマ）
- **パーセント**: `42%`（数字と % の間にスペースなし、いずれも半角）
- **時間（経過・タイムスタンプ）**: 24時間表記、コロン区切り、IBM Plex Mono で `00:14:32`
- **日付（技術系・ID）**: ISO 形式 `2026-06-27` (Mono)
- **日付（ユーザー向け本文）**: `2026年6月27日` または短縮 `6/27 (土)`
- **単位**: 半角数字＋全角単位、`5名`、`38秒`、`24体`、`4分12秒`
- **通貨**: 本文では `100円`、データ表示では `¥100`
- **西暦のみ使用、和暦は使わない**

### 3.13 Mono フォントと日本語

IBM Plex Mono は **欧文・数字・記号のみ** を含み、日本語グリフを持たない。日本語混在ラベルでは Noto Sans JP にフォールバックして等幅性が崩れる。

そのため：

- **Mono ラベルは原則として欧文・数字・記号のみで構成する**
  - 良い: `LIVE`, `P-001`, `RUN #248`, `00:14:32`, `42 / 100`, `STUCK`, `DONE`
  - 悪い: `LIVE 検証中`（和欧混在で等幅崩れ＋スタイル不統一）
- 日本語ラベルが必要な箇所では Noto Sans JP weight 500、letter-spacing 0 で表記する
- 例外: **ペルソナ ID + 日本語名の併記は許容**。半角スペース区切りで `P-001 田中健` のように書く
- 数字を Mono で表示する場合は `font-variant-numeric: tabular-nums` を併用し桁を揃える

### 3.14 Sentence Case と日本語

英語の sentence case は日本語に直接適用できないため、以下のルールで運用：

- 日本語見出し: 通常の表記（漢字・かな・カナの自然な使い分け）。冒頭を含め大文字変換は不要
- 本文の調子: 「です・ます調」を採用、「だ・である調」は避ける
- 体言止めは見出しのみで許容、本文では避ける
- 英語混在の見出しは、英語部分のみ sentence case を厳守
  - 良い: `Confusion score を可視化する`
  - 悪い: `Confusion Score を可視化する`（"Score" は Title Case 違反）

---

## 4. Component Stylings

### Buttons

**Primary CTA（ピル型・標準）**

- Background: `#1a1a1a`
- Text: `#ffffff`
- Padding: 12px 28px
- Border Radius: 500px（完全なピル型）
- Font: Inter, 13px, weight 500
- Letter Spacing: -0.26px

**Primary CTA Alert（警告用ピル型）**

- Background: `#ff4d2c`
- Text: `#ffffff`
- 他は Primary CTA と同じ
- 用途: 「警告を確認」「テストを停止」など

**Secondary / Outline**

- Background: `transparent`
- Text: `#1a1a1a`
- Border: 1px solid `#1a1a1a`
- Border Radius: 6px（控えめな角丸、ピル型ではない）

**Toggle / Tab（実況 ON/OFF、状態切替など）**

- Inactive: text `#707070`, no background, padding 6px 14px
- Active: bg `#1a1a1a`, text `#ffffff`, radius 500px
- Transition: 200ms ease-out

**リプレイボタン（Static フェーズ左パネル）**

- スタイル: Secondary / Outline（bg: transparent, border: 1px solid #e8e8e8, radius: 500px）
- ラベル: 「↺ リプレイ」
- ホバー: border-color → `#d4d4d4`

> **ボタン radius の使い分け**: CTA はピル型（500px）、補助ボタンは控えめな角丸（6px）。STUDIO と同じ思想。

### Cards

- Background: `#ffffff`
- Border: 1px solid `#e8e8e8`
- Border Radius: 12px
- Padding: 20–28px
- Hover: border color shifts to `#d4d4d4`（200ms）
- 影は使わない（フラット基調）

### Alert Cards（Critical 表示）

- Background: `#fff5f2` (Phantom Mist)
- Border: 1px solid `#ff4d2c`
- 他 Card と同じ

### Tags / Mono Labels

- Background: transparent または `#f7f7f7`
- Text: IBM Plex Mono 11px weight 500
- Letter Spacing: -0.44px
- Color: `#707070` (default) / `#1a1a1a` (emphasized) / `#ff4d2c` (alert)
- Padding: 4px 8px
- Border Radius: 4px
- 用途例: `LIVE`, `STUCK`, `DONE`, `RUN #248`, `P-001`, `00:14:32`, `PERSONA`, `INSIGHT`

### Persona Avatar

- Size: 32–40px circle
- Background: `#f7f7f7`
- Border: 1px solid `#e8e8e8`
- Text: Inter 14px weight 500、頭文字または漢字1文字、中央寄せ
- **States**:
  - `idle`: 標準（border: 1px solid `#e8e8e8`）
  - `active`: border: 1.5px solid `#3fb069`、pulse アニメ（2.2s loop、緑 rgba）
  - `stuck`: border: 1px solid `#ff4d2c`、内側にもう1pxの破線（"glitch ring"）
  - `done`: border: 1px solid `#1a1a1a`（完了 = 黒。緑は LIVE/アクティブ専用）
  - `ghost`: border: 1px dashed `#a8a8a8`（無効・休止状態）

> **LIVE = 緑、DONE = 黒の原則**: LIVE 表示に緑（`#3fb069`）を使うため、アバター状態でも LIVE/アクティブは緑ボーダー、完了は黒ボーダーで統一する。

### Input Fields

- Background: `#ffffff`
- Border: 1px solid `#e8e8e8`
- Border Radius: 6px
- Padding: 10px 14px
- Font: Inter 14px weight 400
- Focus: border becomes `#1a1a1a`（影は出さない）

### Progress Bar

- Track: bg `#f7f7f7`, height 4px, radius 2px
- Fill: bg `#1a1a1a` (default) / `#ff4d2c` (alert)
- 数値表示は IBM Plex Mono、横に併置

### Modal

- Background: `#ffffff`
- Border: 1px solid `#e8e8e8`
- Border Radius: 16px
- Padding: 32px
- Backdrop: `rgba(26, 26, 26, 0.4)`
- 唯一影が許される箇所: `0 8px 32px rgba(0, 0, 0, 0.08)`

---

## 5. Layout Principles

### Spacing Scale

| Token | Value | 用途 |
|---|---|---|
| XS | 4px | アイコン内の隙間 |
| S | 8px | テキスト内の小さい区切り |
| M | 16px | カード内の標準 padding 単位 |
| L | 24px | カード間、セクション内 |
| XL | 48px | セクション間 |
| XXL | 80px | ページ大区切り |

### Container

- **Dashboard**: max-width 1440px、side padding 24px
- **LP**: max-width 1200px、side padding 32px
- **Modal**: max-width 600px、center

### Grid — Dashboard（核となる構造）

3カラムグリッドを基本構造とする：

- **Left**: ペルソナ群一覧 / フィルタ / 入力（width 280–320px）
- **Center**: メインビュー — Dynamic 時は swarm 可視化、Static 時は Confusion Score ヒーロー（flex 1）
- **Right**: 思考ログ / インサイト / ペルソナ詳細（width 320–380px）

Dynamic と Static で **同じ 3カラム構造を維持**、内容と動きだけが入れ替わる。これが Scan & Override の前提。

### Grid — LP

セクションごとにフルワイド背景＋中央寄せコンテンツ。STUDIO と同じ構成。

### Density Principle

- 1画面につき "重要な情報塊" は 7–9 個以内
- 余白は要素サイズの 1/2 〜 2 倍を確保

---

## 6. Depth & Elevation

| Level | Shadow | 用途 |
|---|---|---|
| 0 | none | デフォルト。すべてのカード、ボタン |
| 1 | `border #d4d4d4` | Card hover（影ではなくボーダー変化で表現） |
| 2 | `0 8px 32px rgba(0,0,0,0.08)` | Modal のみ。それ以外で影は使わない |

> **基本思想**: フラット。深さは色とボーダーで表現する。

---

## 7. Motion Principles

### Core Principle

動きは「**呼吸**」であり「**演出**」。すべての動きには意味がある。

- **Breathing**: ライブ・アクティブ状態を示す穏やかなループ
- **Reveal**: データの登場を強調する一度きりのアニメ
- **Transition**: 状態変化を示す短い動き
- **Override**: Scan & Override のような "セッションに1度" の演出

### Animation Roles

| 役割 | Duration | Easing | 用途 |
|---|---|---|---|
| UI transition | 200ms | ease-out | ボタンホバー、フォーカス、トグル切替 |
| Reveal | 800–1200ms | ease-out | 数字登場、カード fade-in |
| Line draw | 1500–2000ms | ease-out | チャート・アーク描画（stroke-dashoffset） |
| Pulse (breath) | 2200ms | ease-in-out infinite | Live ドット、active アバター |
| Float | 4000–5000ms | ease-in-out infinite | ペルソナアバターの浮遊 |
| Orbit | 30000–45000ms | linear infinite | 背景の超低速回転（任意） |
| Scan (override) | 600–800ms | ease-out | Dynamic → Static 切替の核心演出 |

### Scan & Override（シグネチャー演出）

```
Phase 0: Dynamic UI 表示中
Phase 1: 0ms — 画面上端から 1px の Phantom Coral (#ff4d2c) の水平ラインが現れる
Phase 2: 0–600ms — スキャンラインが上→下に ease-out で走る
Phase 3: スキャンラインの背後で Dynamic UI の opacity が 0 に
Phase 4: 同時に Static UI が opacity 0 → 1 で重ねて出現
Phase 5: 600ms — スキャンライン消失、Static UI 完全表示
Total: 約 800ms
```

- 1セッションに1度しか発火しない
- 音は鳴らさない（無音演出）
- スキャンライン自体に光やグローは付けない（1px の細線のみ）

### Forbidden（禁止事項）

- グラデーション（あらゆる箇所で禁止）
- グロー、ネオン、ぼかし（box-shadow による光彩、filter: blur など）
- ストロボ、点滅
- 同一画面で 4 種類以上のアニメーションを同時に走らせる
- 中央寄せ以外でのテキスト揺れ・回転

### Glitch の再解釈

ピッチに登場する「波打つような赤いグリッチ（ノイズ）エフェクト」は、**品のあるグリッチ** として実装する：

- 1px dashed border in Phantom Coral
- stroke-dashoffset を 2–3 秒でゆっくり動かして "縞が流れる" ように
- transform / opacity の高速変化や randomize は使わない

---

## 8. Signature Components（GhostUsers 特有）

### 8.1 Persona Swarm（ペルソナ群）

- Dynamic フェーズの中央ビューに表示される
- 8–24 個の小さな円形アバター（24–32px）が緩やかに浮遊
- 浮遊は等速ではなく、各アバター毎に float-y アニメ（duration 4–5s、delay にばらつき）
- 重ならないよう grid または radial で配置、軌道は不規則だが整っている
- 状態別の outline 表現は §4 Persona Avatar の States を参照

### 8.2 Confusion Score Display

- IBM Plex Mono, 96–128px, weight 500
- 数字本体は `#1a1a1a`、末尾の `.` のみ Phantom Coral `#ff4d2c`
- 直下に Mono ラベルで `CONFUSION SCORE` (11px, letter-spacing -0.44px)
- 直下に前回比デルタを Mono small で（例: `−8 vs run #247`、色は `#3fb069` または `#ff4d2c`）
- 登場時は num-reveal アニメ（1.1s ease-out）

### 8.3 Persona Council View

- 横長カード列に各ペルソナのアバター＋発言を吹き出しで配置
- アバターと発言の間に細い線
- 属性間でギャップがあるとき、Phantom Coral のハイライトでアクセント
- 発言は body small (13px) で短く

### 8.4 Frustration Heatmap

- アプリのスクリーンショットの上に半透明のヒートマップを重ねる
- 色は Phantom Coral の透明度バリエーション（`rgba(255, 77, 44, 0.1〜0.6)`）
- 静的画像で OK、点滅させない

### 8.5 離脱の墓場 / Graveyard

- ペルソナが諦めた瞬間のスクリーンショットをグリッド表示
- 各セルは Card と同じスタイル、上端に Mono Tag で `STUCK 00:38` のように時刻
- アバター＋一言コメント（"これ買うんでしたっけ"）を併記

### 8.6 Mono ラベル運用例

| ラベル | 用途 | 色 |
|---|---|---|
| `LIVE` | アクティブな実行中状態 | `#3fb069` |
| `STUCK` | ペルソナが詰まっている | `#ff4d2c` |
| `DONE` | 完了 | `#1a1a1a` |
| `RUN #248` | 実行ID | `#707070` |
| `P-001` | ペルソナID | `#707070` |
| `00:14:32` | 経過時間 | `#1a1a1a` |
| `42 / 100` | スコア表示 | `#1a1a1a` |
| `PERSONA` | セクションラベル | `#707070` |
| `INSIGHT` | インサイト枠ラベル | `#707070` |

### 8.7 Setup Wizard（検証開始前の設定フロー）

検証開始前の **3ステップ設定フロー**。

**Step 01 — ターゲット**
- 検証対象の切り替え: **URL 入力** / **画像アップロード** のトグル
  - URL モード: テキスト入力
  - 画像モード: ドラッグ＆ドロップまたはクリックで PNG / JPG / WebP を複数枚アップロード可能（モックアップ・複数画面遷移・A/B テスト画像に対応）
- デバイス選択: モバイル / タブレット / デスクトップ
- 検証目的: UX 改善 / 離脱分析 / A/B テスト / ユーザビリティテスト
  - A/B テスト選択時: Pattern A / Pattern B の 2 枚をアップロードを推奨

**Step 02 — ペルソナ**
- 「ペルソナを生成 AI に提案してもらう →」ボタンでターゲット記述 → AI 提案
- AI 提案後は即カスタマイズ展開状態
- カスタマイズ項目:
  - **ペルソナ数**: 8 / 12 / 16 / 24 体から選択
  - **年齢層**: 20代 / 30代 / 40代 / 50代 / 60代以上（複数選択可）
  - **性別**: 男性多め / バランス / 女性多め
  - **IT リテラシー**: 低 / 中 / 高
  - **興味関心**: タグから複数選択。選択済みタグは × で削除可。カスタムタグ追加可
  - **重視軸（対象ユーザーの優先軸）**: タグから複数選択。選択済みタグは × で削除可。カスタムタグ追加可
  - **テキスト自由指示**: AIへの追加指示をチャット形式で記述
- 「ペルソナを更新」ボタン: クリック後 1.6秒ローディング（3点ドット）→ 反映
- 左サイドバー: ペルソナ生成完了後に縦リスト形式でアバター + ID + 属性を表示

**Step 03 — タスク & 確認**
- ジャーニープレビュー（タスク入力の上に表示）:
  - 通常フロー: 画面遷移ノード図（全ノード uniform スタイル、赤枠・要注意ラベルなし）
  - A/B テスト: Pattern A / Pattern B の比較レイアウト（アップロード画像サムネイル）
- タスク指示テキスト入力
- **KPI 目標**: タスク完了率の目標値（デフォルト 80%）を入力。Static フェーズの達成度計算に使用
- 検証サマリー（デバイス・目的・ペルソナ数・年齢・性別・リテラシー・KPI など）
- 「検証を開始」ボタン → Dynamic フェーズへ遷移

---

### 8.8 Live Journey Map

Dynamic フェーズ中央カラムに表示するリアルタイム画面遷移フロー。

**タスクヘッダー（マップ上部）**
- タスク指示テキスト + ● Live ドット
- アクティブ数（緑）/ 停滞中（Coral）/ 完了（黒）の 3 統計

**マップ本体**
- 横並びノード（各画面のワイヤーフレームサムネイル + ラベル）を矢印で接続
- ノード下にペルソナアバター（最大 3 体 + `+N` バッジ）
- 停滞箇所は破線 Coral カラーの吹き出し（例: 「3体がラッピング設定を編集中」）
- ノードをクリックすると選択ハイライト（`border: 1px solid #1a1a1a`）
- **停滞ノードのカード自体はニュートラル色**（ボーダー・ラベルは赤くしない）
- 完了ノードのアイコン: グレー（`#c8c8c8`）の小さなチェックマーク

**AI ANALYST ストリーム（マップカード内下部）**
- ヘッダー: ● ライブドット + `AI ANALYST — 客観分析エージェント`（IBM Plex Mono）
- ペルソナの主観ログと区別した **客観分析エージェント** の思考が時系列で流れる
- 3.2 秒ごとに新しい観察が追加（最大 5 件）
- 左ボーダー `#e8e8e8` で THOUGHT LOG と視覚的に差別化
- 時刻（Mono 9px）+ 分析テキスト（12px）の 2 カラム構成

---

### 8.9 Emotion Trend Chart

Dynamic フェーズ、ジャーニーマップ下の折れ線グラフ「リアルタイム・感情推移」。

- 4本の折れ線:
  - ポジティブ: `#3fb069`
  - ニュートラル: `#a8a8a8`
  - ネガティブ: `#f59b42`
  - 離脱に近い: `#ff4d2c`
- Y軸 0–100、X 軸は経過時間（IBM Plex Mono）
- SVG ベースで実装。グラデーション・グロー禁止

---

### 8.10 体験摩擦スコア（Confusion Score）

**定義**: 操作上の迷い・つまずき・離脱を 0〜100 でスコア化した指標。低いほど UX がスムーズ。

- 表示: IBM Plex Mono 96–128px weight 500、末尾 `.` のみ Phantom Coral
- KPI と比較して「達成 / 未達」を判定し、Static フェーズのヒーローに表示

---

### 8.11 Past Reports ビュー

左パネルのロゴ横アイコンをクリックすると表示。

- **テーブル構成**: RUN / URL / DATE / SCORE / DELTA / PERSONA の 6 列
- SCORE: 値の高低で色分け（高 → Coral、低 → 緑）
- 行をクリック → Static フェーズ（レポート）に遷移
- **A/B 比較機能**: チェックボックスで 2 件選択 → 「A/B 比較」ボタン → 比較詳細画面

---

### 8.12 Static フェーズ — レポートタブ構成

Static フェーズ右パネルは 4 タブで構成される:

| タブ | 内容 |
|---|---|
| SCORE | 体験摩擦スコアのヒーロー表示。KPI 達成度（目標達成度 %・達成 / 未達）、完了率・停滞率・平均滞在時間 |
| HEATMAP | アプリ画面へのヒートマップオーバーレイ |
| GRAVEYARD | ペルソナが離脱した瞬間のスクリーンショットグリッド |
| GROWTH | AI による改善提案。全施策後の予測スコアバナー + 改善カード（P1–P3: 改善名・期待スコア減・工数・推奨 Action・A/B Test 案） |

---

### 8.13 A/B 比較詳細画面

Past Reports で 2 件選択後に遷移する比較詳細画面。

**比較精度バッジ**
- URL・タスク・デバイス・ペルソナ条件が同じ: 「高精度比較」（緑）
- 条件が異なる: 「参考比較」（Coral）

**7セクション構成:**

| # | セクション | 内容 |
|---|---|---|
| ① | Run 情報ヒーロー | A/B の RUN#・体験摩擦スコア・前回比・URL・日付・ペルソナ数。優位側に「優位」ラベル |
| ② | 指標比較 | 体験摩擦スコア / 完了率 / 平均滞在時間 / 停滞人数 / 離脱に近い人数の差分 |
| ③ | ジャーニー差分マップ | 各ステップの到達率・停滞率をバーで比較。改善=緑、悪化=赤 |
| ④ | 課題分類カード | 解消 / 改善 / 継続 / 新規・悪化 の 4 分類 |
| ⑤ | ヒートマップ切り替え | PATTERN A / PATTERN B / 差分 の 3 モード。差分モード: 改善=緑、悪化=赤 |
| ⑥ | ペルソナ属性別変化 | 年齢層・IT リテラシー別のスコア差分と完了率変化 |
| ⑦ | AI 比較サマリー + 次の改善候補 3 件 | P1-P3 優先度・期待スコア減・工数付き |

---

## 9. Do's and Don'ts

### Do（推奨）

- 背景は `#ffffff`、テキストは `#1a1a1a`、アクセントは `#ff4d2c` の3色を骨格にする
- font-family は `Inter, "Noto Sans JP", sans-serif` の順（欧文優先）
- 見出しの weight は 600 を基本にする
- 小さいテキスト（11–14px）には負の letter-spacing を適用する
- CTA ボタンは radius: 500px のピル型にする
- 技術的なラベル・ID・タイムスタンプは IBM Plex Mono を使う
- Mono ラベルは ALL CAPS が許容される（例外ルール）
- 数字は tabular-nums で揃える
- ペルソナアバターの状態変化は outline で表現する
- アニメーションは「呼吸」を基本とし、ループは 2.2s〜5s で穏やかに
- 和文と欧文の間に半角スペースを1つ入れる（`田中健 42` / `P-001 田中健`）
- 文末は `。`、文中区切りは `、` を使う
- 数字は Arabic（半角）、24時間表記、ISO 日付 (Mono) で統一する
- Mono ラベルは欧文・数字・記号のみで構成する

### Don't（禁止）

- グラデーションを使う
- ドロップシャドウを Modal 以外で使う
- グロー、ネオン、ぼかし、blur を一切使わない
- font-weight 700 以上を使う（600 = semibold が上限）
- 純黒 `#000000` を使う（`#1a1a1a` を使用）
- 純白以外の背景色を本文エリアで使う（surface は `#f7f7f7` まで）
- アクセント色を本文テキストで使う（強調・CTA・アラート以外で使わない）
- 複数のアクセント色を混在させる（Phantom Coral 1色のみ）
- Title Case や ALL CAPS を本文・見出しで使う（Mono ラベルのみ ALL CAPS 許容）
- 塗りアイコンを使う（outline 1.5px のみ）
- 一度に 4 種類以上のアニメーションを同時に走らせる
- 文末・文中で `.` `,` を使う（必ず `。` `、`）
- Mono フォントの中に日本語を混ぜる（等幅性が崩れる）
- 漢数字を本文・データで使う（Arabic 半角数字を使用）
- 和暦を使う（西暦のみ）
- 「だ・である調」で本文を書く（「です・ます調」を採用）

---

## 10. Responsive Behavior

### Breakpoints

| Name | Width | 説明 |
|---|---|---|
| Mobile | ≤ 768px | 1カラム縦並び |
| Tablet | ≤ 1024px | 2カラム |
| Desktop | > 1024px | 3カラムダッシュボード |

### タッチターゲット

- 最小サイズ: 44px × 44px（WCAG 基準）

### モバイル時の縮小

- Hero number は 64–80px まで縮小
- 本文は 14–16px を維持
- 3カラム → 1カラム縦並び、Center → Left → Right の順に積む
- Persona Swarm はモバイルでは 6–8 体まで減らす

---

## 11. Agent Prompt Guide

### クイックリファレンス

```
Brand: GhostUsers
Tagline: AIペルソナ群でアプリを事前検証

Primary Accent: #ff4d2c (Phantom Coral)
Accent Surface: #fff5f2 (Phantom Mist)
Text Primary: #1a1a1a
Text Secondary: #707070
Text Tertiary: #a8a8a8
Background: #ffffff
Surface: #f7f7f7
Border: #e8e8e8
CTA Background: #1a1a1a
Success: #3fb069
Alert: #ff4d2c (= Primary Accent)

Font Sans: Inter, "Noto Sans JP", sans-serif
Font Mono: "IBM Plex Mono", monospace
Body Size: 15px
Body Line Height: 1.7
Heading Weight: 600 (max, do not use 700)
Letter Spacing Small: -0.26 to -0.48px

Button Radius (CTA): 500px (pill)
Button Radius (Secondary): 6px
Card Radius: 12px
Modal Radius: 16px

Motion: 呼吸のような穏やかなアニメーションのみ
Forbidden: gradient, glow, neon, blur, font-weight 700+
Phase: Dynamic（実行中、群れが動く） / Static（結果、ほぼ静止）
Signature Animation: Scan & Override（800ms、Dynamic → Static の切替）
```

### プロンプト例

```
GhostUsers のデザインシステムに従って、ダッシュボードの結果画面（Static）を作成してください。
- 背景: #ffffff
- 3カラム構造（左: ペルソナリスト 300px / 中央: Confusion Score ヒーロー / 右: Top Issues）
- ヒーロー数字: IBM Plex Mono 112px weight 500、末尾 "." のみ #ff4d2c
- 数字下に Mono ラベル "CONFUSION SCORE" 11px letter-spacing -0.44px color #707070
- ペルソナアバター: 36px 円形、bg #f7f7f7, border 1px #e8e8e8、stuck 状態は border 1px #ff4d2c
- CTA: ピル型 radius 500px bg #1a1a1a text #ffffff
- カード: bg #ffffff border 1px #e8e8e8 radius 12px
- 影は使わない、フラット
- 動き: Live ドットのパルス（2.2s）、数字 reveal（1.1s）のみ
```

### 特記事項

- **IBM Plex Mono の使い分け**: `LIVE`, `RUN #248`, `STUCK`, `P-001`, `00:14:32`, タグ・バッジ・ID・タイムスタンプ・スコアラベル。本文や見出しには使わない
- **Phantom Coral の使い分け**: CTA Alert / 高 Confusion / Critical issue / Scan ライン / Stuck 状態 outline / 警告タグの背景。本文テキスト・通常 CTA・通常ボーダーには使わない
- **アニメーションは "1画面同時 3 種類まで" の原則**: それ以上は混雑する
- **Scan & Override** は 1セッションに 1度のみ。多用すると陳腐化する
- **モリサワや有料フォントは使わない**: Google Fonts のみで完結させる
- **日本語特有のルール**: 和欧混植は半角スペース区切り、Mono ラベルは欧文のみで構成、句読点は `。` `、`、24時間表記と ISO 日付、和暦は使わない、本文は「です・ます調」。詳細は §3.9〜3.14 参照

---

## 12. デザイン参照

- **STUDIO** ([studio.design](https://studio.design/ja)): 全体のクリーンさ、ピル CTA、Mono ラベルの運用思想
- **Bloomberg Graphics** / **The Pudding**: データジャーナリズム的な編集力
- **Linear** ([linear.app](https://linear.app)): ダッシュボードのフラット感、Mono ラベル使い

---

## 13. 改訂履歴

- 2026-06-27: 初版作成（GhostUsers v1）
- 2026-06-28: v1.1 — ペルソナアバターカラールール更新・§8.7〜§8.9 追加
- 2026-06-28: v1.2 — Setup Wizard 拡張（画像アップロード・A/B テスト目的・ペルソナ詳細設定）
- 2026-06-28: v1.3 — Past Reports A/B 比較詳細画面（§8.13 追加）
- 2026-06-28: v1.4 — AI Analyst ストリーム（§8.8 更新）・KPI 目標入力・各種 UX 改善

