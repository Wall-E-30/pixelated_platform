import os
import pygame

def print_image_info(path):
    if not os.path.exists(path):
        print(f"File {path} does not exist.")
        return
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    print(f"{path}: {w}x{h}")

def main():
    paths = [
        "assets/Characters/Samurai.png",
        "assets/Enemies/Forest_Goblin.png",
        "assets/Enemies/Horned_Beast.png",
        "assets/Enemies/Slime.png"
    ]
    for p in paths:
        print_image_info(p)

if __name__ == "__main__":
    main()
