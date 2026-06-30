import pygame
from environment import Platform, Hazard, Decoration, CollectibleItem, InteractiveObject
from entities import SlimeEnemy, ForestGoblinEnemy, HornedBeastEnemy

class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Level configurations
        self.player_spawn_x = 100
        self.player_spawn_y = 400
        self.background_name = "Green.png"  # Default tiling background
        self.finish_x = 3200 # Reaching this X position triggers victory
        
        # Entity / Sprite lists
        self.platforms = []
        self.hazards = []
        self.decorations = []
        self.enemies = []
        self.collectibles = []
        self.interactive_objects = []
        
        self.setup_level()

    def setup_level(self):
        import random
        from assets_manager import AssetsManager
        assets = AssetsManager()
        
        # Retrieve platform widths and heights dynamically
        w_dirt = assets.load_platform_image("platform_grassy_dirt.png").get_width()
        h_dirt = assets.load_platform_image("platform_grassy_dirt.png").get_height()
        w_bridge = assets.load_platform_image("platform_rope_bridge.png").get_width()
        
        # Base Y position for ground platforms
        # Keep 15 pixels of overlap/sink for visual seamlessness
        ground_y = 800 - h_dirt + 15
        
        # 1. Background decorations (placed globally across the whole generated level width)
        # Total Level Width = Start Chunk (500) + 3 Middle Chunks (3 * 800 = 2400) + End Chunk (500) = 3400
        total_width = 3400
        
        # Spatially distribute background pine trees, deciduous trees, and leafy trees
        for x in range(150, total_width - 300, 800):
            self.decorations.append(Decoration(x, None, "decor_pine_trees.png", parallax_factor=0.3, align_bottom=ground_y + 10))
        for x in range(500, total_width - 300, 800):
            self.decorations.append(Decoration(x, None, "decor_deciduous_tree.png", parallax_factor=0.4, align_bottom=ground_y + 10))
        for x in range(300, total_width - 300, 900):
            self.decorations.append(Decoration(x, None, "decor_leafy_tree.png", parallax_factor=0.7, align_bottom=ground_y + 10))
            
        # 2. Foreground decorations (drawn behind entities)
        for x in range(750, total_width - 500, 1200):
            self.decorations.append(Decoration(x, None, "decor_fallen_log.png", parallax_factor=1.0, align_bottom=ground_y + 20))
            self.decorations.append(Decoration(x + 250, None, "decor_stump_logs.png", parallax_factor=1.0, align_bottom=ground_y + 10))
            
        # 3. Start Chunk (0 to 500)
        self.platforms.extend([
            Platform(0, ground_y, "platform_grassy_dirt.png"),
            Platform(w_dirt, ground_y, "platform_grassy_dirt.png")
        ])
        # Start patrol slime
        self.enemies.append(SlimeEnemy(random.randint(250, 420), ground_y - 64, patrol_dist=60))
        
        # 4. Generate 3 randomized middle chunks
        chunk_width = 800
        current_x = 500
        
        # Define the chunk generation functions to choose from
        def generate_flat_chunk(base_x):
            # Ground
            self.platforms.extend([
                Platform(base_x, ground_y, "platform_grassy_dirt.png"),
                Platform(base_x + w_dirt, ground_y, "platform_grassy_dirt.png"),
                Platform(base_x + 2 * w_dirt, ground_y, "platform_stone_brick.png")
            ])
            # High wood platform
            self.platforms.append(Platform(base_x + 250, ground_y - 190, "platform_wood.png"))
            # Coins
            self.collectibles.extend([
                CollectibleItem(base_x + 300, ground_y - 260, "coin"),
                CollectibleItem(base_x + 360, ground_y - 260, "coin")
            ])
            # Enemies
            self.enemies.append(SlimeEnemy(base_x + random.randint(100, 450), ground_y - 64, patrol_dist=80))

        def generate_spike_gap_chunk(base_x):
            # Ground blocks with a gap
            gap_start = base_x + w_dirt
            gap_width = 170
            self.platforms.extend([
                Platform(base_x, ground_y, "platform_grassy_dirt.png"),
                Platform(gap_start + gap_width, ground_y, "platform_grassy_dirt.png")
            ])
            # Spikes in the gap
            self.hazards.append(Hazard(gap_start + 20, ground_y + 30, "hazard_spikes.png"))
            # Bouncy mushroom inside the gap to bounce out
            self.interactive_objects.append(InteractiveObject(gap_start + 60, ground_y + 10, "mushroom"))
            # Floating wood platform over the gap
            self.platforms.append(Platform(gap_start - 20, ground_y - 180, "platform_wood.png"))
            # Coins above wood platform
            self.collectibles.extend([
                CollectibleItem(gap_start + 10, ground_y - 250, "coin"),
                CollectibleItem(gap_start + 70, ground_y - 250, "coin")
            ])
            # Goblin on the wood platform
            self.enemies.append(ForestGoblinEnemy(gap_start + 10, ground_y - 180 - 72, patrol_dist=30))

        def generate_bridge_climb_chunk(base_x):
            # Ground with a rope bridge gap
            self.platforms.extend([
                Platform(base_x, ground_y, "platform_grassy_dirt.png"),
                Platform(base_x + w_dirt, ground_y, "platform_rope_bridge.png"),
                Platform(base_x + w_dirt + w_bridge, ground_y, "platform_grassy_dirt.png")
            ])
            # Floating wood and mossy stone platforms
            self.platforms.extend([
                Platform(base_x + 180, ground_y - 180, "platform_wood.png"),
                Platform(base_x + w_dirt + 120, ground_y - 260, "platform_mossy_stone.png")
            ])
            # Coins
            self.collectibles.extend([
                CollectibleItem(base_x + 230, ground_y - 240, "coin"),
                CollectibleItem(base_x + w_dirt + 170, ground_y - 320, "coin")
            ])
            # Goblin on high mossy stone
            self.enemies.append(ForestGoblinEnemy(base_x + w_dirt + 150, ground_y - 260 - 72, patrol_dist=30))
            # Slime on floor
            self.enemies.append(SlimeEnemy(base_x + 100, ground_y - 64, patrol_dist=60))

        def generate_boss_arena_chunk(base_x):
            # Ground
            self.platforms.extend([
                Platform(base_x, ground_y, "platform_grassy_dirt.png"),
                Platform(base_x + w_dirt + 160, ground_y, "platform_grassy_dirt.png")
            ])
            # Raised mossy rock barrier in the middle
            h_rock = assets.load_platform_image("platform_mossy_rock.png").get_height()
            self.platforms.append(Platform(base_x + w_dirt - 30, ground_y - h_rock + 25, "platform_mossy_rock.png"))
            # Jump pad to vault over the rock barrier
            self.interactive_objects.append(InteractiveObject(base_x + 120, ground_y - 48, "jump_pad"))
            # Coins above rock
            self.collectibles.extend([
                CollectibleItem(base_x + w_dirt, ground_y - h_rock - 30, "coin"),
                CollectibleItem(base_x + w_dirt + 60, ground_y - h_rock - 30, "coin")
            ])
            # Horned Beast Mini-Boss guarding the other side
            self.enemies.append(HornedBeastEnemy(base_x + w_dirt + 240, ground_y - 120))

        # Randomly choose and construct 3 middle chunks
        chunk_generators = [
            generate_flat_chunk, 
            generate_spike_gap_chunk, 
            generate_bridge_climb_chunk, 
            generate_boss_arena_chunk
        ]
        
        # Ensure we get a good variety of different middle chunks
        chosen_generators = [random.choice(chunk_generators) for _ in range(3)]
        
        for generator in chosen_generators:
            generator(current_x)
            current_x += chunk_width
            
        # 5. End Chunk (starting at current_x, which is 500 + 2400 = 2900)
        self.platforms.extend([
            Platform(current_x, ground_y, "platform_grassy_dirt.png"),
            Platform(current_x + w_dirt, ground_y, "platform_grassy_dirt.png")
        ])
        # Treasure chest
        self.collectibles.append(CollectibleItem(current_x + 200, ground_y - 48, "chest"))
        # Final slime guarding chest
        self.enemies.append(SlimeEnemy(current_x + 50, ground_y - 64, patrol_dist=50))
        
        self.finish_x = current_x + 200
