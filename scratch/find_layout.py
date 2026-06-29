import os
import pygame

def find_sprite_layout(name, path, min_w=40, min_h=40):
    if not os.path.exists(path):
        print(f"File {path} does not exist.")
        return
    
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    try:
        surface = pygame.image.load(path).convert_alpha()
        width, height = surface.get_size()
        
        mask = pygame.mask.from_surface(surface)
        processed = pygame.mask.Mask((width, height))
        
        boxes = []
        for y in range(height):
            for x in range(width):
                if mask.get_at((x, y)) and not processed.get_at((x, y)):
                    component_mask = mask.connected_component((x, y))
                    processed.draw(component_mask, (0, 0))
                    rects = component_mask.get_bounding_rects()
                    if rects:
                        r = rects[0]
                        if r.width >= min_w and r.height >= min_h:
                            boxes.append(r)
                            
        # Sort boxes by y first, then x
        boxes.sort(key=lambda b: (b.y // 50, b.x))  # group by approximate rows (within 50px)
        
        print(f"\n=========================================")
        print(f"LAYOUT FOR {name} ({path}) - size: {width}x{height}")
        print(f"Found {len(boxes)} large sprite boxes:")
        
        rows = {}
        for b in boxes:
            row_id = b.y // 50
            if row_id not in rows:
                rows[row_id] = []
            rows[row_id].append(b)
            
        for rid in sorted(rows.keys()):
            row_boxes = sorted(rows[rid], key=lambda b: b.x)
            print(f"  Row Y ~ {rid * 50}:")
            for i, box in enumerate(row_boxes):
                print(f"    Index {i}: Rect({box.x}, {box.y}, {box.width}, {box.height})")
                
    except Exception as e:
        print(f"Error processing {path}: {e}")

def main():
    find_sprite_layout("Samurai", "assets/Characters/Samurai.png", min_w=60, min_h=60)
    find_sprite_layout("Forest Goblin", "assets/Enemies/Forest_Goblin.png", min_w=50, min_h=50)
    find_sprite_layout("Horned Beast", "assets/Enemies/Horned_Beast.png", min_w=60, min_h=60)
    find_sprite_layout("Slime", "assets/Enemies/Slime.png", min_w=40, min_h=40)

if __name__ == "__main__":
    main()
