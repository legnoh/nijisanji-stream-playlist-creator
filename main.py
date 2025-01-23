import os,logging,sys
import modules.nijisanji as niji
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from modules.youtube import Yt

token_file = './token.json'
playlist_id = os.environ['YOUTUBE_PLAYLIST_ID']
movie_lang = os.environ.get('MOVIE_LANGUAGE', None)
video_count = int(os.environ.get('VIDEO_COUNT', 5))

scopes = [
  'https://www.googleapis.com/auth/youtube',
  'https://www.googleapis.com/auth/youtube.readonly'
]

if __name__ == '__main__':

  log_format = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
  log_level = os.getenv("LOGLEVEL", logging.INFO)
  logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S%z', level=log_level)

  if os.path.exists(token_file):
    creds = Credentials.from_authorized_user_file(token_file, scopes)
  else:
    logging.error("token.json is not found. Please execute `uv run get_token.py` before this script!")
    sys.exit(1)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())

  yt = Yt(creds)
  my_channel    = yt.get_channels(mine=True)
  my_channel_id = my_channel[0]['id']

  subscriptions = yt.get_subscriptions(channelId=my_channel_id)
  subscription_channels = []
  for channel in subscriptions:
    subscription_channels.append(channel['snippet']['title'])

  elected_videos = niji.get_streams(subscription_channels, lang=movie_lang)

  if elected_videos == None:
    logging.error("failed to choise videos... exited")
    sys.exit(1)

  logging.info("# プレイリスト確定")
  yt.clear_playlistitem(playlist_id)
  yt.insert_playlistitems(playlist_id, elected_videos[0:video_count])

  logging.info("----")
  for v in elected_videos[video_count+1:len(elected_videos)]:
    logging.info(f"【ランク外】[{v['start_at']}] {v['title']} / {v['channel_name']}")
