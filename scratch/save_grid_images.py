import os
import pygame

def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    bg_sheet = pygame.image.load("assets/Terrain/background_items.png").convert_alpha()
    collect_sheet = pygame.image.load("assets/Items/collectibles.png").convert_alpha()
    
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
    
    bg_boxes = find_candidate_boxes(bg_sheet)
    collect_boxes = find_candidate_boxes(collect_sheet)
    
    # Sort boxes: first by y-level (in rows), then by x
    def group_and_sort_boxes(boxes):
        if not boxes:
            return []
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
    
    # Let's save a grid of collectibles
    # We will draw each collectible on a 150x150 cell with its index
    font = pygame.font.SysFont("Arial", 16)
    
    def create_grid(boxes, sheet, cols=6, cell_size=160):
        rows = (len(boxes) + cols - 1) // cols
        grid_surf = pygame.Surface((cols * cell_size, rows * cell_size), pygame.SRCALPHA, 32)
        grid_surf.fill((30, 30, 30, 255))
        
        for idx, box in enumerate(boxes):
            sub = sheet.subsurface(box)
            # Scale to fit cell (leaving margin)
            fit_size = cell_size - 40
            w, h = sub.get_size()
            scale = min(fit_size/w, fit_size/h)
            new_w, new_h = int(w * scale), int(h * scale)
            scaled = pygame.transform.scale(sub, (new_w, new_h))
            
            c = idx % cols
            r = idx // cols
            cx = c * cell_size
            cy = r * cell_size
            
            # Draw cell background border
            pygame.draw.rect(grid_surf, (60, 60, 60), (cx, cy, cell_size, cell_size), 1)
            
            # Center the image
            ix = cx + (cell_size - new_w) // 2
            iy = cy + (cell_size - new_h) // 2 - 10
            grid_surf.blit(scaled, (ix, iy))
            
            # Draw label
            lbl = font.render(f"Idx {idx}", True, (255, 255, 0))
            grid_surf.blit(lbl, (cx + 5, cy + 5))
            
            coords = font.render(f"{box.x},{box.y}", True, (200, 200, 200))
            grid_surf.blit(coords, (cx + 5, cy + cell_size - 36))
            
            size_lbl = font.render(f"{box.w}x{box.h}", True, (150, 150, 255))
            grid_surf.blit(size_lbl, (cx + 5, cy + cell_size - 20))
            
        return grid_surf

    collect_grid = create_grid(collect_boxes, collect_sheet, cols=4)
    # Save to App Data directory
    app_data_dir = "C:/Users/tilak/.gemini/antigravity/brain/2433dc1e-2032-4c4c-91eb-8e50b2b77a1f"
    pygame.image.save(collect_grid, f"{app_data_dir}/collectibles_page.png")
    
    # background_items has 81 boxes, we can save them in 3 pages of 30, 30, 21
    bg_p1 = create_grid(bg_boxes[:30], bg_sheet, cols=6)
    bg_p2 = create_grid(bg_boxes[30:60], bg_sheet, cols=6)
    bg_p3 = create_grid(bg_boxes[60:], bg_sheet, cols=6)
    
    pygame.image.save(bg_p1, f"{app_data_dir}/bg_items_part1.png")
    pygame.image.save(bg_p2, f"{app_data_dir}/bg_items_part2.png")
    pygame.image.save(bg_p3, f"{app_data_dir}/bg_items_part3.png")
    
    print("Grid images saved successfully.")

if __name__ == "__main__":
    main()
