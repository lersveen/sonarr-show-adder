import sys
import json
import requests
import xmltodict

try:
    imdb_id = str(sys.argv[1])
    api_key = str(sys.argv[2])
except Exception:
    raise ValueError('Missing arguments – need both: <IMDB id> <Sonarr api key>')
    sys.exit()

sonarr_host = 'localhost:8989/sonarr'
user_agent = 'Sonarr-show-adder'
root_folder = '/home/lersveen/Bernt/Serier/'


def get_tvdb_id(imdb_id):
    url = f'https://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid={imdb_id}'

    try:
        r = requests.get(url=url)

        r.raise_for_status()

        print('Succeeded getting info from tvdb')

        response_dict = xmltodict.parse(r.content)

        return response_dict['Data']['Series'].get('seriesid')

    except Exception as e:
        print('Failed getting info from tvdb')
        print(e)
        return None


def lookup_series(tvdb_id):
    headers = {
        'User-Agent': user_agent,
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
        }

    url = f'http://{sonarr_host}/api/series/lookup?term=tvdb:{tvdb_id}'

    try:
        r = requests.get(url=url, headers=headers)

        r.raise_for_status()

        print('Succeeded looking up series')

        return r.json()
    except Exception as e:
        print('Failed looking up series')
        print(e)
        return None


def send_to_sonarr(series_info):
    payload = {
        'monitored': True,
        'tvdbId': series_info[0].get('tvdbId'),
        'title': series_info[0].get('title'),
        'profileId': series_info[0].get('profileId'),
        'titleSlug': series_info[0].get('titleSlug'),
        'seasonFolder': True,
        'seasons': series_info[0].get('seasons'),
        'images': series_info[0].get('images'),
        'qualityProfileId': '1',
        'rootFolderPath': root_folder,
        'addOptions': {
            'searchForMissingEpisodes': True,
            'ignoreEpisodesWithFiles': False
            }
        }

    headers = {
        'User-Agent': user_agent,
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
        }

    url = f'http://{sonarr_host}:8989/api/series'
    try:
        r = requests.post(url=url, data=json.dumps(payload), headers=headers)

        r.raise_for_status()

        print('Succeeded posting')

        return r.json()

    except Exception as e:
        print('Failed posting')
        print(e)
        return None


if __name__ == "__main__":
    tvdb_id = get_tvdb_id(imdb_id)
    series_info = lookup_series(tvdb_id)
    send_to_sonarr(series_info)
