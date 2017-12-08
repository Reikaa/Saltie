import os
import io
import requests
import zipfile


class ServerConverter:
    file_status = {}
    local_file = None
    config_response = None
    download_config = False
    download_model = False

    def __init__(self, server_ip, uploading, download_config, download_model):
        self.server_ip = server_ip
        self.uploading = uploading
        self.download_config = download_config
        self.download_model = download_model

    def load_config(self):
        if self.download_config:
            try:
                self.config_response = requests.get(self.server_ip + '/config/get')
            except Exception as e:
                print('Error downloading config, reverting to file on disk:', e)
                self.download_config = False

    def load_model(self):
        if self.download_model:
            folder = 'training\\saltie\\'
            try:
                b = requests.get(self.server_ip + '/model/get')
                bytes = io.BytesIO()
                for chunk in b.iter_content(chunk_size=1024):
                    if chunk:
                        bytes.write(chunk)
                print('downloaded model')
                with zipfile.ZipFile(bytes) as f:
                    if not os.path.isdir(folder):
                        os.makedirs(folder)
                    for file in f.namelist():
                        contents = f.open(file)
                        print(file)
                        with open(os.path.join(folder, os.path.basename(file)), "wb") as unzipped:
                            unzipped.write(contents.read())
            except Exception as e:
                print('Error downloading model, not writing it:', e)
                download_model = False

    def maybe_upload_replay(self, fn, model_hash):
        try:
            self._upload_replay(fn, model_hash)
        except:
            print('catching all errors to keep the program going')

    def _upload_replay(self, fn, model_hash):
        if not self.uploading:
            self.add_to_local_files(fn)
        with open(fn, 'rb') as f:
            r = ''
            try:
                r = requests.post(self.server_ip, files={'file': f})
            except ConnectionRefusedError as error:
                print('server is down ', error)
                self.add_to_local_files(fn)
            except ConnectionError as error:
                print('server is down', error)
                self.add_to_local_files(fn)
            except:
                print('server is down, general error')
                self.add_to_local_files(fn)

            try:
                print('Upload', r.json()['status'])
                self.file_status[fn] = True
            except:
                self.add_to_local_files(fn)
                print('error retrieving status')

    def add_to_local_files(self, fn):
        if fn not in self.file_status:
            self.file_status[fn] = False

    def retry_files(self):
        for key in self.file_status:
            if not self.file_status[key]:
                print('retrying file:', key)
                self.maybe_upload_replay(key)
        print('all files retried')

    def download_files(self):
        self.load_config()
        self.load_model()
