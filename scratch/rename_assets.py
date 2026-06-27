import os

def rename_assets():
    renames = {
        # Characters
        "assets/Characters/Copilot_20260626_212906.png": "assets/Characters/player_spritesheet.png",
        "assets/Characters/Copilot_20260627_190742.png": "assets/Characters/character_illustration_1.png",
        "assets/Characters/Copilot_20260627_190916.png": "assets/Characters/character_illustration_2.png",
        
        # Enemies
        "assets/Enemies/Copilot_20260626_213137.png": "assets/Enemies/enemy_slime_spritesheet.png",
        "assets/Enemies/Copilot_20260626_221829 (1).png": "assets/Enemies/enemy_slime_leap.png",
        
        # Forest / Terrain / Hazards / Decors
        "assets/Forest/Copilot_20260624_225834 (1).png": "assets/Forest/platform_grass_soil.png",
        "assets/Forest/Copilot_20260624_225834 (11).png": "assets/Forest/platform_mossy_stone.png",
        "assets/Forest/Copilot_20260624_225834 (2).png": "assets/Forest/platform_rope_bridge.png",
        "assets/Forest/Copilot_20260624_225834 (21).png": "assets/Forest/platform_stone_brick.png",
        "assets/Forest/Copilot_20260624_225834 (23).png": "assets/Forest/platform_wood.png",
        "assets/Forest/Copilot_20260624_225834 (24).png": "assets/Forest/hazard_spikes.png",
        "assets/Forest/Copilot_20260624_225856 (1).png": "assets/Forest/platform_grassy_dirt.png",
        "assets/Forest/Copilot_20260624_225856 (4).png": "assets/Forest/platform_mossy_rock.png",
        "assets/Forest/Copilot_20260624_230649 (1).png": "assets/Forest/decor_pine_trees.png",
        "assets/Forest/Copilot_20260624_230649 (2).png": "assets/Forest/decor_deciduous_tree.png",
        "assets/Forest/Copilot_20260624_230649 (3).png": "assets/Forest/decor_leafy_tree.png",
        "assets/Forest/Copilot_20260624_230649 (4).png": "assets/Forest/decor_fallen_log.png",
        "assets/Forest/Copilot_20260624_230649 (5).png": "assets/Forest/decor_stump_logs.png"
    }
    
    for old, new in renames.items():
        if os.path.exists(old):
            try:
                os.rename(old, new)
                print(f"Renamed: {old} -> {new}")
            except Exception as e:
                print(f"Failed renaming {old} to {new}: {e}")
        else:
            print(f"File not found: {old} (might already be renamed)")

if __name__ == "__main__":
    rename_assets()
