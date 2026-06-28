import os

def rename_assets():
    renames = {
        # Enemies
        "assets/Enemies/Copilot_20260628_094646.png": "assets/Enemies/goblin_spritesheet.png",
        "assets/Enemies/Copilot_20260628_094708.png": "assets/Enemies/golem_spritesheet.png",
        "assets/Enemies/Copilot_20260628_095324.png": "assets/Enemies/leaf_goblin_spritesheet.png",
        "assets/Enemies/Copilot_20260628_095423 (1).png": "assets/Enemies/goblin_spear.png",
        "assets/Enemies/Copilot_20260628_100026.png": "assets/Enemies/root_golem_spritesheet.png",
        
        # Forest Items / HUD
        "assets/Forest/Copilot_20260628_094414 (17).png": "assets/Forest/ui_heart.png",
        "assets/Forest/Copilot_20260628_094414 (15).png": "assets/Forest/item_coin.png",
        "assets/Forest/Copilot_20260628_094414 (16).png": "assets/Forest/item_star.png",
        "assets/Forest/Copilot_20260628_094414 (18).png": "assets/Forest/item_potion.png",
        "assets/Forest/Copilot_20260628_094414 (19).png": "assets/Forest/item_ring.png",
        "assets/Forest/Copilot_20260628_094414 (23).png": "assets/Forest/item_chest.png",
        
        # Forest Interactive Objects
        "assets/Forest/Copilot_20260628_094414 (20).png": "assets/Forest/decor_checkpoint_flag.png",
        "assets/Forest/Copilot_20260628_094414 (7).png": "assets/Forest/interactive_jump_pad.png",
        "assets/Forest/Copilot_20260628_094414 (6).png": "assets/Forest/interactive_mushroom.png",
        "assets/Forest/Copilot_20260628_094414 (8).png": "assets/Forest/interactive_crate_1.png",
        "assets/Forest/Copilot_20260628_094414 (9).png": "assets/Forest/interactive_crate_2.png",
        "assets/Forest/Copilot_20260628_094414 (14).png": "assets/Forest/hazard_spike_barrier.png",
        
        # Forest Terrain
        "assets/Forest/Copilot_20260628_094414 (1).png": "assets/Forest/platform_grassy_dirt_alt.png",
        "assets/Forest/Copilot_20260628_094414 (3).png": "assets/Forest/platform_stone_alt.png",
        "assets/Forest/Copilot_20260628_094414 (12).png": "assets/Forest/platform_dark_rock_alt.png",
        "assets/Forest/Copilot_20260628_094414 (21).png": "assets/Forest/platform_floating_island_alt.png",
        
        # Forest Decor
        "assets/Forest/Copilot_20260628_094414 (10).png": "assets/Forest/decor_bush_green.png",
        "assets/Forest/Copilot_20260628_094414 (22).png": "assets/Forest/decor_bush_flowers.png",
        "assets/Forest/Copilot_20260628_094414 (11).png": "assets/Forest/decor_log_stump_alt.png",
        "assets/Forest/Copilot_20260628_094414 (5).png": "assets/Forest/decor_log_stump_mossy.png",
        "assets/Forest/Copilot_20260628_094414 (4).png": "assets/Forest/decor_oak_tree_island.png",
    }
    
    for src, dst in renames.items():
        if os.path.exists(src):
            try:
                os.rename(src, dst)
                print(f"Renamed: {src} -> {dst}")
            except Exception as e:
                print(f"Error renaming {src}: {e}")
        else:
            print(f"Skipping (not found): {src}")

if __name__ == "__main__":
    rename_assets()
