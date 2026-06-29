import os
import io
import subprocess
import pygame

def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    os.makedirs("scratch/originals", exist_ok=True)
    
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
    
    for a in assets:
        path = "assets/Forest/" + a
        try:
            data = subprocess.check_output(["git", "show", "HEAD:" + path])
            img = pygame.image.load(io.BytesIO(data)).convert_alpha()
            pygame.image.save(img, f"scratch/originals/{a}")
            print(f"Extracted original {a}: size={img.get_size()}")
        except Exception as e:
            print(f"Error extracting {a}: {e}")

if __name__ == "__main__":
    main()
