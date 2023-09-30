import os
import modules.youtube as yt
import modules.nijisanji as niji
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

token_file = './token.json'
playlist_id = os.environ.get('YOUTUBE_PLAYLIST_ID')
movie_lang = os.environ.get('MOVIE_LANGUAGE', None)
video_count = int(os.environ.get('VIDEO_COUNT', 5))

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

  subscriptions = yt.get_subscriptions(youtube, channelId=my_channel_id, )
  subscription_channels = []
  for channel in subscriptions:
    subscription_channels.append(channel['snippet']['title'])
  
  elected_videos = niji.get_streams(subscription_channels, lang=movie_lang)

  yt.clear_playlistitem(youtube, playlist_id)

  for i in range(0, video_count):

    v = elected_videos[i]
    print("【確定】[{d}] {title} / {author}".format(d=v['start_at'], title=v['title'], author=v['channel_name']))

    yt.insert_playlistitem(youtube, body={
      'snippet': {
        'playlistId': playlist_id,
        'resourceId': {
          'kind': 'youtube#video',
          'videoId': v['youtube_video_id']
        }
      }
    })

  print('--------------------')

  for i in range(video_count, video_count+10):
    v = elected_videos[i]
    print("【次点】[{d}] {title} / {author}".format(d=v['start_at'], title=v['title'], author=v['channel_name']))
