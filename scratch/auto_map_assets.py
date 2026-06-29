import os
import io
import subprocess
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
                    boxes.append(rects[0])
    return boxes

def get_best_match(original_img, boxes, sheet_img):
    ow, oh = original_img.get_size()
    candidates = []
    
    for box in boxes:
        # Distance metric based on size difference
        size_diff = abs(box.width - ow) + abs(box.height - oh)
        # Allow some scaling discrepancy
        if size_diff < 150:
            candidates.append((size_diff, box))
            
    if not candidates:
        # If no close match, look at aspect ratio
        orig_ratio = ow / oh
        for box in boxes:
            box_ratio = box.width / box.height
            ratio_diff = abs(box_ratio - orig_ratio)
            if ratio_diff < 0.15:
                # Add with a penalty
                candidates.append((int(ratio_diff * 1000) + 150, box))
                
    candidates.sort(key=lambda x: x[0])
    
    # Compare the top candidate boxes using sampled pixels
    best_box = None
    best_score = -1
    
    for diff, box in candidates[:5]:
        box_surface = sheet_img.subsurface(box)
        scaled_orig = pygame.transform.scale(original_img, (box.width, box.height))
        
        # Sample a 10x10 grid of pixels
        match_count = 0
        total_samples = 0
        for gx in range(0, box.width, max(1, box.width // 10)):
            for gy in range(0, box.height, max(1, box.height // 10)):
                c1 = scaled_orig.get_at((gx, gy))
                c2 = box_surface.get_at((gx, gy))
                
                # Check color difference
                if c1[3] > 10 and c2[3] > 10:
                    dist = abs(c1[0]-c2[0]) + abs(c1[1]-c2[1]) + abs(c1[2]-c2[2])
                    if dist < 45:
                        match_count += 1
                    total_samples += 1
                elif c1[3] <= 10 and c2[3] <= 10:
                    match_count += 1
                    total_samples += 1
                else:
                    total_samples += 1
                    
        score = match_count / total_samples if total_samples > 0 else 0
        if score > best_score:
            best_score = score
            best_box = box
            
    return best_box, best_score

def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    bg_sheet = pygame.image.load("assets/Terrain/background_items.png").convert_alpha()
    collect_sheet = pygame.image.load("assets/Items/collectibles.png").convert_alpha()
    
    print("Finding bounding boxes in sheets...")
    bg_boxes = find_candidate_boxes(bg_sheet)
    collect_boxes = find_candidate_boxes(collect_sheet)
    print(f"Found {len(bg_boxes)} boxes in background_items and {len(collect_boxes)} boxes in collectibles.")
    
    assets = [
        "platform_grassy_dirt.png",
        "platform_stone_brick.png",
        "platform_wood.png",
        "platform_rope_bridge.png",
        "platform_mossy_stone.png",
        "platform_mossy_rock.png",
        "hazard_spikes.png",
        "interactive_jump_pad.png",
        "interactive_mushroom.png",
        "decor_pine_trees.png",
        "decor_deciduous_tree.png",
        "decor_leafy_tree.png",
        "decor_fallen_log.png",
        "decor_stump_logs.png",
        "ui_heart.png",
        "item_coin.png",
        "item_chest.png",
    ]
    
    print("\nMapping results:")
    for a in assets:
        path = "assets/Forest/" + a
        try:
            data = subprocess.check_output(["git", "show", "HEAD:" + path])
            orig_img = pygame.image.load(io.BytesIO(data)).convert_alpha()
            
            match_bg_box, score_bg = get_best_match(orig_img, bg_boxes, bg_sheet)
            match_col_box, score_col = get_best_match(orig_img, collect_boxes, collect_sheet)
            
            if score_bg >= score_col and score_bg > 0.4:
                print(f"'{a}': ('background_items', ({match_bg_box.x}, {match_bg_box.y}, {match_bg_box.width}, {match_bg_box.height})),  # score={score_bg:.2f}")
            elif score_col > 0.4:
                print(f"'{a}': ('collectibles', ({match_col_box.x}, {match_col_box.y}, {match_col_box.width}, {match_col_box.height})),  # score={score_col:.2f}")
            else:
                # Print best effort even if low score
                if score_bg >= score_col:
                    print(f"'{a}': ('background_items', ({match_bg_box.x}, {match_bg_box.y}, {match_bg_box.width}, {match_bg_box.height})) [LOW SCORE={score_bg:.2f}]")
                else:
                    print(f"'{a}': ('collectibles', ({match_col_box.x}, {match_col_box.y}, {match_col_box.width}, {match_col_box.height})) [LOW SCORE={score_col:.2f}]")
        except Exception as e:
            print(f"Error mapping {a}: {e}")

if __name__ == "__main__":
    main()
