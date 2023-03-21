import os
import modules.youtube as yt
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

token_file = './token.json'
playlist_id = os.environ.get('YOUTUBE_PLAYLIST_ID')

scopes = [
  'https://www.googleapis.com/auth/youtube',
  'https://www.googleapis.com/auth/youtube.readonly'
]

if __name__ == '__main__':

  creds = None

  if os.path.exists(token_file):
    creds = Credentials.from_authorized_user_file(token_file, scopes)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())

  youtube = build(
    serviceName='youtube',
    version='v3',
    credentials=creds
  )

  my_channel = yt.get_channels(youtube, mine=True)
  my_channel_id = my_channel[0]['id']

  subscriptions = yt.get_subscriptions(youtube, channelId=my_channel_id)
  subscription_ids = []
  for channel in subscriptions:
    subscription_ids.append(channel['snippet']['resourceId']['channelId'])

  yt.clear_playlistitem(youtube, playlist_id)

  items = yt.search_videos(youtube,
    q="にじさんじ",
    eventType='live',
    # order='date',
  )

  new_items = []
  for item in items:
    if item['snippet']['channelId'] in subscription_ids:
      new_items.append(item)
  
  # 空の場合、デフォルト動画を入れる
  if len(new_items) == 0:
    new_items.append({
      "id": {"videoId": "6uddGul0oAc"},
      "snippet": {"publishedAt": "0000", "title": "default", "channelTitle": "default"},
    })
  else:
    # 日付が新しい順に並び替え
    new_items = sorted(new_items, key=lambda d: d['snippet']['publishedAt'], reverse=True)

  for new_item in new_items:
    print("{d} 開始: {title} 投稿者: {author}".format(d=new_item['snippet']['publishedAt'], title=new_item['snippet']['title'], author=new_item['snippet']['channelTitle']))
    
    body = {
      'snippet': {
        'playlistId': playlist_id,
        'resourceId': {
          'kind': 'youtube#video',
          'videoId': new_item['id']['videoId']
        }
      }
    }

    playlist = yt.insert_playlistitem(youtube, body=body)
