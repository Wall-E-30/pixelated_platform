import os
import pygame

def get_boxes(sheet_img):
    sw, sh = sheet_img.get_size()
    mask = pygame.mask.from_surface(sheet_img)
    processed = pygame.mask.Mask((sw, sh))
    boxes = []
    for y in range(sh):
        for x in range(sw):
            if mask.get_at((x, y)) and not processed.get_at((x, y)):
                component_mask = mask.connected_component((x, y))
                processed.draw(component_mask, (0, 0))
                rects = component_mask.get_bounding_rects()
                if rects:
                    boxes.append(rects[0])
    return boxes

def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    orig = pygame.image.load("scratch/originals/item_chest.png").convert_alpha()
    ow, oh = orig.get_size()
    
    bg_sheet = pygame.image.load("assets/Terrain/background_items.png").convert_alpha()
    collect_sheet = pygame.image.load("assets/Items/collectibles.png").convert_alpha()
    
    print("Searching in background_items...")
    bg_boxes = get_boxes(bg_sheet)
    for b in bg_boxes:
        if abs(b.width - ow) < 50 and abs(b.height - oh) < 50:
            print(f"Found size match in background_items: {b}")
            
    print("Searching in collectibles...")
    collect_boxes = get_boxes(collect_sheet)
    for b in collect_boxes:
        if abs(b.width - ow) < 50 and abs(b.height - oh) < 50:
            print(f"Found size match in collectibles: {b}")

if __name__ == "__main__":
    main()
