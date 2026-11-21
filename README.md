# enshu-lifehack-kosai

湖西ライフハック（遠州ライフハック 湖西市版）の **静的サイト** リポジトリ。
公開先：`https://kosai.enshu-lifehack.com/`（Cloudflare Workers Static Assets）

御前崎版から手動クローン・履歴を切って新設。横展開の設計原則は袋井版の指示書（`enshu-lifehack-fukuroi` リポジトリ `docs/fukuroi-lifehack-design-spec.md`）に準拠する。

## 構成

静的HTMLのみ。Cloudflare の **Build output directory = `/`**（ビルド不要）で配信する。

```
index.html              トップ（くらしの場面・目的から選ぶ）
data/city.json          市プロファイル（市名・公式窓口・CVフラグ等の差分を集約）
data/topics_master.json 中項目マスター台帳（磐田155項目が起点）
data/content/<category>.json 中項目ごとの執筆済みコンテンツ（qa/steps/tabs等）
life/<大項目>/           くらしの大項目ページ
life/<大項目>/<中項目>/   個別ページ
sitemap.xml             サイトマップ
robots.txt
_redirects              旧 /iwata/ 配下 → 直下への 301
404.html                カスタム404
favicon.svg
```

## 生成方法

本サイトは公式サイトのクロール・静的化ではなく、`data/topics_master.json` の中項目台帳をもとに、公式情報を1件ずつ調査した上でAIが執筆する「台帳駆動」の生成物である（掛川版・森町版と同じ方式）。

## 最新情報の更新

期限・休止・制度変更は `data/current-updates.json` に確認日、本文、公式出典、対象ページを記録します。既存本文の変更は `data/topics_master.json` と `data/content/` に反映してください。今回確認した案内の日付と、ページ全体の従来の確認日は区別しています。

既存のcanonical・回遊・共通部品・計測を保持した更新手順：

```sh
python scripts/refresh_current_information.py
node scripts/build-search-index.mjs
python scripts/build_sitemap.py
python scripts/inspect_all.py
node scripts/test-search.mjs
node scripts/check-synonyms.mjs
python scripts/check_official_links.py
```

公開前後に実ブラウザーでPC・狭幅表示、最新情報から詳細への導線、出典リンクを確認します。終了した期限案内は次回更新時に整理し、未確認の全ページへ一律に確認日を付け替えないでください。

## 免責事項

本サイトは湖西市公式サイトではありません。最新・正確な情報は湖西市公式サイトをご確認ください。
運営：富士ヶ丘サービス ／ 代表：大石浩之


## トップの写真館・富士ヶ丘サービス相談案内（2026-11-19）

`parts/community-links.html` がトップページの案内の原本です。`index.html` の `PART:community-links` マーカーへ同期してください。写真館は実在する市町だけに掲載し、他市町の館をその市町の写真館として表示しません。実家カルテと介護相談は市町別UTM・クリック計測付きです。行政案内・既存のガイド・各自治体公式へのリンクを保持してください。相談写真は運営会社の既存サイトに掲載された写真です。
