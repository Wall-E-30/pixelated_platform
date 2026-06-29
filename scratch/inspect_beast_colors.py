import pygame
import os
from collections import Counter

def inspect_beast_colors():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    path = "assets/Enemies/Horned_Beast.png"
    if not os.path.exists(path):
        print("Not found")
        return
    img = pygame.image.load(path)
    w, h = img.get_size()
    
    # Let's count colors of pixels along the top border
    colors = []
    for x in range(w):
        colors.append(img.get_at((x, 0))[:3])
        colors.append(img.get_at((x, h-1))[:3])
    for y in range(h):
        colors.append(img.get_at((0, y))[:3])
        colors.append(img.get_at((w-1, y))[:3])
        
    counter = Counter(colors)
    print("Most common border colors:")
    for color, count in counter.most_common(10):
        print(f"  Color {color}: {count} pixels")

if __name__ == "__main__":
    inspect_beast_colors()
