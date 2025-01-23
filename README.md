# nijisanji-stream-playlist-creator

- にじさんじの配信情報から、特に自分好みの配信だけを抜き出してプレイリスト化するスクリプトです。
- 特に雑談などのラジオ系配信、かつメン限などを除いたものを中心に、登録済みチャンネル、配信中のものを先頭でピックアップします。

## 事前準備

- YouTube APIを用いるため、事前にGoogle Cloud Consoleでプロジェクトを作る。
  - [YouTube Data API の概要  |  Google for Developers](https://developers.google.com/youtube/v3/getting-started?hl=ja)
- プレイリストの編集を行うため、OAuth2.0 クライアントIDで認証情報を作成する。
  - [OAuth ウェブ クライアント ID を作成する - Google Workspace Migrate](https://support.google.com/workspacemigrate/answer/9222992?hl=JA)
  - リダイレクト先は `http://localhost:8000/` とする。
  - 作ったアプリは本番環境まで公開しておく。Googleの審査までやる必要はない。
  - 作った認証情報のページから、client_secret json ファイルをダウンロードしておく。

## Usage

```sh
# clone
git clone https://github.com/legnoh/nijisanji-stream-playlist-creator.git
cd nijisanji-stream-playlist-creator

# copy client_secret file into project
cp ~/Downloads/client_secret.....json ./

# create venv
uv sync --dev

# set .env
cp .env.example .env
code .env

# create token.json
uv run get_token.py

# run
uv run main.py
```

## 備考

- 7日おきにトークンが切れるので、下記からアプリを消して再度承認しなおす
  - https://myaccount.google.com/permissions
  - `uv run get_token.py`

## Disclaim / 免責事項

- 当スクリプトは、にじさんじ、ANY COLOR株式会社からは非公認のものです。
  - これらを利用したことによるいかなる損害についても当方では責任を負いかねます。
- 当スクリプトはこれらのサイトに対し、負荷をかけることを目的として制作したものではありません。
  - 利用の際は常識的な範囲でのアクセス頻度に抑えてください。
  - 先方に迷惑をかけない範囲での利用を強く推奨します。
