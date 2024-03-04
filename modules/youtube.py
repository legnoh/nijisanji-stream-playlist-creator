from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import logging

class Yt:

  def __init__(self, creds:Credentials) -> None:
    self.client = build(
      serviceName='youtube',
      version='v3',
      credentials=creds,
      num_retries=3
    )

  def get_channels(self, **params):

    channels = []
    params['pageToken'] = ''
    params['maxResults'] = 50
    params['part'] = 'id,snippet'
    params['fields'] = 'items(id,snippet(title,customUrl))'

    while params['pageToken'] is not None:
      channels_response = self.client.channels().list(**params).execute()
      for channel_item in channels_response['items']:
        channels.append(channel_item)
      params['pageToken'] = channels_response.get('nextPageToken', None)
    return channels


  def get_subscriptions(self, **params):

    channels = []
    params['pageToken'] = ''
    params['maxResults'] = 50
    params['part'] = 'id,snippet'
    # params['fields'] = 'items(id,snippet(title,resourceId(channelId)))'

    while params['pageToken'] is not None:
      subscriptions_response = self.client.subscriptions().list(**params).execute()
      for subscription_item in subscriptions_response['items']:
        channels.append(subscription_item)
      params['pageToken'] = subscriptions_response.get('nextPageToken', None)
    return channels


  def search_videos(self, **params):

    videos = []
    params['pageToken'] = ''
    params['maxResults'] = 50
    params['type'] = 'video'
    params['part'] = 'id,snippet'    
    params['fields'] = "items(id(videoId),snippet(publishedAt,channelId,title,channelTitle))" 

    while params['pageToken'] is not None:
      search_response = self.client.search().list(**params).execute()
      for search_item in search_response['items']:
        videos.append(search_item)
      params['pageToken'] = search_response.get('nextPageToken', None)
    return videos


  def list_playlistitems(self, **params):

    videos = []
    params['pageToken'] = ''
    params['maxResults'] = 50
    params['part'] = 'id'
    params['fields'] = "items(id)"

    while params['pageToken'] is not None:
      search_response = self.client.playlistItems().list(**params).execute()
      for search_item in search_response['items']:
        videos.append(search_item)
      params['pageToken'] = search_response.get('nextPageToken', None)
    return videos


  def insert_playlistitems(self, playlist_id:str, items):

    # batch = youtube.new_batch_http_request(callback=insert_exception)
    for i,v in enumerate(items):
      logging.info("【採用】[{d}] {t} / {a}".format(d=v['start_at'], t=v['title'], a=v['channel_name']))
      self.client.playlistItems().insert(
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



  def clear_playlistitem(self, playlist_id):

    logging.info("Remove all playlist items...")
    items = self.list_playlistitems(playlistId=playlist_id)
    for item in items:
      self.client.playlistItems().delete(id=item['id']).execute()
    logging.info("Removed all playlist items successfully.")

  # def insert_exception(self, request_id, response, exception):
  #   if exception is not None:
  #     logging.info("Error with insert playlist items: {e}: {rq}:{rs}".format(e=exception, rq=request_id, rs=response))
  #     pass
  #   else:
  #     logging.info("Inserted playlist items successfully: {rq}:{rs}".format(rq=request_id, rs=response))
  #     pass
