import os
import pygame
from os.path import join

class AssetsManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AssetsManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        self.initialized = True
        self.image_cache = {}
        
        # Define the exact bounding boxes for Player sprites (from player_spritesheet.png)
        # Bounding boxes: (x, y, width, height)
        # The original sprites face right.
        self.PLAYER_BOXES = {
            "idle": [(1035, 90, 136, 317)],
            "run": [
                (1336, 471, 209, 307),
                (1609, 471, 203, 306),
                (1900, 475, 220, 288),
                (2197, 472, 223, 304)
            ],
            "jump": [
                (1369, 941, 216, 299),
                (1672, 882, 150, 347)
            ],
            "fall": [
                (1900, 869, 239, 349),
                (2197, 932, 212, 308),
                (90, 1340, 171, 313)
            ],
            "attack": [
                (84, 902, 244, 337),
                (332, 903, 265, 336),
                (658, 904, 225, 334),
                (957, 886, 258, 352)
            ],
            "hit": [
                (345, 1338, 175, 316),
                (574, 1340, 285, 312)
            ]
        }
        
        # Define bounding boxes for Slime Enemy sprites (from Slime.png)
        self.SLIME_BOXES = {
            "idle": [
                (1372, 182, 211, 116),
                (1634, 182, 267, 116),
                (1931, 201, 266, 97),
                (2225, 210, 247, 88)
            ],
            "walk": [
                (62, 415, 198, 113),
                (300, 415, 200, 113),
                (549, 415, 195, 113),
                (793, 419, 201, 111),
                (1031, 418, 210, 111),
                (1284, 418, 195, 112)
            ],
            "jump": [
                (77, 783, 201, 106),
                (331, 729, 201, 160),
                (593, 635, 224, 158),
                (870, 695, 228, 159),
                (1145, 806, 246, 84)
            ],
            "fall": [
                (1441, 779, 198, 110),
                (1725, 742, 198, 147),
                (1972, 744, 206, 145),
                (2224, 731, 209, 158)
            ]
        }
        
        # Bounding boxes for Forest Goblin (from Forest_Goblin.png)
        self.GOBLIN_BOXES = {
            "idle": [(54, 88, 191, 258)],
            "run": [
                (452, 88, 205, 258),
                (752, 88, 209, 258),
                (1033, 88, 213, 258),
                (1344, 88, 238, 257)
            ],
            "melee": [
                (48, 446, 251, 257),
                (340, 454, 305, 255)
            ],
            "hit": [
                (42, 851, 199, 263),
                (435, 857, 298, 256),
                (775, 862, 287, 246)
            ]
        }
        self.LEAF_GOBLIN_BOXES = {
            "cloak": [(2176, 1251, 199, 250)],
            "revealed": [(2500, 1239, 192, 262)],
            "throw": [
                (946, 452, 230, 257),
                (1234, 454, 293, 255)
            ]
        }
        
        # Bounding boxes for Horned Beast (from Horned_Beast.png)
        self.HORNED_BEAST_BOXES = {
            "idle": [(49, 135, 372, 362)],
            "slam": [
                (84, 671, 499, 339),
                (681, 652, 325, 358),
                (1039, 695, 452, 314)
            ],
            "hit": [
                (1751, 678, 342, 336),
                (2112, 682, 342, 332)
            ]
        }
        
        # Mapping from filename to sheet, coordinates, and original size
        self.SHEET_MAPPINGS = {
            # Terrain/Platforms (from Terrain/background_items.png)
            "platform_grassy_dirt.png": ("Terrain/background_items.png", (47, 24, 141, 164), (359, 142)),
            "platform_stone_brick.png": ("Terrain/background_items.png", (728, 42, 140, 146), (244, 99)),
            "platform_wood.png": ("Terrain/background_items.png", (2247, 100, 358, 206), (228, 91)),
            "platform_rope_bridge.png": ("Terrain/background_items.png", (2247, 100, 358, 206), (295, 130)),
            "platform_mossy_stone.png": ("Terrain/background_items.png", (1408, 42, 141, 146), (256, 105)),
            "platform_mossy_rock.png": ("Terrain/background_items.png", (1120, 1284, 277, 229), (265, 140)),
            
            # Hazards
            "hazard_spikes.png": ("Terrain/background_items.png", (65, 1296, 222, 199), (204, 96)),
            
            # Interactive Objects
            "interactive_jump_pad.png": ("Terrain/background_items.png", (1490, 1331, 111, 158), (129, 116)),
            "interactive_mushroom.png": ("Terrain/background_items.png", (1643, 1372, 104, 117), (141, 123)),
            
            # Decorations
            "decor_pine_trees.png": ("Terrain/background_items.png", (646, 597, 386, 617), (417, 374)),
            "decor_deciduous_tree.png": ("Terrain/background_items.png", (47, 575, 593, 651), (470, 394)),
            "decor_leafy_tree.png": ("Terrain/background_items.png", (1655, 1033, 170, 181), (227, 181)),
            "decor_fallen_log.png": ("Terrain/background_items.png", (1421, 693, 368, 204), (530, 150)),
            "decor_stump_logs.png": ("Terrain/background_items.png", (1842, 686, 282, 211), (465, 121)),
            
            # Collectibles (from Items/collectibles.png)
            "item_coin.png": ("Items/collectibles.png", (30, 26, 102, 112), (105, 105)),
            "ui_heart.png": ("Items/collectibles.png", (856, 169, 136, 123), (88, 80)),
        }



    def load_image(self, path, convert_alpha=True):
        """Loads and caches images to avoid redundant disk access."""
        if path in self.image_cache:
            return self.image_cache[path]
            
        if not os.path.exists(path):
            raise FileNotFoundError(f"Asset file not found: {path}")
            
        image = pygame.image.load(path)
        if convert_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
            
        self.image_cache[path] = image
        return image

    def extract_and_scale_sprite(self, sheet, box, target_size):
        """
        Crops a sprite from a sheet, scales it preserving aspect ratio,
        and centers it on a transparent square surface of size (target_size, target_size).
        """
        x, y, w, h = box
        # Extract sub-surface
        sub_rect = pygame.Rect(x, y, w, h)
        sub_surface = sheet.subsurface(sub_rect)
        
        # Calculate scaling to fit within target_size while keeping aspect ratio
        scale_ratio = min(target_size / w, target_size / h)
        new_w = int(w * scale_ratio)
        new_h = int(h * scale_ratio)
        
        scaled_sub = pygame.transform.scale(sub_surface, (new_w, new_h))
        
        # Create transparent target surface
        final_surface = pygame.Surface((target_size, target_size), pygame.SRCALPHA, 32)
        
        # Center scaled sprite on target surface
        offset_x = (target_size - new_w) // 2
        offset_y = (target_size - new_h) // 2
        final_surface.blit(scaled_sub, (offset_x, offset_y))
        
        return final_surface

    def load_player_sprites(self, target_size=96):
        """Extracts and returns player animations, categorized by state and direction."""
        sheet_path = join("assets", "Characters", "Samurai.png")
        sheet = self.load_image(sheet_path)
        
        animations = {}
        
        for state, boxes in self.PLAYER_BOXES.items():
            right_sprites = []
            left_sprites = []
            
            for box in boxes:
                sprite = self.extract_and_scale_sprite(sheet, box, target_size)
                right_sprites.append(sprite)
                # Flip for left direction
                left_sprite = pygame.transform.flip(sprite, True, False)
                left_sprites.append(left_sprite)
                
            animations[f"{state}_right"] = right_sprites
            animations[f"{state}_left"] = left_sprites
            
        return animations

    def load_slime_sprites(self, target_size=64):
        """Extracts and returns slime enemy animations, categorized by state and direction."""
        sheet_path = join("assets", "Enemies", "Slime.png")
        sheet = self.load_image(sheet_path)
        
        animations = {}
        
        for state, boxes in self.SLIME_BOXES.items():
            right_sprites = []
            left_sprites = []
            
            for box in boxes:
                sprite = self.extract_and_scale_sprite(sheet, box, target_size)
                right_sprites.append(sprite)
                left_sprite = pygame.transform.flip(sprite, True, False)
                left_sprites.append(left_sprite)
                
            animations[f"{state}_right"] = right_sprites
            animations[f"{state}_left"] = left_sprites
            
        return animations

    def load_goblin_sprites(self, target_size=96):
        """Extracts and returns Goblin animations from Forest_Goblin.png."""
        sheet_path = join("assets", "Enemies", "Forest_Goblin.png")
        sheet = self.load_image(sheet_path)
        
        animations = {}
        
        # Load from standard sheet (idle, run, melee, hit)
        for state, boxes in self.GOBLIN_BOXES.items():
            right_sprites = []
            left_sprites = []
            for box in boxes:
                sprite = self.extract_and_scale_sprite(sheet, box, target_size)
                right_sprites.append(sprite)
                left_sprites.append(pygame.transform.flip(sprite, True, False))
            animations[f"{state}_right"] = right_sprites
            animations[f"{state}_left"] = left_sprites
            
        # Load from leaf variant sheet (cloak, revealed, throw)
        for state, boxes in self.LEAF_GOBLIN_BOXES.items():
            right_sprites = []
            left_sprites = []
            for box in boxes:
                sprite = self.extract_and_scale_sprite(sheet, box, target_size)
                right_sprites.append(sprite)
                left_sprites.append(pygame.transform.flip(sprite, True, False))
            animations[f"{state}_right"] = right_sprites
            animations[f"{state}_left"] = left_sprites
            
        return animations

    def load_horned_beast_sprites(self, target_size=128):
        """Extracts and returns Horned Beast animations from Horned_Beast.png."""
        sheet_path = join("assets", "Enemies", "Horned_Beast.png")
        sheet = self.load_image(sheet_path)
        
        animations = {}
        for state, boxes in self.HORNED_BEAST_BOXES.items():
            right_sprites = []
            left_sprites = []
            for box in boxes:
                sprite = self.extract_and_scale_sprite(sheet, box, target_size)
                right_sprites.append(sprite)
                left_sprites.append(pygame.transform.flip(sprite, True, False))
            animations[f"{state}_right"] = right_sprites
            animations[f"{state}_left"] = left_sprites
            
        return animations

    def load_background_tile(self, name):
        """Loads a background tile from assets/Background/ or assets/Forest/ with dimming."""
        path_bg = join("assets", "Background", name)
        path_forest = join("assets", "Forest", name)
        path = path_bg if os.path.exists(path_bg) else path_forest
        img = self.load_image(path)
        
        # Apply a darkening filter to the background image so it sits back and platforms pop!
        dimmed = img.copy()
        dimmed.fill((85, 85, 105, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return dimmed

    def load_mapped_sprite(self, name):
        """Checks SHEET_MAPPINGS, crops and scales from unified sheets, caching the result."""
        cache_key = f"mapped_{name}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
            
        if name in self.SHEET_MAPPINGS:
            sheet_subpath, box, target_size = self.SHEET_MAPPINGS[name]
            sheet_path = join("assets", sheet_subpath)
            sheet = self.load_image(sheet_path)
            
            x, y, w, h = box
            sub_rect = pygame.Rect(x, y, w, h)
            sub_surface = sheet.subsurface(sub_rect)
            
            scaled = pygame.transform.scale(sub_surface, target_size)
            self.image_cache[cache_key] = scaled
            return scaled
            
        return None

    def load_platform_image(self, name):
        """Loads a platform image from sheet if mapped, otherwise from assets/Forest/."""
        img = self.load_mapped_sprite(name)
        if img is not None:
            return img
        path = join("assets", "Forest", name)
        return self.load_image(path)

    def load_hazard_image(self, name):
        """Loads a hazard image from sheet if mapped, otherwise from assets/Forest/."""
        img = self.load_mapped_sprite(name)
        if img is not None:
            return img
        path = join("assets", "Forest", name)
        return self.load_image(path)

    def load_decoration_image(self, name):
        """Loads a decoration image with desaturation."""
        img = self.load_mapped_sprite(name)
        if img is None:
            path = join("assets", "Forest", name)
            img = self.load_image(path)
            
        # Dim decorations so players do not confuse them with collidable platforms
        dimmed = img.copy()
        dimmed.fill((135, 135, 155, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return dimmed

    def load_projectile_image(self, name):
        """Loads a projectile image from assets/Enemies/."""
        path = join("assets", "Enemies", name)
        return self.load_image(path)

