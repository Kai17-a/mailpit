# Mailpit + Discord Webhook

開発環境で送信されたメールを Mailpit で受信・保存し、新着メールの概要を Discord に通知するための Docker Compose 構成。

## 構成

- `mailpit`: SMTP サーバー、メール保存、Web UI の提供
- `webhook-handler`: 新着メールの件名、送信元、宛先、本文の抜粋を Discord Webhook に転送する FastAPI アプリケーション
- `mailpit-data`: 受信メールを保存する Docker ボリューム

## 接続先

- SMTP: `localhost:1025`
- Mailpit Web UI: `http://localhost:8025`
- Webhook ハンドラー: `http://webhook-handler:8080/mail`（Compose ネットワーク内）

## 必要な環境変数

- `DISCORD_WEBHOOK_URL`: Discord の通知先 Webhook URL
- `MP_WEBHOOK_URL`: Mailpit から Webhook ハンドラーへの通知先 URL
- `MAILPIT_PUBLIC_URL`: Discord 通知に表示する Mailpit Web UI の URL

## 図

- mailpit to webhook_server

  ```mermaid
  sequenceDiagram
      autonumber

      participant App as Vaultwarden / Outline
      participant Mailpit as Mailpit
      participant Handler as webhook-handler
      participant Discord as Discord Webhook

      App->>Mailpit: SMTPでメール送信
      Mailpit->>Mailpit: メールを保存

      Mailpit->>Handler: POST /mail<br/>メール概要のJSON
      Handler-->>Mailpit: 200 OK

      Handler->>Handler: 件名・送信元・本文などを整形

      Handler->>Discord: Webhook POST
      Discord-->>Handler: 204 No Content
  ```
