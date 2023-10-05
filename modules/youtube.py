import requests
from selenium.webdriver.common.by import By
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium.common.exceptions import NoSuchElementException

def get_channels(youtube, **params):

  channels = []
  params['pageToken'] = ''
  params['maxResults'] = 50
  params['part'] = 'id,snippet'
  params['fields'] = 'items(id,snippet(title,customUrl))'

  while params['pageToken'] is not None:
    channels_response = youtube.channels().list(**params).execute()
    for channel_item in channels_response['items']:
      channels.append(channel_item)
    params['pageToken'] = channels_response.get('nextPageToken', None)
  return channels


def get_subscriptions(youtube, **params):

  channels = []
  params['pageToken'] = ''
  params['maxResults'] = 50
  params['part'] = 'id,snippet'
  # params['fields'] = 'items(id,snippet(title,resourceId(channelId)))'

  while params['pageToken'] is not None:
    subscriptions_response = youtube.subscriptions().list(**params).execute()
    for subscription_item in subscriptions_response['items']:
      channels.append(subscription_item)
    params['pageToken'] = subscriptions_response.get('nextPageToken', None)
  return channels


def search_videos(youtube, **params):

  videos = []
  params['pageToken'] = ''
  params['maxResults'] = 50
  params['type'] = 'video'
  params['part'] = 'id,snippet'    
  params['fields'] = "items(id(videoId),snippet(publishedAt,channelId,title,channelTitle))" 

  while params['pageToken'] is not None:
    search_response = youtube.search().list(**params).execute()
    for search_item in search_response['items']:
      videos.append(search_item)
    params['pageToken'] = search_response.get('nextPageToken', None)
  return videos


def list_playlistitems(youtube, **params):

  videos = []
  params['pageToken'] = ''
  params['maxResults'] = 50
  params['part'] = 'id'
  params['fields'] = "items(id)"

  while params['pageToken'] is not None:
    search_response = youtube.playlistItems().list(**params).execute()
    for search_item in search_response['items']:
      videos.append(search_item)
    params['pageToken'] = search_response.get('nextPageToken', None)
  return videos


def insert_playlistitems(youtube, playlist_id, items):

  # batch = youtube.new_batch_http_request(callback=insert_exception)
  for i,v in enumerate(items):
    print("【採用】[{d}] {t} / {a}".format(d=v['start_at'], t=v['title'], a=v['channel_name']))
    youtube.playlistItems().insert(
      part='snippet',
      fields='id,snippet(position)',
      body={
      'snippet': {
        'playlistId': playlist_id,
        'position': i,
        'resourceId': {
          'kind': 'youtube#video',
          'videoId': v['youtube_video_id']
        }
      }
    }
    ).execute()
  # batch.execute()



def clear_playlistitem(youtube, playlist_id):

  print("Remove all playlist items...")
  items = list_playlistitems(youtube, playlistId=playlist_id)
  for item in items:
    youtube.playlistItems().delete(id=item['id']).execute()
  print("Removed all playlist items successfully.")

def insert_exception(request_id, response, exception):
  if exception is not None:
    print("Error with insert playlist items: {e}: {rq}:{rs}".format(e=exception, rq=request_id, rs=response))
    pass
  else:
    print("Inserted playlist items successfully: {rq}:{rs}".format(rq=request_id, rs=response))
    pass

def is_members_only(driver, video_id) -> bool:
  try:
    driver.get("https://www.youtube.com/watch?v={v}".format(v=video_id))
    badges = driver.find_elements(By.CSS_SELECTOR, "div.badge-style-type-members-only")
    if len(badges) > 0:
      return True
    return False
  except NoSuchElementException as e:
    print("ERROR: {e} found, URL: {u}".format(e=e, u=driver.current_url))
    return False
