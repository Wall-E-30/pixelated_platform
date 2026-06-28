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
        
        # 1. Background decorations (placed globally across the whole generated level width)
        # We will distribute them dynamically based on the total width of the level.
        # Total Level Width = Start Chunk (500) + 3 Middle Chunks (3 * 800 = 2400) + End Chunk (500) = 3400
        total_width = 3400
        
        # Spatially distribute background pine trees, deciduous trees, and leafy trees
        for x in range(150, total_width - 300, 800):
            self.decorations.append(Decoration(x, 310, "decor_pine_trees.png", parallax_factor=0.3))
        for x in range(500, total_width - 300, 800):
            self.decorations.append(Decoration(x, 290, "decor_deciduous_tree.png", parallax_factor=0.4))
        for x in range(300, total_width - 300, 900):
            self.decorations.append(Decoration(x, 500, "decor_leafy_tree.png", parallax_factor=0.7))
            
        # 2. Foreground decorations (drawn behind entities)
        for x in range(750, total_width - 500, 1200):
            self.decorations.append(Decoration(x, 550, "decor_fallen_log.png", parallax_factor=1.0))
            self.decorations.append(Decoration(x + 250, 560, "decor_stump_logs.png", parallax_factor=1.0))
            
        # 3. Start Chunk (0 to 500)
        # Safe spawning area
        self.platforms.extend([
            Platform(0, 680, "platform_grassy_dirt.png"),
            Platform(359, 680, "platform_grassy_dirt.png")
        ])
        # Start patrol slime
        self.enemies.append(SlimeEnemy(random.randint(250, 420), 616, patrol_dist=60))
        
        # 4. Generate 3 randomized middle chunks
        chunk_width = 800
        current_x = 500
        
        # Define the chunk generation functions to choose from
        def generate_flat_chunk(base_x):
            # Ground
            self.platforms.extend([
                Platform(base_x, 680, "platform_grassy_dirt.png"),
                Platform(base_x + 359, 680, "platform_grassy_dirt.png"),
                Platform(base_x + 718, 680, "platform_stone_brick.png")
            ])
            # High wood platform
            self.platforms.append(Platform(base_x + 250, 480, "platform_wood.png"))
            # Coins
            self.collectibles.extend([
                CollectibleItem(base_x + 300, 400, "coin"),
                CollectibleItem(base_x + 360, 400, "coin")
            ])
            # Enemies
            self.enemies.append(SlimeEnemy(base_x + random.randint(100, 500), 616, patrol_dist=80))

        def generate_spike_gap_chunk(base_x):
            # Ground blocks with a gap from base_x + 359 to base_x + 500
            self.platforms.extend([
                Platform(base_x, 680, "platform_grassy_dirt.png"),
                Platform(base_x + 500, 680, "platform_grassy_dirt.png")
            ])
            # Spikes in the gap
            self.hazards.append(Hazard(base_x + 370, 730, "hazard_spikes.png"))
            # Bouncy mushroom inside the gap to bounce out
            self.interactive_objects.append(InteractiveObject(base_x + 410, 690, "mushroom"))
            # Floating wood platform over the gap
            self.platforms.append(Platform(base_x + 330, 500, "platform_wood.png"))
            # Coins above wood platform
            self.collectibles.extend([
                CollectibleItem(base_x + 380, 420, "coin"),
                CollectibleItem(base_x + 440, 420, "coin")
            ])
            # Goblin on the wood platform
            self.enemies.append(ForestGoblinEnemy(base_x + random.randint(330, 430), 428, patrol_dist=30))

        def generate_bridge_climb_chunk(base_x):
            # Ground with a rope bridge gap from base_x + 359 to base_x + 654
            self.platforms.extend([
                Platform(base_x, 680, "platform_grassy_dirt.png"),
                Platform(base_x + 359, 680, "platform_rope_bridge.png"),
                Platform(base_x + 654, 680, "platform_grassy_dirt.png")
            ])
            # Floating wood and mossy stone platforms
            self.platforms.extend([
                Platform(base_x + 200, 500, "platform_wood.png"),
                Platform(base_x + 500, 430, "platform_mossy_stone.png")
            ])
            # Coins
            self.collectibles.extend([
                CollectibleItem(base_x + 250, 440, "coin"),
                CollectibleItem(base_x + 550, 370, "coin")
            ])
            # Goblin on high mossy stone
            self.enemies.append(ForestGoblinEnemy(base_x + random.randint(500, 600), 358, patrol_dist=30))
            # Slime on floor
            self.enemies.append(SlimeEnemy(base_x + 100, 616, patrol_dist=60))

        def generate_boss_arena_chunk(base_x):
            # Ground
            self.platforms.extend([
                Platform(base_x, 680, "platform_grassy_dirt.png"),
                Platform(base_x + 515, 680, "platform_grassy_dirt.png")
            ])
            # Raised mossy rock barrier in the middle
            self.platforms.append(Platform(base_x + 250, 600, "platform_mossy_rock.png"))
            # Jump pad to vault over the rock barrier
            self.interactive_objects.append(InteractiveObject(base_x + 150, 632, "jump_pad"))
            # Coins above rock
            self.collectibles.extend([
                CollectibleItem(base_x + 300, 520, "coin"),
                CollectibleItem(base_x + 360, 520, "coin")
            ])
            # Horned Beast Mini-Boss guarding the other side
            self.enemies.append(HornedBeastEnemy(base_x + random.randint(550, 680), 560))

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
            Platform(current_x, 680, "platform_grassy_dirt.png"),
            Platform(current_x + 359, 680, "platform_grassy_dirt.png")
        ])
        # Treasure chest
        self.collectibles.append(CollectibleItem(current_x + 200, 632, "chest"))
        # Final slime guarding chest
        self.enemies.append(SlimeEnemy(current_x + 50, 616, patrol_dist=50))
        
        self.finish_x = current_x + 200

