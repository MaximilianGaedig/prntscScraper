# https://prnt.sc/{any 2 letters upper/lower}{any 4 numbers}
# Example:
# https://prnt.sc/da3344
import argparse
import concurrent.futures
import glob
import os
import string

import cv2
import pytesseract
import requests
from PIL import Image
from progressbar import progressbar

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 "
                  "Safari/537.36 "
}
preprocess = "thresh"  # blur
# global item_limit
global search_terms
global ocr


def scrape_image(link_val):
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
    if request.ok:
        image_request = requests.get(file_url, headers=headers)
        if image_request.ok:
            with open(f"images/{link_val}{extension}", "wb") as image:
                image.write(image_request.content)
                image.close()
        else:
            raise Exception(
                f"status code for image: {image_request.status_code}")
    else:
        raise Exception(
            f"status code for request: {request.status_code}")
    if ocr:
        image_path = glob.glob(f'images/{link_val}*')[0]
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if preprocess == "thresh":
            gray = cv2.threshold(
                gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        elif preprocess == "blur":
            gray = cv2.medianBlur(gray, 3)
        tmp_name = image_path[7:]
        cv2.imwrite(tmp_name, gray)
        text = pytesseract.image_to_string(
            Image.open(tmp_name)).replace("\n", "")
        os.remove(tmp_name)
        if any(substring in text.lower() for substring in search_terms):
            print(f"found something in {link_val}, ocr string: {text}")
            with open("results.txt", "a") as results:
                results.write(
                    f"found something in {link_val}, ocr string: {text}\n")
        os.rename(image_path, f"images_scanned/{image_path[7:]}")


def process(link_val):
    try:
        if len(glob.glob(f'images_scanned/{link_val}*')) != 1:
            if len(glob.glob(f'images/{link_val}*')) != 1:
                scrape_image(link_val)

    except Exception as e:
        print(f"getting {link_val} had following error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape images off prnt.sc')
    parser.add_argument('--singular-image', help='Enable or disable image recognition', default='')
    # parser.add_argument('--count', help='The number of images to scrape. 0 for infinite', default=0, type=int)
    parser.add_argument('--image-recognition', help='Enable or disable image recognition', default=True,
                        type=bool)
    parser.add_argument('--search-terms', help='Terms to search for', default=[], type=list)
    parser.add_argument('--output', help='The path where images will be stored.', default='images')
    parser.add_argument('--scanned-output', help='The path where scanned images will be stored.',
                        default='images_scanned')
    args = parser.parse_args()
    if not os.path.exists(args.output):
        os.mkdir(args.output)
    if ocr:
        if not os.path.exists(args.scanned_output):
            os.mkdir(args.scanned_output)
    # item_limit = args.count
    search_terms = args.search_terms
    ocr = args.image_recognition
    if args.singular_image != '':
        args = parser.parse_args()
        pool = string.ascii_letters + string.digits
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for char1 in progressbar(pool):
                for char2 in progressbar(pool):
                    for char3 in progressbar(pool):
                        for char4 in progressbar(pool):
                            for char5 in progressbar(pool):
                                letter_comb = char1 + char2 + char3 + char4 + char5
                                process(f"{letter_comb}")
    else:
        scrape_image(args.singular_image)
