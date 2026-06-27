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
