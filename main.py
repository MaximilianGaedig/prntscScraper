# https://prnt.sc/{any 2 letters upper/lower}{any 4 numbers}
# Example:
# https://prnt.sc/da3344
import string
import requests
import os
import glob
from tqdm import tqdm
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"}

if not os.path.exists('images'):
    os.mkdir('images')

for letter in tqdm(string.ascii_letters, desc="First letter"):
    for letter2 in tqdm(string.ascii_letters, desc="Second letter"):
        letter_comb = letter + letter2
        for i in tqdm(range(0, 9999), desc="Number", unit_scale=True):
            link_val = f"{letter_comb}{i:04}"
            try:
                if not len(glob.glob(f'images/{link_val}*')) == 1:
                    # print(f"searching https://prnt.sc/{link_val}")
                    request = requests.get(
                        f"https://prnt.sc/{link_val}", headers=headers)
                    text = request.text
                    end_index = text.find(
                        f' crossorigin="anonymous" alt="Lightshot screenshot" id="screenshot-image" image-id="{link_val}"')
                    start_index = request.text.rfind('src=', 0, end_index)
                    file_url = f"{text[start_index + 5:end_index - 1]}"
                    if "https:" not in file_url:
                        file_url = f"https:{file_url}"
                    extension = file_url[file_url.rfind('.'):]
                    # print(f"downloading {file_url}")
                    if request.status_code == 200:
                        image_request = requests.get(file_url, headers=headers)
                        if image_request.status_code == 200:
                            with open(f"images/{link_val}{extension}", "wb") as image:
                                image.write(image_request.content)
                                image.close()
                        else:
                            raise Exception(
                                f"status code for image: {image_request.status_code}")

                    else:
                        raise Exception(
                            f"status code for request: {image_request.status_code}")
            except Exception as e:
                print(f"getting {link_val} had following error: {e}")
