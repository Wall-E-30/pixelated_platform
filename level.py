import pygame
from environment import Platform, Hazard, Decoration, CollectibleItem, InteractiveObject
from entities import (
    SlimeEnemy, ForestGoblinEnemy, HornedBeastEnemy,
    DesertAutomatonEnemy, DesertAxeGolemEnemy, DesertHammerGolemEnemy
)

class Level:
    def __init__(self, width, height, theme="forest"):
        self.width = width
        self.height = height
        self.theme = theme
        
        # Level configurations
        self.player_spawn_x = 100
        self.player_spawn_y = 400
        self.background_name = "background.jpg"  # Default tiling background
        self.finish_x = 3200 # Reaching this X position triggers victory
        
        # Entity / Sprite lists
        self.platforms = []
        self.hazards = []
        self.decorations = []
        self.enemies = []
        self.collectibles = []
        self.interactive_objects = []
        self.checkpoints = []
        
        self.setup_level()

    def setup_level(self):
        import random
        from assets_manager import AssetsManager
        assets = AssetsManager()
        
        # Theme-specific asset keys and enemy classes
        if self.theme == "desert":
            asset_dirt = "platform_sand_top.png"
            asset_brick = "platform_desert_stone.png"
            asset_wood = "platform_desert_wood.png"
            asset_bridge = "platform_desert_bridge.png"
            asset_spikes = "hazard_cactus.png"
            
            # Decorations
            asset_tree_1 = "decor_cactus_1.png"
            asset_tree_2 = "decor_cactus_2.png"
            asset_log_1 = "decor_desert_ruin_1.png"
            asset_log_2 = "decor_desert_ruin_2.png"
            
            # Enemy classes
            EnemySmall = DesertAutomatonEnemy
            EnemyMedium = DesertAxeGolemEnemy
            EnemyLarge = DesertHammerGolemEnemy
        else:
            asset_dirt = "platform_grassy_dirt.png"
            asset_brick = "platform_stone_brick.png"
            asset_wood = "platform_wood.png"
            asset_bridge = "platform_rope_bridge.png"
            asset_spikes = "hazard_spikes.png"
            
            # Decorations
            asset_tree_1 = "decor_pine_trees.png"
            asset_tree_2 = "decor_deciduous_tree.png"
            asset_log_1 = "decor_fallen_log.png"
            asset_log_2 = "decor_stump_logs.png"
            
            # Enemy classes
            EnemySmall = SlimeEnemy
            EnemyMedium = ForestGoblinEnemy
            EnemyLarge = HornedBeastEnemy
            
        # Retrieve platform widths and heights dynamically
        w_dirt = assets.load_platform_image(asset_dirt).get_width()
        h_dirt = assets.load_platform_image(asset_dirt).get_height()
        w_bridge = assets.load_platform_image(asset_bridge).get_width()
        
        # Base Y position for ground platforms
        # Keep 15 pixels of overlap/sink for visual seamlessness
        ground_y = 800 - h_dirt + 15
        self.ground_y = ground_y
        
        # 1. Background decorations (placed globally across the whole generated level width)
        total_width = 6500
        
        # Spatially distribute background cactus/trees
        for x in range(150, total_width - 300, 800):
            self.decorations.append(Decoration(x, None, asset_tree_1, parallax_factor=0.3, align_bottom=ground_y + 10))
        for x in range(500, total_width - 300, 800):
            self.decorations.append(Decoration(x, None, asset_tree_2, parallax_factor=0.4, align_bottom=ground_y + 10))
        if self.theme != "desert":
            for x in range(300, total_width - 300, 900):
                self.decorations.append(Decoration(x, None, "decor_leafy_tree.png", parallax_factor=0.7, align_bottom=ground_y + 10))
            
        # 2. Foreground decorations (drawn behind entities)
        for x in range(750, total_width - 500, 1200):
            self.decorations.append(Decoration(x, None, asset_log_1, parallax_factor=1.0, align_bottom=ground_y + 20))
            self.decorations.append(Decoration(x + 250, None, asset_log_2, parallax_factor=1.0, align_bottom=ground_y + 10))
            
        # 3. Start Chunk (0 to 500)
        self.platforms.extend([
            Platform(0, ground_y, asset_dirt),
            Platform(w_dirt, ground_y, asset_dirt)
        ])
        # Start patrol small enemy
        self.enemies.append(EnemySmall(random.randint(250, 420), ground_y - 64, patrol_dist=60))
        
        # 4. Generate randomized middle chunks
        chunk_width = 800
        current_x = 500
        
        # Define the chunk generation functions to choose from
        def generate_flat_chunk(base_x):
            # Ground
            self.platforms.extend([
                Platform(base_x, ground_y, asset_dirt),
                Platform(base_x + w_dirt, ground_y, asset_dirt),
                Platform(base_x + 2 * w_dirt, ground_y, asset_brick)
            ])
            # High wood platform
            self.platforms.append(Platform(base_x + 250, ground_y - 190, asset_wood))
            # Coins
            self.collectibles.extend([
                CollectibleItem(base_x + 300, ground_y - 260, "coin"),
                CollectibleItem(base_x + 360, ground_y - 260, "coin")
            ])
            # Enemies
            self.enemies.append(EnemySmall(base_x + random.randint(100, 450), ground_y - 64, patrol_dist=80))

        def generate_spike_gap_chunk(base_x):
            # Ground blocks with a gap
            gap_start = base_x + w_dirt
            gap_width = 170
            self.platforms.extend([
                Platform(base_x, ground_y, asset_dirt),
                Platform(gap_start + gap_width, ground_y, asset_dirt)
            ])
            # Spikes in the gap
            self.hazards.append(Hazard(gap_start + 20, ground_y + 30, asset_spikes))
            # Bouncy element inside the gap to bounce out
            self.interactive_objects.append(InteractiveObject(gap_start + 60, ground_y + 10, "mushroom", theme=self.theme))
            # Floating wood platform over the gap
            self.platforms.append(Platform(gap_start - 20, ground_y - 180, asset_wood))
            # Coins above wood platform
            self.collectibles.extend([
                CollectibleItem(gap_start + 10, ground_y - 250, "coin"),
                CollectibleItem(gap_start + 70, ground_y - 250, "coin")
            ])
            # Medium enemy on the wood platform
            enemy_y = ground_y - 180 - (80 if self.theme == "desert" else 72)
            self.enemies.append(EnemyMedium(gap_start + 10, enemy_y, patrol_dist=30))

        def generate_bridge_climb_chunk(base_x):
            # Ground with a rope bridge gap
            self.platforms.extend([
                Platform(base_x, ground_y, asset_dirt),
                Platform(base_x + w_dirt, ground_y, asset_bridge),
                Platform(base_x + w_dirt + w_bridge, ground_y, asset_dirt)
            ])
            # Floating wood and stone platforms
            self.platforms.extend([
                Platform(base_x + 180, ground_y - 180, asset_wood),
                Platform(base_x + w_dirt + 120, ground_y - 260, asset_brick)
            ])
            # Coins
            self.collectibles.extend([
                CollectibleItem(base_x + 230, ground_y - 240, "coin"),
                CollectibleItem(base_x + w_dirt + 170, ground_y - 320, "coin")
            ])
            # Medium enemy on high stone
            enemy_y = ground_y - 260 - (80 if self.theme == "desert" else 72)
            self.enemies.append(EnemyMedium(base_x + w_dirt + 150, enemy_y, patrol_dist=30))
            # Small enemy on floor
            self.enemies.append(EnemySmall(base_x + 100, ground_y - 64, patrol_dist=60))

        def generate_boss_arena_chunk(base_x):
            # Ground
            self.platforms.extend([
                Platform(base_x, ground_y, asset_dirt),
                Platform(base_x + w_dirt + 160, ground_y, asset_dirt)
            ])
            # Raised barrier in the middle
            if self.theme == "desert":
                self.platforms.append(Platform(base_x + w_dirt - 30, ground_y - 64, asset_brick))
                barrier_h = 64
            else:
                h_rock = assets.load_platform_image("platform_mossy_rock.png").get_height()
                self.platforms.append(Platform(base_x + w_dirt - 30, ground_y - h_rock + 25, "platform_mossy_rock.png"))
                barrier_h = h_rock - 25
                
            # Jump pad to vault over the barrier
            self.interactive_objects.append(InteractiveObject(base_x + 120, ground_y - 48, "jump_pad", theme=self.theme))
            # Coins above barrier
            self.collectibles.extend([
                CollectibleItem(base_x + w_dirt, ground_y - barrier_h - 30, "coin"),
                CollectibleItem(base_x + w_dirt + 60, ground_y - barrier_h - 30, "coin")
            ])
            # Boss Mini-Boss guarding the other side
            boss_y = ground_y - 120
            self.enemies.append(EnemyLarge(base_x + w_dirt + 240, boss_y))

        # Randomly choose and construct 6 middle chunks
        chunk_generators = [
            generate_flat_chunk, 
            generate_spike_gap_chunk, 
            generate_bridge_climb_chunk, 
            generate_boss_arena_chunk
        ]
        
        # Ensure we get a good variety of different middle chunks
        chosen_generators = [random.choice(chunk_generators) for _ in range(6)]
        
        from environment import Checkpoint
        
        for idx, generator in enumerate(chosen_generators):
            generator(current_x)
            current_x += chunk_width
            
            # Place a checkpoint flag after chunk 2 (index 1) and chunk 4 (index 3)
            if idx in [1, 3]:
                # Place a flat ground platform for the checkpoint to stand safely on
                self.platforms.append(Platform(current_x, ground_y, asset_dirt))
                self.checkpoints.append(Checkpoint(current_x + 100, ground_y - 54))
                current_x += w_dirt
            
        # 5. End Chunk (starting at current_x)
        self.platforms.extend([
            Platform(current_x, ground_y, asset_dirt),
            Platform(current_x + w_dirt, ground_y, asset_dirt)
        ])
        # Treasure chest
        self.collectibles.append(CollectibleItem(current_x + 200, ground_y - 48, "chest"))
        # Final small enemy guarding chest
        self.enemies.append(EnemySmall(current_x + 50, ground_y - 64, patrol_dist=50))
        
        self.finish_x = current_x + 200
