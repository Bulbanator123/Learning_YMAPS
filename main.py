import pygame
import os
from io import BytesIO
import requests
from PIL import Image
import sys

# -------Импорты--------

pygame.init()
clock = pygame.time.Clock()
width, height = 650, 650
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('CopyYandexMaps')
user_text = ' '
font = pygame.font.SysFont('Calibri', 32)  # Шрифт
input_rect = pygame.Rect(10, 10, 140, 40)  # Прямоугольник поля ввода
active = False
color_ac = pygame.Color('black')  # Цвет нажатого состояния
color_pc = pygame.Color('red')  # Цвет ненажатого состояния
color = color_pc
all_sprites = pygame.sprite.Group()
mapa_group = pygame.sprite.Group()
FPS = 60


class MAPA(pygame.sprite.Sprite):  # Класс карты
    def __init__(self, x, y, sprite):
        super().__init__(mapa_group, all_sprites)
        self.image = sprite
        self.rect = self.image.get_rect().move(x, y)

    def up_down(self, plus_or_minus):  # функция изменения масштаба
        x = self.rect.x
        y = self.rect.y
        self.image = pygame.transform.scale(load_image('mapa.jpg'),
                                            (self.rect.w + 10 * plus_or_minus, self.rect.h + 10 * plus_or_minus))
        self.rect = self.image.get_rect().move(x - 5 * plus_or_minus, y - 5 * plus_or_minus)


def map_search(user_text):  # Функция для нахождения места, введённого в поиске
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": user_text,
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


def load_image(name, colorkey=None):  # Функция для загрузки картинок
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


def terminate():  # Функция для завершения приложения
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    running = True
    mapa = None
    while running:
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                running = False

            if events.type == pygame.MOUSEBUTTONDOWN:  # Клавиша мыши нажата
                if input_rect.collidepoint(events.pos):
                    active = True
                else:
                    active = False
                if mapa:
                    if events.button == 4:
                        mapa.up_down(1)
                    elif events.button == 5:
                        mapa.up_down(-1)
            if events.type == pygame.KEYDOWN:  # Кнопка нажата
                if active is True:  # Поле ввода нажато
                    if events.key == pygame.K_RETURN:
                        for el in mapa_group:
                            mapa_group.remove(el)
                        map_search(user_text)
                        fon = pygame.transform.scale(load_image('mapa.jpg'), (width, height - 100))
                        mapa = MAPA(0, 100, fon)
                    elif events.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += events.unicode
                if mapa:
                    if events.key == pygame.K_PAGEUP:
                        mapa.up_down(1)
                    elif events.key == pygame.K_PAGEDOWN:
                        mapa.up_down(-1)
        screen.fill('white')
        mapa_group.draw(screen)
        if active:  # Изменение цвета ввода
            color = color_ac
        else:
            color = color_pc

        pygame.draw.rect(screen, color, input_rect, 2)

        text_surface = font.render(user_text, True, (0, 204, 204))
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        input_rect.w = max(100, text_surface.get_width() + 10)
        pygame.display.flip()
        clock.tick(FPS)
    terminate()
