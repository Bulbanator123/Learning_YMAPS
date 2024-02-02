import pygame
import os
from io import BytesIO
import requests
from PIL import Image

pygame.init()
clock = pygame.time.Clock()
width, height = 650, 650
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('CopyYandexMaps')
user_text = ' '
font = pygame.font.SysFont('frenchscript', 32)
input_rect = pygame.Rect(10, 10, 140, 40)
active = False
color_ac = pygame.Color('black')
color_pc = pygame.Color('red')
color = color_pc
all_sprites = pygame.sprite.Group()
mapagroup = pygame.sprite.Group()
active = False


class JPG(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        super().__init__(mapagroup, all_sprites)
        self.image = sprite
        self.rect = self.image.get_rect().move(x, y)


def map_search(user_text):
    toponim = user_text
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponim,
        "format": "json"
    }

    response = requests.get(geocoder_api_server, params=params)
    if not response:
        pass
    else:
        json_response = response.json()
        coords = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        lon, lat = coords.split(" ")
        delta = "0.005"
        map_params = {
            "ll": ",".join([lon, lat]),
            "spn": ",".join([delta, delta]),
            "l": "sat"
        }
        api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(api_server, params=map_params)
        image = Image.open(BytesIO(response.content))
        image.save("data/mapa.jpg")


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f'Файл с изображением "{fullname}" не найден')
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


while True:
    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            pygame.quit()

        if events.type == pygame.MOUSEBUTTONDOWN:
            if input_rect.collidepoint(events.pos):
                active = True
            else:
                active = False

        if events.type == pygame.KEYDOWN:
            if active is True:
                if events.key == pygame.K_RETURN:
                    map_search(user_text)
                    fon = pygame.transform.scale(load_image('mapa.jpg'), (width, height - 100))
                    JPG(0, 100, fon)
                elif events.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += events.unicode
    screen.fill('white')
    mapagroup.draw(screen)
    all_sprites.draw(screen)
    if active:
        color = color_ac
    else:
        color = color_pc

    pygame.draw.rect(screen, color, input_rect, 2)

    text_surface = font.render(user_text, True, (0, 204, 204))
    screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
    input_rect.w = max(100, text_surface.get_width() + 10)
    pygame.display.flip()
    clock.tick(60)
