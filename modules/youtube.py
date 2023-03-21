import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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
  params['fields'] = 'items(id,snippet(title,resourceId(channelId)))'

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


def insert_playlistitem(youtube, **params):
  
  params['part'] = 'snippet'
  params['fields'] = 'id,snippet(position)'
  return youtube.playlistItems().insert(**params).execute()


def clear_playlistitem(youtube, playlist_id):
  items = list_playlistitems(youtube, playlistId=playlist_id)
  for item in items:
    youtube.playlistItems().delete(
          id=item['id']
    ).execute()
