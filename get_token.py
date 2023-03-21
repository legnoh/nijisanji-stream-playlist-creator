import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

client_secret_file = os.environ.get('YOUTUBE_CLIENT_SECRET_FILE', './client_secret.json')
token_file = os.environ.get('YOUTUBE_TOKEN_FILE', './token.json')
force_recreate = os.environ.get('FORCE_RECREATE', False)

scopes = [
  'https://www.googleapis.com/auth/youtube',
  'https://www.googleapis.com/auth/youtube.readonly'
]

if __name__ == '__main__':

  creds = None
  
  if os.path.exists(token_file):
    creds = Credentials.from_authorized_user_file(token_file, scopes)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token and not force_recreate:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
      creds = flow.run_local_server(port=8000)
    with open('token.json', 'w') as token:
      token.write(creds.to_json())
