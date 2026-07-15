# かよちん天気画像 LINE 自動送信

毎朝 5:15（日本時間）にローカルのCodex自動実行で西東京市の天気を取得し、テンプレ画像を参照して服装画像を生成します。天気情報を合成し、GitHubの公開URLを経由してLINEへ送ります。

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

毎朝のCodex画像生成では `python outfit_prompt.py` の結果と基準画像を画像生成へ渡し、生成画像を `weather_card.py --outfit <画像パス>` に渡します。

## かよちんの見た目を固定する

基準画像を次の場所へ保存します。

`assets/reference/kayochin_reference.png`

この画像はGitの対象外なので、公開リポジトリへは送られません。画像生成時は基準画像を `referenced_image_paths` の入力画像として実際に添付し、顔立ち・髪型・髪色・目の色を維持して、服装・持ち物・背景だけを変更します。基準画像がない場合、画像生成用プロンプト作成はエラーで停止します。詳しくは [`assets/reference/README.md`](assets/reference/README.md) を参照してください。

## 費用

- 天気: Open-Meteo（個人・非商用、APIキー不要）
- 定時実行: Codexのローカル自動実行（画像生成枠を使用）
- 画像公開: GitHub / `raw.githubusercontent.com`
- LINE: LINE公式アカウントのコミュニケーションプラン（月200通まで0円）

1人へ1日1回なら、通常は月28〜31通です。

## 初回設定

1. `assets/outfits/` に服装画像を追加します。命名規則は同フォルダの README を参照してください。
2. このフォルダの公開可能なファイルを、公開GitHubリポジトリへ置きます。基準画像と秘密情報はアップロードしません。
3. LINE公式アカウントを作り、Official Account Managerで Messaging API を有効にします。
4. その公式アカウントを、自分のLINEで友だち追加します。
5. LINE Developersのチャネルからチャネルアクセストークンを発行します。
6. `setup_line_secrets.ps1` を実行し、アクセストークンとユーザーIDをWindowsユーザー専用に暗号化保存します。
7. Codexの毎朝5:15自動実行を有効にします。

アクセストークンはファイルに直接書かないでください。

## 手元で画像だけ試す

```powershell
python -m pip install -r requirements.txt
python weather_card.py
```

生成画像は `public/YYYY-MM-DD.png` に保存されます。服装画像がまだない場合は、案内入りの仮画像になります。

## 補足

- ローカル自動実行には、このWindows環境とCodexが利用できる状態である必要があります。
- LINEの画像メッセージ仕様上、画像はLINE側が取得できるHTTPS URLに置く必要があります。
- 公開リポジトリを使うため、服装画像と生成画像はURLを知っている人から閲覧可能です。
- 過去画像を残したくない場合は、定期削除処理を追加できます。
