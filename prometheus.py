import tomllib
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests


class Crawler:
    def __init__(self):
        self.cfg_file_path = Path(r'textbooks.toml')
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        }
        self.session = requests.session()
        self.session.headers.update(self.headers)
        self.base_folder = Path(r'./text_book')
        self.create_folder()
        self.load_cfg_file()

    def load_cfg_file(self):
        if self.cfg_file_path.exists():
            with open(self.cfg_file_path, 'rb') as f:
                urls = tomllib.load(f)['urls_list']
                print(urls)
            if urls:
                for url in urls:
                    self.download_text(url)
        else:
            content = "请访问该网站https://basic.smartedu.cn/tchMaterial" \
                      "#将所需课本的URL填入中urls_list中，用半角单引号''包裹，结尾附加半角逗号,每个url一行，所有标点皆为英文符号\n" \
                      "#例如'https://basic.smartedu.cn/tchMaterial/detail?contentType=assets_document&contentId=144425f4" \
                      "-87a0-4a3a-82b7-ea7be112856c&catalogType=tchMaterial&subCatalog=tchMaterial',\n\n" \
                      "urls_list = [\n\t\n]"
            with open(self.cfg_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def create_folder(self):
        Path.mkdir(self.base_folder, parents=True, exist_ok=True)

    def parse_url(self, url: str):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        content_id = query_params.get('contentId', [None])[0]
        content_type = query_params.get('contentType', [None])[0]
        if not content_type:
            return
        text_response = self.session.get(
            f'https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/details/{content_id}.json')
        # audio_response = self.session.get(
        #     f'https://s-file-2.ykt.cbern.com.cn/zxx/ndrs/resources/{content_id}/relation_audios.json')
        aa = f'https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/details/{content_id}.json'
        print(aa)
        text_data = text_response.json()
        text_tile = text_data['title'].replace(' ', '')
        print(text_tile)
        for item in text_data['ti_items']:
            if item['lc_ti_format'] == 'pdf':
                text_resource_url: str = item['ti_storages'][0].replace('-private', '')
                break
        return text_resource_url, content_id, text_tile

    # def get_file_name(self):
    #     file_name = self.url.split('/')[-1].split('?')[0]
    #     file_name = Path(file_name)
    #     page_num = file_name.stem
    #     return file_name, page_num

    # def gen_url(self, page: int):
    #     url_without_query, url_suffix = self.url.split('?')
    #     base_url, file_name = url_without_query.rsplit('/', 1)
    #     file_name = Path(file_name)
    #     return f'{base_url}/{page}{file_name.suffix}?{url_suffix}'

    def download_text(self, url: str):
        text_resource_url, content_id, text_tile = self.parse_url(url)
        print(text_resource_url, content_id, text_tile)
        if '·' in text_tile:
            text_tile = text_tile.split('·')[1]
        response = self.session.get(text_resource_url, stream=True)
        response.raise_for_status()
        file_path = self.base_folder / Path(f'{text_tile}.pdf')
        with open(file_path, 'wb') as f:
            chunk_size = 131072
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # 过滤掉keep-alive新chunk
                    f.write(chunk)
                    f.flush()
            print(f'Downloaded {text_tile}')


if __name__ == '__main__':
    url = r'https://basic.smartedu.cn/tchMaterial/detail?contentType=assets_document&contentId=144425f4-87a0-4a3a-82b7-ea7be112856c&catalogType=tchMaterial&subCatalog=tchMaterial'
    crawler = Crawler()
    # crawler.download_text(url)
