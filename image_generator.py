from json import JSONDecodeError
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
ICON_FONT = "seguiemj.ttf"
AVATAR_CORNER = 0
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
ICON_POSITION = (193, 120)
ICON_SPACING = (35, 0)
DESCRIPTION_POSITION = (195, 153)

def add_image_corner(image: Image, radius: int):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2 - 1, radius * 2 - 1), fill=255)
    alpha = Image.new('L', image.size, 255)
    w, h = image.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
    image.putalpha(alpha)
    return image

def get_tuple_position(index: int, position: tuple[int, int], size: tuple[int, int], spacing: tuple[int, int], direction: tuple[int, int]) -> tuple[int, int]:
    return get_position(index, position[0], size[0], spacing[0], direction[0]), get_position(index, position[1], size[1], spacing[1], direction[1])

def get_position(index: int, position: int, size: int, spacing: int, direction: int) -> int:
    return position + (index * (spacing + size) * direction, 0)[index == 0 or direction == 0]

def get_side_icon(is_client: bool, is_server: bool):
    if is_client and is_server:
        return "🌐"
    elif is_client:
        return "🖥️"
    elif is_server:
        return "📟"
    else:
        return ""

def get_json_info(json_info, informations: list[str | int] | str, on_error_value = None, on_error_message: str | None = None):
    try:
        if isinstance(informations, str):
            json_info = json_info[informations]
        else:
            for information in informations:
                json_info = json_info[information]
    except (TypeError, KeyError):
        if on_error_message is not None and on_error_message:
            print(on_error_message)
        return on_error_value
    return json_info

def generate_curseforge_image(url: str):
    # Get mod JSON from CurseForge Website
    driver.get(url)
    mod_json = json.loads(re.sub(r'<[a-zA-Z0-9=/"\-_.:;%?& ]*script[a-zA-Z0-9=/"\-_.:;%?& ]*>', '', re.search(r'<script[a-zA-Z0-9=/"\-_.:;%?& ]*id=\"__NEXT_DATA__\"[a-zA-Z0-9=/"\-_.:;%?& ]*>(.*)</script>', driver.page_source).group(0)))
    # Get mod information from JSON
    name = get_json_info(mod_json, ["props", "pageProps", "project", "name"], "", "Le titre du mod n'a pas été trouvé")
    slug = get_json_info(mod_json, ["props", "pageProps", "project", "slug"], name, "Le slug du mod n'a pas été trouvé")
    summary = get_json_info(mod_json, ["props", "pageProps", "project", "summary"], "", "La description du mod n'a pas été trouvé")
    downloads = int(get_json_info(mod_json, ["props", "pageProps", "project", "downloads"], 0, "Le nombre de téléchargement du mod n'a pas été trouvé"))
    author = get_json_info(mod_json, ["props", "pageProps", "project", "author", "name"], "", "L'auteur du mod n'a pas été trouvé")
    avatar_url = get_json_info(mod_json, ["props", "pageProps", "project", "avatarUrl"], "", "L'avatar du mod n'a pas été trouvé")
    loaders = []
    versions = []
    categories = []
    for loader in get_json_info(mod_json, ["props", "pageProps", "gameFlavor", "items"], [], "Les modLoaders du mod n'ont pas été trouvés"):
        loaders.append(loader["name"])
    for version in get_json_info(mod_json, ["props", "pageProps", "gameVersions"], [], "Les versions du mod n'ont pas été trouvées"):
        versions.append(version["value"])
    for category in get_json_info(mod_json, ["props", "pageProps", "project", "categories"], [], "Les categories du mod n'ont pas été trouvées"):
        categories.append(category["name"].replace("/", "&"))  # category["slug"]
    # Remove false version from versions and put them in loaders
    loaders += [version for version in versions if not re.search(r"[a-zA-Z0-9\-.]*[0-9]+\.[0-9]+[a-zA-Z0-9\-.]*", version)]
    versions = [version for version in versions if version not in loaders]
    generate_image(name, slug, author, downloads, summary, avatar_url, loaders, versions, categories)

def generate_modrinth_image(url: str):
    # Get mod JSON from Modrinth Website
    mod_json = json.loads(requests.get(url).content)
    # Get mod information from JSON
    name = get_json_info(mod_json, "title", "", "Le titre du mod n'a pas été trouvé")
    slug = get_json_info(mod_json, "slug", name, "Le slug du mod n'a pas été trouvé")
    summary = get_json_info(mod_json, "description", "", "La description du mod n'a pas été trouvé")
    downloads = int(get_json_info(mod_json, "downloads", 0, "Le nombre de téléchargement du mod n'a pas été trouvé"))
    avatar_url = get_json_info(mod_json, "icon_url", "", "L'avatar du mod n'a pas été trouvé")
    side = get_side_icon(get_json_info(mod_json, "client_side", "").lower() in ("required", "optional"), get_json_info(mod_json, "server_side", "").lower() in ("required", "optional"))
    loaders = []
    versions = []
    categories = []
    for loader in get_json_info(mod_json, "loaders", [], "Les modLoaders du mod n'ont pas été trouvés"):
        loaders.append(loader.title())
    for version in get_json_info(mod_json, "game_versions", [], "Les versions du mod n'ont pas été trouvées"):
        versions.insert(0, version)
    for category in get_json_info(mod_json, "categories", [], "Les categories du mod n'ont pas été trouvées"):
        categories.append(category.replace("/", "&").title())
    for category in get_json_info(mod_json, "additional_categories", [], "Les categories additionnelles du mod n'ont pas été trouvées"):
        categories.append(category.replace("/", "&").title())
    # Get mod author
    author = ""
    #if len(get_json_info(mod_json, "organization", "")) > 0:
        #author = "" # TODO: Organizations not yet available from the API
    if not author:
        for user in json.loads(requests.get(f"https://api.modrinth.com/v2/project/{url.rsplit("/", 1)[-1]}/members").content):
            if get_json_info(user, "role", "").lower() == "owner":
                author = get_json_info(user, ["user", "username"], "", "L'auteur du mod n'a pas été trouvé")
                break
            elif not author:
                author = get_json_info(user, ["user", "username"], "")
    generate_image(name, slug, author, downloads, summary, avatar_url, loaders, versions, categories, side)

def generate_image(name: str, slug: str, author: str, downloads: int, summary: str, avatar_url: str, loaders: list[str], versions: list[str], categories: list[str], side: str = ""):
    downloads = (downloads, f"{round(downloads / 1000, 1)}K", f"{round(downloads / 1000000, 1)}M", f"{round(downloads / 1000000000, 1)}B")[(downloads >= 1000) + (downloads >= 1000000) + (downloads >= 1000000000)]
    print(f'\n{name} ({slug})\nPar {author} ({downloads} Téléchargements) {side}\n{summary}\nAvatar: {avatar_url}\nModLoaders: {loaders}\nVersions: {versions}\nCategories: {categories}\n')
    # Create image
    mod_image = Image.open(IMAGE_DIR + "\\" + TEMPLATE_IMAGE)
    # Add text
    image_drawing = ImageDraw.Draw(mod_image)
    title_font = ImageFont.truetype(FONT_DIR + "\\" + TITLE_FONT, 40)
    description_font = ImageFont.truetype(FONT_DIR + "\\" + TEXT_FONT, 20)
    while image_drawing.textbbox(TITLE_POSITION, name, font = title_font)[2] >= get_tuple_position(len(loaders) - 1, LOADER_POSITION, LOADER_SIZE, LOADER_SPACING, LOADER_DIRECTION)[0] and ' ' in name:
        name = name.rsplit(' ', 1)[0]
    summary = summary.rsplit('\n', 1)[0]
    if image_drawing.textbbox(DESCRIPTION_POSITION, summary, font = description_font)[2] >= get_tuple_position(len(categories) - 1, CATEGORY_POSITION, CATEGORY_SIZE, CATEGORY_SPACING, CATEGORY_DIRECTION)[0] and ' ' in summary:
        summary = summary.rsplit(' ', 1)[0]
        while image_drawing.textbbox(DESCRIPTION_POSITION, f"{summary}...", font = description_font)[2] >= get_tuple_position(len(categories) - 1, CATEGORY_POSITION, CATEGORY_SIZE, CATEGORY_SPACING, CATEGORY_DIRECTION)[0] and ' ' in summary:
            summary = summary.rsplit(' ', 1)[0]
        summary += "..."
    image_drawing.text(TITLE_POSITION, name, font = title_font, fill = (0, 0, 0))
    if len(author) > 0:
        image_drawing.text(AUTHOR_POSITION, f"Par {author}", font = ImageFont.truetype(FONT_DIR + "\\" + TITLE_FONT, 30), fill = (0, 0, 0))
    if len(side) > 0:
        image_drawing.text(ICON_POSITION, side, font = ImageFont.truetype(FONT_DIR + "\\" + ICON_FONT, 25), fill = (0, 0, 0))
    if len(versions) > 0:
        image_drawing.text((SUBTITLE_POSITION, tuple(map(sum, zip(SUBTITLE_POSITION, ICON_SPACING))))[len(side) > 0], f"[{(versions[0], f'{versions[-1]} - {versions[0]}')[len(versions) > 1]}] ({downloads} téléchargements)", font = ImageFont.truetype(FONT_DIR + "\\" + TITLE_FONT, 25), fill = (0, 0, 0))
    else:
        image_drawing.text((SUBTITLE_POSITION, tuple(map(sum, zip(SUBTITLE_POSITION, ICON_SPACING))))[len(side) > 0], f"{("", f" {side}")[side != ""]}({downloads} téléchargements)", font = ImageFont.truetype(FONT_DIR + "\\" + TITLE_FONT, 25), fill = (0, 0, 0))
    image_drawing.text(DESCRIPTION_POSITION, summary, fill = (0, 0, 0), font = description_font)
    # Add mod avatar
    avatar = Image.open(BytesIO(requests.get(avatar_url).content)).resize(AVATAR_SIZE)
    if AVATAR_CORNER > 0:
        avatar = add_image_corner(avatar, AVATAR_CORNER)
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
        user_input = input("Veuillez saisir l'URL d'un mod CurseForge/Modrinth ou son slug: ").strip()
        try:
            if not user_input:
                continue
            if user_input.upper() == "EXIT":
                break
            elif "legacy.curseforge.com" in user_input:
                generate_curseforge_image((f"http://{user_input}", user_input)[user_input.startswith("http")].replace('legacy.curseforge.com', 'curseforge.com'))
            elif "curseforge.com" in user_input:
                generate_curseforge_image((f"http://{user_input}", user_input)[user_input.startswith("http")])
            elif "modrinth.com" in user_input:
                generate_modrinth_image(f"https://api.modrinth.com/v2/project/{(user_input.rsplit("/", 1)[-1], user_input.rsplit("/", 2)[-2])[user_input.endswith(("gallery", "changelog", "versions"))]}")
            elif re.search(r"[a-zA-Z0-9\-]+", user_input):
                try:
                    generate_curseforge_image(f"https://www.curseforge.com/minecraft/mc-mods/{user_input.lower()}")
                except (KeyError, IndexError, AttributeError, TypeError, requests.exceptions.MissingSchema, selenium.exceptions.WebDriverException) as error:
                    generate_modrinth_image(f"https://api.modrinth.com/v2/project/{user_input.lower()}")
            else:
                print("URL Invalide")
        except (KeyError, IndexError, JSONDecodeError) as error:
            print(f"URL Curseforge/Modrinth Invalide: {error.args}")
        except (AttributeError, TypeError, requests.exceptions.MissingSchema) as error:
            print(f"URL de mod CurseForge/Modrinth Invalide: {error.args}")
        except FileNotFoundError as error:
            print(f'Le fichier "{error.filename}" n\'existe pas')
        except selenium.exceptions.WebDriverException:
            print("Veuillez garder le navigateur ouvert")
            driver = webdriver.Firefox()
            driver.minimize_window()
    driver.close()