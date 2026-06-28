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
        self.background_name = "Copilot_20260628_094414.png"  # Gorgeous forest parallax background
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
        # 1. Background decorations (Far distance, Parallax = 0.3 - 0.5)
        # Trees placed across the level
        self.decorations.extend([
            # Far Pine Trees (Factor 0.3)
            Decoration(150, 310, "decor_pine_trees.png", parallax_factor=0.3),
            Decoration(950, 310, "decor_pine_trees.png", parallax_factor=0.3),
            Decoration(1750, 310, "decor_pine_trees.png", parallax_factor=0.3),
            Decoration(2600, 310, "decor_pine_trees.png", parallax_factor=0.3),
            
            # Far Deciduous Trees (Factor 0.4)
            Decoration(500, 290, "decor_deciduous_tree.png", parallax_factor=0.4),
            Decoration(1300, 290, "decor_deciduous_tree.png", parallax_factor=0.4),
            Decoration(2100, 290, "decor_deciduous_tree.png", parallax_factor=0.4),
            Decoration(2900, 290, "decor_deciduous_tree.png", parallax_factor=0.4),
            
            # Closer Leafy Trees (Factor 0.7)
            Decoration(300, 500, "decor_leafy_tree.png", parallax_factor=0.7),
            Decoration(1150, 500, "decor_leafy_tree.png", parallax_factor=0.7),
            Decoration(2400, 500, "decor_leafy_tree.png", parallax_factor=0.7),
        ])
        
        # 2. Foreground decorations (No parallax, factor = 1.0, drawn behind entities)
        self.decorations.extend([
            Decoration(750, 550, "decor_fallen_log.png", parallax_factor=1.0),
            Decoration(2150, 550, "decor_fallen_log.png", parallax_factor=1.0),
            Decoration(1000, 560, "decor_stump_logs.png", parallax_factor=1.0),
            Decoration(2750, 560, "decor_stump_logs.png", parallax_factor=1.0),
        ])
        
        # 3. Platforms (Solid, collidable ground)
        # Ground platforms
        # y = 680 is the floor surface height for most blocks
        self.platforms.extend([
            # Starting floor block (0 to 359)
            Platform(0, 680, "platform_grassy_dirt.png"),
            
            # Rope bridge over water/gap (359 to 654)
            Platform(359, 680, "platform_rope_bridge.png"),
            
            # Middle floor block (654 to 1013)
            Platform(654, 680, "platform_grassy_dirt.png"),
            
            # Gap from 1013 to 1210 (Contains spikes below)
            # Next block starts at 1210 (1210 to 1454)
            Platform(1210, 680, "platform_stone_brick.png"),
            
            # Platform raised slightly (1454 to 1710)
            Platform(1454, 620, "platform_mossy_stone.png"),
            
            # Wood platform (1920 to 2148)
            Platform(1920, 650, "platform_wood.png"),
            
            # Long ground path (2148 to 2507)
            Platform(2148, 680, "platform_grassy_dirt.png"),
            
            # Raised rock barrier (2507 to 2772)
            Platform(2507, 600, "platform_mossy_rock.png"),
            
            # Stone brick wall before final floor (2772 to 3016)
            Platform(2772, 520, "platform_stone_brick.png"),
            
            # Final Floor (3016 to 3500)
            Platform(3016, 680, "platform_grassy_dirt.png"),
        ])
        
        # 4. Floating platforms (For jumping challenges)
        self.platforms.extend([
            Platform(500, 500, "platform_wood.png"),          # Floating wood above rope bridge
            Platform(800, 430, "platform_mossy_stone.png"),   # Floating mossy stone
            Platform(1350, 480, "platform_stone_brick.png"),  # Floating brick
            Platform(1650, 380, "platform_wood.png"),         # Floating wood
            Platform(2250, 480, "platform_mossy_stone.png"),  # Floating mossy stone
        ])
        
        # 5. Hazards (Spikes placed in gaps or platforms)
        self.hazards.extend([
            # Spikes in the gap between 1013 and 1210
            Hazard(1013, 730, "hazard_spikes.png"),
            
            # Spikes placed on the high stone wall for challenge
            Hazard(2800, 424, "hazard_spikes.png"),
        ])
        
        # 6. Interactive Objects (Bouncy springs & mushrooms)
        self.interactive_objects.extend([
            # Bouncy mushroom in the bottom of the spiked gap to help recover
            InteractiveObject(1090, 690, "mushroom"),
            
            # Jump pad to jump high onto the stone wall barrier
            InteractiveObject(2650, 632, "jump_pad"),
        ])
        
        # 7. Collectible Items (Gold coins & final treasure chest)
        # Gold coins distributed on floating/challenging platforms
        self.collectibles.extend([
            # Coins on starting ground
            CollectibleItem(250, 640, "coin"),
            CollectibleItem(300, 640, "coin"),
            
            # Coins on rope bridge platform
            CollectibleItem(520, 460, "coin"),
            CollectibleItem(560, 460, "coin"),
            
            # Coins in middle section
            CollectibleItem(820, 390, "coin"),
            CollectibleItem(1370, 440, "coin"),
            CollectibleItem(1670, 340, "coin"),
            CollectibleItem(2270, 440, "coin"),
            
            # Coins before final boss
            CollectibleItem(2520, 560, "coin"),
            CollectibleItem(2580, 560, "coin"),
            
            # Final Source Code chest at the end
            CollectibleItem(3250, 632, "chest"),
        ])
        
        # 8. Enemies
        self.enemies.extend([
            # Patrol Slime on starting area
            SlimeEnemy(750, 616, patrol_dist=100),
            
            # Slime on high mossy stone platform
            SlimeEnemy(850, 366, patrol_dist=50),
            
            # Forest Goblin in Leaf Cloak camouflage above rope bridge
            ForestGoblinEnemy(570, 428, patrol_dist=40),
            
            # Forest Goblin on floating wood platform in middle
            ForestGoblinEnemy(1660, 308, patrol_dist=40),
            
            # Slime on stone brick floor
            SlimeEnemy(1280, 616, patrol_dist=60),
            
            # Horned Beast Mini-Boss guarding the forest floor path
            HornedBeastEnemy(2300, 560),
            
            # Patrol slime near the chest
            SlimeEnemy(3100, 616, patrol_dist=50),
        ])

