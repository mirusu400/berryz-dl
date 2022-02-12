import requests
import json
import os
import sys
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib import parse

class Berryz:
    def __init__(self, link):
        self.head_link = link
        self.files = []
        self.folders = []

    def get_file_list(self, link = "/"):
        r = requests.get(self.head_link + link)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table', {'class': 'sortable'})
        trs = table.find("tbody").find_all('tr')
        for tr in trs:
            c_elem, i_elem, f_elem, s_elem, d_elem = tr.find_all('td')
            file_type = "folder" if i_elem.find("img")['alt'].strip() == "D" else "file"
            file_name = f_elem.find('a').text.strip()
            file_link = f_elem.find('a')['href'].strip()
            file_size = s_elem.text.strip()
            file_date = d_elem.text.strip()
            if file_type == "folder":
                self.folders.append({
                    "file_type": file_type,
                    "file_name": file_name,
                    "file_link": link + file_link,
                    "file_size": file_size,
                    "file_date": file_date
                })
            elif file_type == "file":
                self.files.append({
                    "file_type": file_type,
                    "file_name": file_name,
                    "file_link": link + file_link,
                    "file_size": file_size,
                    "file_date": file_date
                })
            else:
                raise Exception("Unknown file type")

        return self.files

    def get_file_list_recursive(self, link = "/"):
        if link == "/":
            print("[*] Fetching folder: {}".format("root"))
        self.get_file_list(link)
        while (len(self.folders) > 0):
            folder = self.folders.pop()
            print("[*] Fetching folder: {}".format(folder['file_name']))
            self.get_file_list_recursive(folder['file_link'])
    
    
    def download_file(self, link):
        download_dir = f"./downloads{parse.unquote(link)}"
        try:
            os.makedirs(os.path.dirname(download_dir))
        except:
            pass
        print(f"[*] Downloading file: {link}")
        r = requests.get(self.head_link + link, stream=True)
        with open(download_dir, 'wb') as f:
            for chunk in tqdm(r.iter_content(chunk_size=1024)):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return True
    
    def download_file_batch(self):
        for file in self.files:
            self.download_file(file['file_link'])
    
    def dump_json(self):
        with open("out.json", "w", encoding="utf-8") as f:
            json.dump(b.files, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    try:
        link = sys.argv[1]
    except:
        print("[*] Usage: python main.py <link>")
        exit(0)

    b = Berryz(link)
    b.get_file_list_recursive()
    b.download_file_batch()
    b.dump_json()
    