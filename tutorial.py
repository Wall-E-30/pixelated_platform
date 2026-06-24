import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("pixelated platform")

BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))   #debug 1: Use 2 set of parantheses, because it take only one value, we are passing it as a tuple

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image):
    for tile in background:
        window.blit(bg_image, tile)

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        draw(window, background, bg_image)
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)