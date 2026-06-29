import os
import pygame

def find_candidate_boxes(sheet_img):
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
                    r = rects[0]
                    if r.width >= 10 and r.height >= 10:
                        boxes.append(r)
    return boxes

def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    os.makedirs("scratch/extracted_sprites", exist_ok=True)
    
    bg_sheet = pygame.image.load("assets/Terrain/background_items.png").convert_alpha()
    collect_sheet = pygame.image.load("assets/Items/collectibles.png").convert_alpha()
    
    bg_boxes = find_candidate_boxes(bg_sheet)
    collect_boxes = find_candidate_boxes(collect_sheet)
    
    # Sort boxes: first by y-level (in rows), then by x
    # We group boxes into rows if their y centers are within 30 pixels of each other
    def group_and_sort_boxes(boxes):
        if not boxes:
            return []
        # sort by y first
        boxes = sorted(boxes, key=lambda r: r.y)
        rows = []
        current_row = [boxes[0]]
        for b in boxes[1:]:
            if abs(b.centery - current_row[0].centery) < 40:
                current_row.append(b)
            else:
                rows.append(sorted(current_row, key=lambda r: r.x))
                current_row = [b]
        rows.append(sorted(current_row, key=lambda r: r.x))
        
        flat_list = []
        for r in rows:
            flat_list.extend(r)
        return flat_list

    bg_boxes = group_and_sort_boxes(bg_boxes)
    collect_boxes = group_and_sort_boxes(collect_boxes)
    
    html_content = """
    <html>
    <head>
        <title>Sprite Inspection Gallery</title>
        <style>
            body { font-family: sans-serif; background: #222; color: #fff; padding: 20px; }
            h2 { border-bottom: 2px solid #555; padding-bottom: 10px; margin-top: 40px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 15px; }
            .card { background: #333; border: 1px solid #444; border-radius: 8px; padding: 10px; text-align: center; }
            .img-container { background: #444; height: 160px; display: flex; align-items: center; justify-content: center; border-radius: 4px; overflow: hidden; margin-bottom: 8px; }
            img { max-width: 100%; max-height: 100%; object-fit: contain; }
            .meta { font-size: 12px; color: #ccc; line-height: 1.4; }
        </style>
    </head>
    <body>
        <h1>Consolidated Sprite Sheets Inspection Gallery</h1>
        
        <h2>Collectibles (from collectibles.png)</h2>
        <div class="grid">
    """
    
    # Save collectibles
    for idx, box in enumerate(collect_boxes):
        sub = collect_sheet.subsurface(box)
        fn = f"scratch/extracted_sprites/collectibles_sprite_{idx}.png"
        pygame.image.save(sub, fn)
        html_content += f"""
            <div class="card">
                <div class="img-container">
                    <img src="extracted_sprites/collectibles_sprite_{idx}.png">
                </div>
                <div class="meta">
                    <strong>Idx {idx}</strong><br>
                    x={box.x}, y={box.y}<br>
                    w={box.width}, h={box.height}
                </div>
            </div>
        """
        
    html_content += """
        </div>
        <h2>Background Items / Terrain (from background_items.png)</h2>
        <div class="grid">
    """
    
    # Save background items
    for idx, box in enumerate(bg_boxes):
        sub = bg_sheet.subsurface(box)
        fn = f"scratch/extracted_sprites/background_items_sprite_{idx}.png"
        pygame.image.save(sub, fn)
        html_content += f"""
            <div class="card">
                <div class="img-container">
                    <img src="extracted_sprites/background_items_sprite_{idx}.png">
                </div>
                <div class="meta">
                    <strong>Idx {idx}</strong><br>
                    x={box.x}, y={box.y}<br>
                    w={box.width}, h={box.height}
                </div>
            </div>
        """
        
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open("scratch/inspect_sprites.html", "w") as f:
        f.write(html_content)
        
    print(f"Extracted {len(collect_boxes)} collectibles and {len(bg_boxes)} background items.")

if __name__ == "__main__":
    main()
