import os
import pygame

def find_beast_layout():
    path = "assets/Enemies/Horned_Beast.png"
    if not os.path.exists(path):
        print(f"File {path} does not exist.")
        return
    
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    try:
        surface = pygame.image.load(path).convert_alpha()
        width, height = surface.get_size()
        
        # Create a new surface where background grey (approx 51, 51, 51) is transparent
        processed_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(height):
            for x in range(width):
                r, g, b, a = surface.get_at((x, y))
                # Check if it is near the background grey color
                if abs(r - 51) < 8 and abs(g - 51) < 8 and abs(b - 51) < 8:
                    processed_surface.set_at((x, y), (0, 0, 0, 0))
                else:
                    processed_surface.set_at((x, y), (r, g, b, a))
        
        mask = pygame.mask.from_surface(processed_surface)
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
                        if r.width >= 50 and r.height >= 50:
                            boxes.append(r)
                            
        # Sort boxes by y first, then x
        boxes.sort(key=lambda b: (b.y // 50, b.x))
        
        print(f"\n=========================================")
        print(f"LAYOUT FOR Horned Beast (assets/Enemies/Horned_Beast.png) - size: {width}x{height}")
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
        print(f"Error processing Horned Beast: {e}")

if __name__ == "__main__":
    find_beast_layout()
