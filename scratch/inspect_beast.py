import pygame
import os

def inspect_beast():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    path = "assets/Enemies/Horned_Beast.png"
    if not os.path.exists(path):
        print("Not found")
        return
    img = pygame.image.load(path)
    print("Format:", img.get_flags())
    print("Has alpha:", img.get_alpha() is not None)
    
    # Check pixels at corners or edges
    w, h = img.get_size()
    corners = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, h//2)]
    for pt in corners:
        color = img.get_at(pt)
        print(f"Pixel at {pt}: {color}")

if __name__ == "__main__":
    inspect_beast()
