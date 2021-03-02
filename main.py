import sys
import json
import csv
import requests
import xmltodict

try:
    imdb_list_id = str(sys.argv[1])
    api_key = str(sys.argv[2])
except Exception:
    raise ValueError('Missing arguments – need both: <IMDB list id> <Sonarr api key>')
    sys.exit()

sonarr_host = 'localhost:8989/sonarr'
user_agent = 'Sonarr-show-adder'
root_folder = '/home/lersveen/Bernt/Serier/'
quality_profile = 6


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
    data = {
        'monitored': True,
        'tvdbId': series_info[0].get('tvdbId'),
        'title': series_info[0].get('title'),
        'profileId': quality_profile,
        'titleSlug': series_info[0].get('titleSlug'),
        'seasonFolder': True,
        'seasons': series_info[0].get('seasons'),
        'images': series_info[0].get('images'),
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

    url = f'http://{sonarr_host}/api/series'
    try:
        r = requests.post(url=url, data=json.dumps(data), headers=headers)

        r.raise_for_status()

        print('Succeeded posting to Sonarr')

        return r.json()

    except Exception as e:
        print('Failed posting to Sonarr')
        print(e)
        return None


def get_imdb_list(imdb_list_id):
    data = []

    headers = {'Content-Type': 'text/csv'}
    url = f'https://www.imdb.com/list/{imdb_list_id}/export'

    try:
        with requests.get(url, headers=headers, stream=True) as r:
            lines = (line for line in r.iter_lines(decode_unicode=True))
            for row in csv.DictReader(lines):
                data.append(row)

        r.raise_for_status()

        print('Succeeded getting list from IMDB')

        return data
    except Exception as e:
        print('Failed getting list from IMDB')
        print(e)
        return None


def filter_imdb_list(imdb_list, field, filter_value):
    filtered_list = []
    for item in imdb_list:
        if item.get(field) == filter_value:
            filtered_list.append(item)
    return filtered_list


if __name__ == "__main__":
    imdb_list = get_imdb_list(imdb_list_id)
    series_list = filter_imdb_list(imdb_list, 'Title Type', 'tvSeries')

    for series in series_list:
        tvdb_id = get_tvdb_id(series.get('Const'))
        series_info = lookup_series(tvdb_id)
        response = send_to_sonarr(series_info)
        print(response)
