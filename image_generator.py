from selenium import common as selenium
from selenium import webdriver
from PIL import ImageDraw
from PIL import ImageFont
from PIL import Image
from io import BytesIO
import requests
import json
import re
import os

# Constants
OUTPUT_DIR = "output"
FONT_DIR = "fonts"
IMAGE_DIR = "images"
TEMPLATE_IMAGE = "Template.png"
TEXT_FONT = "arial.ttf"
TITLE_FONT = "arialbd.ttf"
AVATAR_SIZE = (150, 150)
AVATAR_POSITION = (25, 27)
LOADER_SIZE = (75, 75)
LOADER_POSITION = (1400, 27)
LOADER_SPACING = (15, 0)
LOADER_DIRECTION = (-1, 0)
CATEGORY_SIZE = (55, 55)
CATEGORY_POSITION = (1420, 122)
CATEGORY_SPACING = (15, 0)
CATEGORY_DIRECTION = (-1, 0)
TITLE_POSITION = (195, 24)
AUTHOR_POSITION = (195, 73)
SUBTITLE_POSITION = (195, 114)
DESCRIPTION_POSITION = (195, 153)

def get_tuple_position(index: int, position: tuple[int, int], size: tuple[int, int], spacing: tuple[int, int], direction: tuple[int, int]) -> tuple[int, int]:
    return get_position(index, position[0], size[0], spacing[0], direction[0]), get_position(index, position[1], size[1], spacing[1], direction[1])

def get_position(index: int, position: int, size: int, spacing: int, direction: int) -> int:
    return position + (index * (spacing + size) * direction, 0)[index == 0 or direction == 0]

def get_json_info(json_info, informations: list[str], on_error_value = None, on_error_message: str | None = None):
    try:
        for information in informations:
            json_info = json_info[information]
    except (TypeError, KeyError):
        if on_error_message is not None and on_error_message:
            print(on_error_message)
        return on_error_value
    return json_info

def generate_image(url: str):
    # Get mod JSON from CurseForge Website
    driver.get(url)
    mod_json = json.loads(re.sub(r'<[a-zA-Z0-9=/"\-_.:;%?& ]*script[a-zA-Z0-9=/"\-_.:;%?& ]*>', '', re.search(r'<script[a-zA-Z0-9=/"\-_.:;%?& ]*id=\"__NEXT_DATA__\"[a-zA-Z0-9=/"\-_.:;%?& ]*>(.*)</script>', driver.page_source).group(0)))

    # Get mod information from JSON
    name = get_json_info(mod_json, ["props", "pageProps", "project", "name"], "", "Le titre du mod n'a pas été trouvé")
    slug = get_json_info(mod_json, ["props", "pageProps", "project", "slug"], name, "Le slug du mod n'a pas été trouvé")
    summary = get_json_info(mod_json, ["props", "pageProps", "project", "summary"], "", "La description du mod n'a pas été trouvé")
    downloads = int(get_json_info(mod_json, ["props", "pageProps", "project", "downloads"], 0, "Le nombre de téléchargement du mod n'a pas été trouvé"))
    downloads = (downloads, f"{round(downloads / 1000, 1)}K", f"{round(downloads / 1000000, 1)}M", f"{round(downloads / 1000000000, 1)}B")[(downloads >= 1000) + (downloads >= 1000000) + (downloads >= 1000000000)]
    author = get_json_info(mod_json, ["props", "pageProps", "project", "author", "name"], "", "L'auteur du mod n'a pas été trouvé")
    avatar_url = get_json_info(mod_json, ["props", "pageProps", "project", "avatarUrl"], "", "L'avatar du mod n'a pas été trouvé")
    loaders = []
    versions = []
    categories = []
    for loader in get_json_info(mod_json, ["props", "pageProps", "gameFlavor", "items"], [], "Les modLoaders du mod n'ont pas été trouvés"):
        loaders.append(loader["name"])
    for version in get_json_info(mod_json, ["props", "pageProps", "gameVersions"], [], "Les versions du mod n'ont pas été trouvés"):
        versions.append(version["value"])
    for category in get_json_info(mod_json, ["props", "pageProps", "project", "categories"], [], "Les categories du mod n'ont pas été trouvés"):
        categories.append(category["name"].replace("/", "&"))  # category["slug"]
    # Remove false version from versions and put them in loaders
    loaders += [version for version in versions if not re.search(r"[a-zA-Z0-9\-.]*[0-9]+\.[0-9]+[a-zA-Z0-9\-.]*", version)]
    versions = [version for version in versions if version not in loaders]
    print(f'\n{name} ({slug})\nPar {author} ({downloads} Téléchargements)\n{summary}\nAvatar: {avatar_url}\nModLoaders: {loaders}\nVersions: {versions}\nCategories: {categories}\n')
    # Create image
    mod_image = Image.open(IMAGE_DIR + "\\" + TEMPLATE_IMAGE)
    # Add text
    image_drawing = ImageDraw.Draw(mod_image)
    title_font = ImageFont.truetype(FONT_DIR + "\\" + TITLE_FONT, 40)
    description_font = ImageFont.truetype(FONT_DIR + "\\" + TEXT_FONT, 20)
    while image_drawing.textbbox(TITLE_POSITION, name, font = title_font)[2] >= get_tuple_position(len(loaders) - 1, LOADER_POSITION, LOADER_SIZE, LOADER_SPACING, LOADER_DIRECTION)[0] and ' ' in name:
        name = name.rsplit(' ', 1)[0]
    if image_drawing.textbbox(DESCRIPTION_POSITION, summary, font = description_font)[2] >= get_tuple_position(len(categories) - 1, CATEGORY_POSITION, CATEGORY_SIZE, CATEGORY_SPACING, CATEGORY_DIRECTION)[0] and ' ' in summary:
        summary = summary.rsplit(' ', 1)[0]
        while image_drawing.textbbox(DESCRIPTION_POSITION, f"{summary}...", font = description_font)[2] >= get_tuple_position(len(categories) - 1, CATEGORY_POSITION, CATEGORY_SIZE, CATEGORY_SPACING, CATEGORY_DIRECTION)[0] and ' ' in summary:
            summary = summary.rsplit(' ', 1)[0]
        summary += "..."
    image_drawing.text(TITLE_POSITION, name, font = title_font, fill = (0, 0, 0))
    image_drawing.text(AUTHOR_POSITION, f"Par {author}", font = ImageFont.truetype(FONT_DIR + "\\" + TITLE_FONT, 30), fill = (0, 0, 0))
    if len(versions) > 0:
        image_drawing.text(SUBTITLE_POSITION, f"[{(versions[0], f'{versions[-1]} - {versions[0]}')[len(versions) > 1]}] ({downloads} téléchargements)", font = ImageFont.truetype(FONT_DIR + "\\" + TITLE_FONT, 25), fill = (0, 0, 0))
    else:
        image_drawing.text(SUBTITLE_POSITION, f"({downloads} téléchargements)", font = ImageFont.truetype(FONT_DIR + "\\" + TITLE_FONT, 25), fill = (0, 0, 0))
    image_drawing.text(DESCRIPTION_POSITION, summary, fill = (0, 0, 0), font = description_font)
    # Add mod avatar
    avatar = Image.open(BytesIO(requests.get(avatar_url).content)).resize(AVATAR_SIZE)
    mod_image.paste(avatar, AVATAR_POSITION, avatar.convert('RGBA'))
    # Add loaders
    for index, loader in enumerate(loaders):
        loader_image = Image.open(IMAGE_DIR + "\\" + loader + ".png").resize(LOADER_SIZE)
        mod_image.paste(loader_image, get_tuple_position(index, LOADER_POSITION, LOADER_SIZE, LOADER_SPACING, LOADER_DIRECTION), loader_image.convert('RGBA'))
    # Add categories
    for index, category in enumerate(categories):
        category_image = Image.open(IMAGE_DIR + "\\" + category + ".png").resize(CATEGORY_SIZE)
        mod_image.paste(category_image, get_tuple_position(index, CATEGORY_POSITION, CATEGORY_SIZE, CATEGORY_SPACING, CATEGORY_DIRECTION), category_image.convert('RGBA'))
    # Save image
    os.makedirs(OUTPUT_DIR, exist_ok = True)
    mod_image.save(OUTPUT_DIR + "\\" + slug + ".png")

# Main Function
if __name__ == '__main__':
    driver = webdriver.Firefox()
    driver.minimize_window()
    user_input = ""
    while user_input.upper() != "EXIT":
        user_input = input("Veuillez saisir l'URL d'un mod CurseForge ou son slug: ").strip()
        try:
            if not user_input:
                continue
            if user_input.upper() == "EXIT":
                break
            elif "curseforge.com" in user_input:
                generate_image((f"http://{user_input}", user_input)[user_input.startswith("http")])
            elif re.search(r"[a-zA-Z0-9\-]+", user_input):
                generate_image(f"https://www.curseforge.com/minecraft/mc-mods/{user_input.lower()}")
            else:
                print("URL Invalide")
        except (KeyError, IndexError) as error:
            print(f"URL Curseforge Invalide: {error.args}")
        except (AttributeError, TypeError, requests.exceptions.MissingSchema) as error:
            print(f"URL de mod CurseForge Invalide: {error.args}")
        except FileNotFoundError as error:
            print(f'Le fichier "{error.filename}" n\'existe pas')
        except selenium.exceptions.WebDriverException:
            print("Veuillez garder le navigateur ouvert")
            driver = webdriver.Firefox()
            driver.minimize_window()
    driver.close()