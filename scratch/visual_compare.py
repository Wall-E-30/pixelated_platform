import os
import io
import subprocess
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
    os.makedirs("scratch/compare", exist_ok=True)
    
    bg_sheet = pygame.image.load("assets/Terrain/background_items.png").convert_alpha()
    collect_sheet = pygame.image.load("assets/Items/collectibles.png").convert_alpha()
    
    bg_boxes = get_boxes(bg_sheet)
    collect_boxes = get_boxes(collect_sheet)
    
    mapping_candidates = {
        "platform_grassy_dirt.png": (bg_sheet, [
            pygame.Rect(1421, 693, 368, 204),
            pygame.Rect(47, 575, 593, 651),
            pygame.Rect(646, 597, 386, 617),
        ]),
        "platform_stone_brick.png": (bg_sheet, [
            pygame.Rect(1842, 686, 282, 211),
            pygame.Rect(1074, 955, 280, 265),
            pygame.Rect(1426, 1043, 199, 171),
        ]),
        "platform_wood.png": (bg_sheet, [
            pygame.Rect(2171, 703, 164, 188),
            pygame.Rect(2371, 721, 146, 147),
            pygame.Rect(2558, 722, 217, 164),
        ]),
        "platform_rope_bridge.png": (bg_sheet, [
            pygame.Rect(1074, 955, 280, 265),
            pygame.Rect(1421, 693, 368, 204),
            pygame.Rect(1120, 1284, 277, 229),
        ]),
        "platform_mossy_stone.png": (bg_sheet, [
            pygame.Rect(1655, 1033, 170, 181),
            pygame.Rect(1866, 1032, 212, 182),
            pygame.Rect(2112, 1050, 200, 164),
        ]),
        "platform_mossy_rock.png": (bg_sheet, [
            pygame.Rect(1842, 686, 282, 211),
            pygame.Rect(1866, 1032, 212, 182),
            pygame.Rect(1421, 693, 368, 204),
        ]),
        "hazard_spikes.png": (bg_sheet, [
            pygame.Rect(663, 1325, 76, 64),
            pygame.Rect(1461, 1413, 46, 76),
        ]),
        "interactive_jump_pad.png": (bg_sheet, [
            pygame.Rect(1461, 1413, 46, 76),
            pygame.Rect(581, 1360, 53, 41),
        ]),
        "interactive_mushroom.png": (bg_sheet, [
            pygame.Rect(581, 1360, 53, 41),
            pygame.Rect(1461, 1413, 46, 76),
        ]),
        "decor_pine_trees.png": (bg_sheet, [
            pygame.Rect(2083, 24, 140, 281),
            pygame.Rect(2628, 24, 140, 281),
        ]),
        "decor_deciduous_tree.png": (bg_sheet, [
            pygame.Rect(2247, 100, 358, 206),
        ]),
        "decor_leafy_tree.png": (bg_sheet, [
            pygame.Rect(2247, 100, 358, 206),
        ]),
        "decor_fallen_log.png": (bg_sheet, [
            pygame.Rect(2622, 341, 135, 199),
        ]),
        "decor_stump_logs.png": (bg_sheet, [
            pygame.Rect(2622, 341, 135, 199),
        ]),
    }
    
    for filename, (sheet, rects) in mapping_candidates.items():
        try:
            data = subprocess.check_output(["git", "show", "HEAD:assets/Forest/" + filename])
            orig = pygame.image.load(io.BytesIO(data)).convert_alpha()
            ow, oh = orig.get_size()
            
            # Create a comparison surface
            comp_w = ow + 20 + sum(r.width + 10 for r in rects)
            comp_h = max(oh, max(r.height for r in rects)) + 40
            comp_surf = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA, 32)
            
            # Draw original
            comp_surf.blit(orig, (10, 20))
            
            # Draw labels
            font = pygame.font.SysFont("Arial", 12)
            lbl = font.render("Original", True, (255, 255, 255))
            comp_surf.blit(lbl, (10, 2))
            
            curr_x = ow + 30
            for i, r in enumerate(rects):
                sub = sheet.subsurface(r)
                comp_surf.blit(sub, (curr_x, 20))
                
                lbl = font.render(f"Cand {i}: {r.x},{r.y},{r.w},{r.h}", True, (255, 255, 255))
                comp_surf.blit(lbl, (curr_x, 2))
                
                curr_x += r.width + 15
                
            pygame.image.save(comp_surf, f"scratch/compare/{filename}")
            print(f"Saved comparison for {filename}")
        except Exception as e:
            print(f"Error {filename}: {e}")

if __name__ == "__main__":
    main()
