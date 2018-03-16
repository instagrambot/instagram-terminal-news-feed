import getpass
import json
import os
import requests
from display import display_to_terminal

def get_credential():
    if not os.path.exists('credential.json'):
        return
    try:
        with open('credential.json') as json_data:
            credential = json.load(json_data)
            return credential
    except FileNotFoundError:
        print("credential.json file not found in current directory. Exiting.")
        exit()

def fetch_news_feed(session):
    res = session.get("https://i.instagram.com/api/v1/feed/timeline/", headers={
        'user-agent':"Instagram 10.3.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+",
        'cookie':'sessionid={0};'.format(session.cookies['sessionid'])
    })
    if res.status_code != 200:
        print("ERROR: got "+str(res.status_code)+" when fetching!")
        exit()
    res = json.loads(res.text)
    posts_info = {}
    for item in res['items']:
        if 'user' not in item: continue
        username = item['user']['username']
        key = username + '_' +  str(item['taken_at']) + '.jpg'
        try:
            posts_info[key] = {
                'username': username,
                'caption': item['caption']['text'] if item['caption'] else "",
                'image_url': item['image_versions2']['candidates'][0]['url'],
                'likes': str(item['like_count']) if item['like_count'] else '0',
                'site_url': 'https://www.instagram.com/p/' + item['code'] + '/?taken-by=' + username
            }
        except KeyError:
            pass
    return posts_info

def save_image(posts_info, session):
    if not os.path.exists('images'):
        os.makedirs('images')

    for key in posts_info.keys():
        res = session.get(posts_info[key]['image_url'])
        with open('images/' + key, 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

def remove_image_dir():
    file_list = os.listdir('./images/')
    for filename in file_list:
        os.remove('./images/' + filename)

def save_credentials(credential, permission):
    if not permission:
        return
    with open('credential.json', 'w') as _file:
        json.dump(credential, _file)

def get_login_session(credential):
    session = requests.Session()
    session.headers.update({'Referer': 'https://www.instagram.com/'})
    req = session.get('https://www.instagram.com/')
    session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
    login_data = credential
    res = session.post('https://www.instagram.com/accounts/login/ajax/', data=login_data, allow_redirects=True)
    res_text = json.loads(res.text);
    if res_text['status'] == 'fail':
        return None, res_text
    return session, res_text

def login(credential):
    if credential:
        session, _ = get_login_session(credential)
        return session

    user, pwd = "", ""
    while True:
        user = input('Username: ')
        pwd = getpass.getpass(prompt='Password: ')
        session, res = get_login_session({"username": user, "password": pwd})
        if res['status'] == 'fail':
            print(res['message'])
            exit()
        if not res['authenticated']:
            print("Bad username or password")
        else:
            break

    permission = input("save credentials(y/n)? [n]: ")
    credential = {"username": user, "password": pwd}
    save_credentials(credential, permission == 'y')
    return session

def main():
    credential = get_credential()
    session = login(credential)
    posts_info = fetch_news_feed(session)
    save_image(posts_info, session)
    display_to_terminal(posts_info)
    remove_image_dir()

if __name__ == '__main__':
    main()
