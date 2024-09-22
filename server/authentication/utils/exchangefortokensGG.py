import requests
from datetime       import datetime, timezone, timedelta
from django.conf    import settings

def ExchangeForTokensGG(code):
    client_id = settings['GOOGLE_CLIENT_ID']
    client_secret = settings['GOOGLE_CLIENT_SECRET']
    redirect_uri = 'https://www.aennaki.me/api/oauth/google/callback/'
    url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    response = requests.post(url, data=data)
    tokens = response.json()
    if 'expires_in' in tokens:
        expiration_time = datetime.now(timezone.utc) + timedelta(seconds=tokens['expires_in'])
        if datetime.now(timezone.utc) > expiration_time:
            data = {
                'refresh_token': tokens.get('refresh_token'),
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'refresh_token'
            }
            response = requests.post(url, data=data)
            tokens = response.json()
    token = tokens['access_token']
    return token