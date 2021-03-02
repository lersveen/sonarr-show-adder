import json
import requests

imdb_id = '123'
api_key = '123'
sonarr_host = 'localhost'


def send_to_sonarr():
    payload = {
        'monitored': True,
        'imdbId': imdb_id,
        'title': 'The Jinx: The Life and Deaths of Robert Durst',
        'titleSlug': 'the-jinx-the-life-and-deaths-of-robert-durst',
        'seasonFolder': True,
        'qualityProfileId': '1',
        'rootFolderPath': '/home/TV Shows/',
        'seasons':
            [
                {
                    'monitored': True, 'seasonNumber': 1
                }
            ],
            'addOptions': {
                'searchForMissingEpisodes': True,
                'ignoreEpisodesWithFiles': False
                }
        }

    headers = {
        'User-Agent': "Show adder",
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
        }

    url = 'http://{SONARR_HOST}:8989/api/series/'
    try:
        r = requests.post(url=url, data=json.dumps(payload), headers=headers)

        r.raise_for_status()

        print('Succeeded posting')

        return r.json()

    except Exception:
        print('Failed posting')
        return None


result = send_to_sonarr()

print(result)
