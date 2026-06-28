import pygame
from assets_manager import AssetsManager

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, image_name):
        super().__init__()
        self.assets_manager = AssetsManager()
        self.image = self.assets_manager.load_platform_image(image_name)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, image_name="hazard_spikes.png", damage=1):
        super().__init__()
        self.assets_manager = AssetsManager()
        self.image = self.assets_manager.load_hazard_image(image_name)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = damage
        self.name = "spikes"

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Decoration(pygame.sprite.Sprite):
    def __init__(self, x, y, image_name, parallax_factor=0.3):
        """
        Non-collidable atmospheric decorations.
        parallax_factor: 0.0 means moves with screen (hud), 
                         0.5 means moves at half speed of player (distant background),
                         1.0 means moves with world (standard foreground).
        """
        super().__init__()
        self.assets_manager = AssetsManager()
        self.image = self.assets_manager.load_decoration_image(image_name)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.parallax_factor = parallax_factor

    def draw(self, win, offset_x, offset_y=0):
        # Apply parallax formula: x_pos = start_x - offset_x * factor
        # Since standard objects move as rect.x - offset_x, parallax is offset_x * (1 - parallax_factor)
        # So we render at: rect.x - offset_x * parallax_factor
        render_x = self.rect.x - int(offset_x * self.parallax_factor)
        render_y = self.rect.y - int(offset_y * self.parallax_factor)
        win.blit(self.image, (render_x, render_y))


class CollectibleItem(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type="coin"):
        super().__init__()
        self.assets_manager = AssetsManager()
        self.item_type = item_type
        self.collected = False
        
        if item_type == "coin":
            raw_image = self.assets_manager.load_platform_image("item_coin.png")
            self.image = pygame.transform.scale(raw_image, (32, 32))
        elif item_type == "chest":
            raw_image = self.assets_manager.load_platform_image("item_chest.png")
            # item_chest.png contains 2 frames: 0 = closed, 1 = open
            w, h = raw_image.get_size()
            frame_w = w // 2
            self.sprites = [
                raw_image.subsurface((0, 0, frame_w, h)),
                raw_image.subsurface((frame_w, 0, frame_w, h))
            ]
            self.sprites = [pygame.transform.scale(s, (56, 48)) for s in self.sprites]
            self.image = self.sprites[0]
        else:
            raw_image = self.assets_manager.load_platform_image("item_coin.png")
            self.image = pygame.transform.scale(raw_image, (32, 32))
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def collect(self):
        self.collected = True
        if self.item_type == "chest" and hasattr(self, "sprites"):
            self.image = self.sprites[1]
            self.mask = pygame.mask.from_surface(self.image)

    def draw(self, win, offset_x):
        if self.item_type == "chest":
            # Always draw the chest (closed or open)
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
        elif not self.collected:
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class InteractiveObject(pygame.sprite.Sprite):
    def __init__(self, x, y, obj_type="jump_pad"):
        super().__init__()
        self.assets_manager = AssetsManager()
        self.obj_type = obj_type
        
        if obj_type == "jump_pad":
            raw_image = self.assets_manager.load_platform_image("interactive_jump_pad.png")
            self.image = pygame.transform.scale(raw_image, (48, 48))
            self.bounce_vel = -14.5
        elif obj_type == "mushroom":
            raw_image = self.assets_manager.load_platform_image("interactive_mushroom.png")
            self.image = pygame.transform.scale(raw_image, (48, 48))
            self.bounce_vel = -11.0
        else:
            raw_image = self.assets_manager.load_platform_image("interactive_jump_pad.png")
            self.image = pygame.transform.scale(raw_image, (48, 48))
            self.bounce_vel = -12.0
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_tick = 0
        self.animating = False

    def trigger_bounce(self, player):
        player.y_vel = self.bounce_vel
        player.fall_count = 0
        player.jump_count = 1  # Reset to 1 jump allowed (effectively double jump allowed mid-air!)
        player.state = "jump"
        self.animating = True
        self.animation_tick = 12

    def update(self):
        if self.animating:
            self.animation_tick -= 1
            if self.animation_tick <= 0:
                self.animating = False

    def draw(self, win, offset_x):
        if self.animating:
            squashed = pygame.transform.scale(self.image, (self.rect.width + 10, self.rect.height - 10))
            render_rect = squashed.get_rect(midbottom=(self.rect.centerx, self.rect.bottom))
            win.blit(squashed, (render_rect.x - offset_x, render_rect.y))
        else:
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

