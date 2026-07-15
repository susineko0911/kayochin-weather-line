# かよちん天気画像 LINE 自動送信

毎朝 5:30（日本時間）に西東京市の天気を取得し、気温・雨に合う服装画像へ天気を合成して、LINEへ送ります。

## 服装ルールを変更する

服装・季節・イベントの設定は [`outfit_config.json`](outfit_config.json) にまとめています。

- `temperature_rules`: 最高気温ごとの基本服装
- `weather_modifiers`: 雨の傘、雪用の靴、強風時の表現
- `events`: 正月、クリスマスなど、日付で優先する服装と背景
- `seasons`: 春夏秋冬の色・素材の雰囲気

イベント服装が基本服装より優先され、その後に雨・雪・強風の小物が追加されます。例えば雨のクリスマスなら「クリスマスコーデ＋傘」になります。

現在の天気から画像生成用プロンプトを確認できます。

```powershell
python outfit_prompt.py
python outfit_prompt.py --plan-json
```

毎朝のCodex画像生成では `python outfit_prompt.py` の結果を画像生成指示として使い、生成画像を `weather_card.py --outfit <画像パス>` に渡します。

## かよちんの見た目を固定する

基準画像を次の場所へ保存します。

`assets/reference/kayochin_reference.png`

この画像はGitの対象外なので、公開リポジトリへは送られません。画像生成時は基準画像を参照し、顔立ち・髪型・髪色・目の色を維持して、服装・持ち物・背景だけを変更します。詳しくは [`assets/reference/README.md`](assets/reference/README.md) を参照してください。

## 費用

- 天気: Open-Meteo（個人・非商用、APIキー不要）
- 定時実行と画像公開: GitHub Actions / `raw.githubusercontent.com`
- LINE: LINE公式アカウントのコミュニケーションプラン（月200通まで0円）

1人へ1日1回なら、通常は月28〜31通です。

## 初回設定

1. `assets/outfits/` に服装画像を追加します。命名規則は同フォルダの README を参照してください。
2. このフォルダの中身を、新しい **公開GitHubリポジトリ** の直下へ置きます。
3. LINE公式アカウントを作り、Official Account Managerで Messaging API を有効にします。
4. その公式アカウントを、自分のLINEで友だち追加します。
5. LINE Developersのチャネルから長期のチャネルアクセストークンを発行します。
6. GitHubリポジトリの `Settings > Secrets and variables > Actions` に次を登録します。
   - `LINE_CHANNEL_ACCESS_TOKEN`: 手順5のトークン
   - `LINE_TO`: 送信先のLINEユーザーID（`U`から始まる値）
7. GitHubの `Actions` で「かよちん天気画像を送信」を開き、`Run workflow` で試します。

アクセストークンはファイルに直接書かないでください。

## 手元で画像だけ試す

```powershell
python -m pip install -r requirements.txt
python weather_card.py
```

生成画像は `public/YYYY-MM-DD.png` に保存されます。服装画像がまだない場合は、案内入りの仮画像になります。

## 補足

- GitHubの予約実行は混雑時に数分遅れる場合があります。
- LINEの画像メッセージ仕様上、画像はLINE側が取得できるHTTPS URLに置く必要があります。
- 公開リポジトリを使うため、服装画像と生成画像はURLを知っている人から閲覧可能です。
- 過去画像を残したくない場合は、定期削除処理を追加できます。
