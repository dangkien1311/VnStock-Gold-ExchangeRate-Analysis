import os
import requests
import pandas as pd
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

def file_exists_in_folder(folder_path, file_name):
    file_path = os.path.join(folder_path, file_name)
    return os.path.isfile(file_path)

val = input("Enter your words: ") 
words = val.split(',')
words_list = [item.lower() for item in words]

for i in words_list:
    base_url = "https://dictionary.cambridge.org"
    url = f"https://dictionary.cambridge.org/dictionary/english/{i}"
    folder_path = '/media/kiendt/DATA/ielts reading/audio file'
    with requests.Session() as session:
        try:
            session.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
            response = session.get(url,allow_redirects=True)
            soup = BeautifulSoup(response.content, "html.parser")
            true_name = response.url.split('/')[-1]
            if '?' in true_name:
                true_name = true_name.split('?')[0]
            check_path = f'{true_name}.mp3'
            if file_exists_in_folder(folder_path,check_path):
                print(f"word {i} exists in folder {folder_path} with name {check_path}")
                continue
            save_path = f'/media/kiendt/DATA/ielts reading/audio file/{true_name}.mp3'
            check_url= 'https://dictionary.cambridge.org/dictionary/english/'
            if check_url == response.url:
                print(f'word "{i}" is not correct or not exits in cambride data')
                continue
            frame = soup.find(id="audio1")
            source_tag = frame.find('source')
            frame_url = urljoin(base_url, source_tag['src'])
            response_mp3 = requests.get(url = frame_url, headers= session.headers)
            with open(save_path,'wb') as f:
                f.write(response_mp3.content)
                print(f'successful write {i} to {save_path}')
        except Exception  as e:
            print(e)