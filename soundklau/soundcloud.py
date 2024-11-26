import random
import re
import sys
import time
from ssl import SSLContext
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import json
from urllib.parse import unquote


SC_TRACK_RESOLVE_REGEX = r"^(?:https?:\/\/)soundcloud\.com\/[a-z0-9](?!.*?(-|_){2})[\w-]{1,23}[a-z0-9]\/[^\s]+$"

SSL_VERIFY=False

client_id = None
auth_token = None

def set_client_id(new_client_id):
    """ Set client_id """
    global client_id
    client_id = new_client_id

def set_auth_token(new_auth_token):
    """ Set auth_token """
    global auth_token
    auth_token = new_auth_token

def get_ssl_setting():
    """ Get ssl context """
    if SSL_VERIFY:
        return None
    return SSLContext()

def eprint(*values, **kwargs):
    """ Print to stderr """
    print(*values, file=sys.stderr, **kwargs)

def get_filename_from_header(headers):
    content_disposition = headers.get("Content-Disposition")
    if content_disposition:
        # Extract filename from the Content-Disposition header
        parts = content_disposition.split(";")
        for part in parts:
            if "filename=" in part:
                filename = part.split("=", 1)[1].strip().strip('"')
                return unquote(filename)
    return None

def download_file(url):
    """ Download file from url """
    req = Request(url)
    
    if auth_token:
        req.add_header('Authorization', auth_token)
    with urlopen(req, context=get_ssl_setting()) as client:
        headers = client.info()  # Get headers
        suggested_filename = get_filename_from_header(headers)
        return (client.read(), suggested_filename)

SCRAPE_URLS = [
    'https://soundcloud.com/mt-marcy/cold-nights'
]

def api_get(url):
    """ make a GET request to the soundcloud api with a client_id"""
    global client_id
    global auth_token
    if not client_id:
        client_id = get_client_id()
    

    url = f"{url}&client_id={client_id}"
    req = Request(url)
    
    if auth_token:
        req.add_header('Authorization', auth_token)
    with urlopen(req, context=get_ssl_setting()) as client:
        return json.loads(client.read().decode('utf-8'))
    

def get_page(url):
    """ get text from url """
    with urlopen(url, context=get_ssl_setting(), ) as client:
        return client.read().decode('utf-8')

def find_script_urls(html_text):
    """ Get script url that has client_id in it """
    dom = BeautifulSoup(html_text, 'html.parser')
    scripts = dom.findAll('script', attrs={'src': True})
    scripts_list = []
    for script in scripts:
        src = script['src']
        if 'cookielaw.org' not in src:  # filter out cookielaw.org
            scripts_list.append(src)
    return scripts_list

def extract_client_id(script_text):
    """ Extract client_id from script """
    client_id = re.findall(r'client_id=([a-zA-Z0-9]+)', script_text)
    if len(client_id) > 0:
        return client_id[0]
    return False


def get_client_id():
    """ get creds """
    url = random.choice(SCRAPE_URLS)
    page_text = get_page(url)
    script_urls = find_script_urls(page_text)
    client_id = None
    for script in script_urls:
        if not client_id:
            if type(script) is str and not "":  # pylint: disable=simplifiable-condition
                js_text = f'{get_page(script)}'
                client_id = extract_client_id(js_text)
        else:
            return client_id

def fetch_liked_tracks(user_id):
    base_url = f"https://api-v2.soundcloud.com/users/{user_id}/track_likes"
    params = {
        "limit": 24,
        "offset": 0,
        "linked_partitioning": 1,
        "app_version": 1732529162,
        "app_locale": "en"
    }
    
    all_likes = []
    next_href = base_url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])
    
    while next_href:
        response = api_get(next_href)
        next_href = response.get('next_href')
        all_likes.extend(response['collection'])
    return all_likes

def download_track(track_id):
    base_url = f"https://api-v2.soundcloud.com/tracks/{track_id}/download"
    params = {
        "app_version": 1732529162,
        "app_locale": "en"
    }    
    url =  base_url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])
    downloadUrl = api_get(url)['redirectUri']
    data, suggested_filename = download_file(downloadUrl)
    f = open(suggested_filename, "wb")
    f.write(data)    
    f.close()
    return suggested_filename