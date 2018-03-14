#!/usr/bin/python3
import json
import os
import requests

def get_config():
    try:
        with open('config.json') as json_data:
            config = json.load(json_data)
            return config
    except FileNotFoundError:
        print("config.json file not found in current directory. Exiting.")
        exit()

def fetch_news_feed(session):
    response = session.get("https://i.instagram.com/api/v1/feed/timeline/", headers={
        'user-agent':"Instagram 10.3.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+",
        'cookie':'sessionid={0};'.format(session.cookies['sessionid'])
    })
    if response.status_code != 200:
        print("ERROR: got "+str(response.status_code)+" when fetching!")
        exit()
    response = json.loads(response.text)
    image_info = []
    for item in response['items']:
        # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2')
        # print(json.dumps(item, indent=4))
        try:
            url = {
                'url': item['image_versions2']['candidates'][0]['url'],
                'username': item['user']['username'],
                'caption': item['caption']['text']
            }
            image_info.append(url)
        except KeyError:
            pass
    print(image_info)

def get_login_session(config):
    session = requests.Session()
    session.headers.update({'Referer': 'https://www.instagram.com/'})
    req = session.get('https://www.instagram.com/')
    session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
    login_data = {'username': config['username'], 'password': config['password']}
    session.post('https://www.instagram.com/accounts/login/ajax/', data=login_data, allow_redirects=True)
    return session

def main():
    config = get_config()
    session = get_login_session(config)
    fetch_news_feed(session)

if __name__ == '__main__':
    main()
