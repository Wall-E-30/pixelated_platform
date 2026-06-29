import os
import pygame

def inspect_image(path):
    if not os.path.exists(path):
        print(f"File {path} does not exist.")
        return
    
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    try:
        img = pygame.image.load(path).convert_alpha()
        w, h = img.get_size()
        print(f"Image {path}: width={w}, height={h}")
        
        # Connected component bounding boxes (using the logic from analyze_new_assets.py)
        mask = pygame.mask.from_surface(img)
        processed = pygame.mask.Mask((w, h))
        boxes = []
        for y in range(h):
            for x in range(w):
                if mask.get_at((x, y)) and not processed.get_at((x, y)):
                    component_mask = mask.connected_component((x, y))
                    processed.draw(component_mask, (0, 0))
                    rects = component_mask.get_bounding_rects()
                    if rects:
                        r = rects[0]
                        if r.width >= 5 and r.height >= 5:
                            boxes.append(r)
        
        print(f"Found {len(boxes)} bounding boxes:")
        for idx, box in enumerate(boxes):
            print(f"  Box {idx}: x={box.x}, y={box.y}, w={box.width}, h={box.height}")
    except Exception as e:
        print(f"Error inspecting {path}: {e}")

def main():
    paths = [
        "assets/Characters/Samurai.png",
        "assets/Enemies/Forest_Goblin.png",
        "assets/Enemies/Horned_Beast.png",
        "assets/Enemies/Slime.png"
    ]
    for p in paths:
        inspect_image(p)

if __name__ == "__main__":
    main()
