from selenium import webdriver
import json
import re
import os

# Constants
IMAGE_DIR = "images"

# Check all images
def image_checker(url: str):
    driver.get(url)
    mod_json = json.loads(re.sub(r'<[a-zA-Z0-9=/"\-_.:;%?& ]*script[a-zA-Z0-9=/"\-_.:;%?& ]*>', '', re.search(r'<script[a-zA-Z0-9=/"\-_.:;%?& ]*id=\"__NEXT_DATA__\"[a-zA-Z0-9=/"\-_.:;%?& ]*>(.*)</script>', driver.page_source).group(0)))
    for category in mod_json["props"]["pageProps"]["categoriesTree"]["allCategories"]:
        if not os.path.exists(IMAGE_DIR + "\\" + category["name"].replace("/", "&") + ".png"):
            print(f"Image for category '{category["name"].replace("/", "&")}' do not exist")

# Main Function
if __name__ == '__main__':
    driver = webdriver.Firefox()
    image_checker("https://www.curseforge.com/minecraft/mc-mods/jei")
    driver.close()