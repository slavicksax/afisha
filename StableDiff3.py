import base64
import io
import requests
from PIL import Image
import json
import time

def getImage2(promt):
    response = requests.post(
        f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
        headers={
            "authorization": f"Bearer sk-DWe5DFhtUVAijUK3IsktkI9vurzBUb4axb4HuSyG5cUFhcWb",
            "accept": "image/*"
        },
        files={"none": ''},
        data={
            "prompt": promt,
            "output_format": "jpeg",
        },
    )

    if response.status_code == 200:
        return response.content
        #with open("./dog-wearing-glasses.jpeg", 'wb') as file:
        #   file.write(response.content)
    else:
        raise Exception(str(response.json()))



class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                print('DONE')
                return data['images']
            elif data['status'] == 'PROCESSING':
                print('PROCESSING')
            elif data['status'] == 'FAIL':
                print('FAIL')
            elif data['status'] == 'FAIL':
                print('FAIL')
            attempts -= 1
            time.sleep(delay)


def getImage(promt):
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '9CD9957FCC60FF2A7AC96DC69352820D', '72D1A6C91FDE1FB9C2BF6E2449C94308')
    model_id = api.get_model()
    uuid = api.generate(promt, model_id)
    images = api.check_generation(uuid)
    image_data = io.BytesIO(base64.b64decode(images[0]))
    #image = Image.open(image_data)
    return image_data
    #image.save('output.png', 'PNG')