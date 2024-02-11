from selenium import webdriver
from PIL import Image
from io import BytesIO
import requests
import re

# Constants
IMAGE_DIR = "images"

# Download all images
def download_images(url: str):
    driver.get(url)
    images = re.findall(r'https://media.forgecdn.net[a-zA-Z0-9/]*.png', driver.page_source)
    print(images)
    for index, image in enumerate(images):
        Image.open(BytesIO(requests.get(image).content)).save(IMAGE_DIR + "\\" + str(index) + ".png")

# Main Function
if __name__ == '__main__':
    driver = webdriver.Firefox()
#    download_images("https://legacy.curseforge.com/minecraft/bukkit-plugins")
#    download_images("https://legacy.curseforge.com/minecraft/modpacks")
#    download_images("https://legacy.curseforge.com/minecraft/customization")
#    download_images("https://legacy.curseforge.com/minecraft/mc-addons")
#    download_images("https://legacy.curseforge.com/minecraft/mc-mods")
#    download_images("https://legacy.curseforge.com/minecraft/texture-packs")
#    download_images("https://legacy.curseforge.com/minecraft/worlds")
    driver.close()