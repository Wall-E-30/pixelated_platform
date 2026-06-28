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
            "idle": [(176, 353, 114, 213)],
            "run": [
                (434, 376, 182, 190),
                (611, 376, 166, 189)
            ],
            "jump": [(852, 311, 126, 224)],
            "fall": [(852, 311, 126, 224)], # Reusing jump pose for fall
            "attack": [(1094, 394, 268, 172)]
        }
        
        # Define bounding boxes for Slime Enemy sprites (from enemy_slime_spritesheet.png)
        # Bounding boxes: (x, y, width, height)
        # Original sprites face right.
        self.SLIME_BOXES = {
            "idle": [(215, 497, 127, 66)],
            "walk": [
                (215, 497, 127, 66),
                (447, 497, 167, 68),
                (632, 497, 191, 66)
            ],
            "jump": [(909, 388, 118, 164)],
            "fall": [(1142, 516, 201, 60)]
        }
        
        # Bounding boxes for Forest Goblin (from goblin_spritesheet.png and leaf_goblin_spritesheet.png)
        self.GOBLIN_BOXES = {
            "idle": [(253, 465, 185, 179)],
            "run": [(512, 428, 236, 215)],
            "melee": [(735, 483, 298, 163)],
            "hit": [(1098, 468, 219, 184)]
        }
        self.LEAF_GOBLIN_BOXES = {
            "cloak": [(178, 517, 219, 196)],
            "revealed": [(1059, 520, 333, 200)],
            "throw": [(519, 473, 458, 236)]
        }
        
        # Bounding boxes for Horned Beast (from golem_spritesheet.png)
        self.HORNED_BEAST_BOXES = {
            "idle": [(130, 319, 390, 369)],
            "slam": [(544, 400, 447, 288)],
            "hit": [(1045, 388, 358, 303)]
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
        sheet_path = join("assets", "Characters", "player_spritesheet.png")
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
        sheet_path = join("assets", "Enemies", "enemy_slime_spritesheet.png")
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
        """Extracts and returns Goblin animations from both standard and leaf sheets."""
        std_sheet_path = join("assets", "Enemies", "goblin_spritesheet.png")
        leaf_sheet_path = join("assets", "Enemies", "leaf_goblin_spritesheet.png")
        
        std_sheet = self.load_image(std_sheet_path)
        leaf_sheet = self.load_image(leaf_sheet_path)
        
        animations = {}
        
        # Load from standard sheet (idle, run, melee, hit)
        for state, boxes in self.GOBLIN_BOXES.items():
            right_sprites = []
            left_sprites = []
            for box in boxes:
                sprite = self.extract_and_scale_sprite(std_sheet, box, target_size)
                right_sprites.append(sprite)
                left_sprites.append(pygame.transform.flip(sprite, True, False))
            animations[f"{state}_right"] = right_sprites
            animations[f"{state}_left"] = left_sprites
            
        # Load from leaf variant sheet (cloak, revealed, throw)
        for state, boxes in self.LEAF_GOBLIN_BOXES.items():
            right_sprites = []
            left_sprites = []
            for box in boxes:
                sprite = self.extract_and_scale_sprite(leaf_sheet, box, target_size)
                right_sprites.append(sprite)
                left_sprites.append(pygame.transform.flip(sprite, True, False))
            animations[f"{state}_right"] = right_sprites
            animations[f"{state}_left"] = left_sprites
            
        return animations

    def load_horned_beast_sprites(self, target_size=128):
        """Extracts and returns Horned Beast animations from golem_spritesheet.png."""
        sheet_path = join("assets", "Enemies", "golem_spritesheet.png")
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
        """Loads a background tile from assets/Background/."""
        path = join("assets", "Background", name)
        return self.load_image(path)

    def load_platform_image(self, name):
        """Loads a platform image from assets/Forest/."""
        path = join("assets", "Forest", name)
        return self.load_image(path)

    def load_hazard_image(self, name):
        """Loads a hazard image from assets/Forest/."""
        path = join("assets", "Forest", name)
        return self.load_image(path)

    def load_decoration_image(self, name):
        """Loads a decoration image from assets/Forest/."""
        path = join("assets", "Forest", name)
        return self.load_image(path)

    def load_projectile_image(self, name):
        """Loads a projectile image from assets/Enemies/."""
        path = join("assets", "Enemies", name)
        return self.load_image(path)

