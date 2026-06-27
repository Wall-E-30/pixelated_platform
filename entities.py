import pygame
from assets_manager import AssetsManager

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.fall_count = 0
        self.direction = "right"
        self.image = None
        self.mask = None

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def update_mask(self):
        if self.image:
            self.mask = pygame.mask.from_surface(self.image)


class Player(Entity):
    GRAVITY = 0.8
    ANIMATION_DELAY = 5
    INVINCIBLE_DURATION = 90  # Frames of invincibility after hit

    def __init__(self, x, y):
        super().__init__(x, y, 96, 96)
        self.assets_manager = AssetsManager()
        self.sprites = self.assets_manager.load_player_sprites(target_size=96)
        
        self.image = self.sprites["idle_right"][0]
        self.update_mask()
        
        # Gameplay variables
        self.max_health = 5
        self.health = 5
        self.jump_count = 0
        self.direction = "right"
        
        # State machine
        self.state = "idle" # idle, run, jump, fall, attack, hit
        self.hit = False
        self.hit_timer = 0
        self.attacking = False
        self.attack_timer = 0
        self.animation_count = 0

    def jump(self):
        # Jump or Double Jump
        if self.jump_count < 2:
            # -8 or -9 vertical velocity
            self.y_vel = -8.5
            self.jump_count += 1
            self.fall_count = 0
            self.animation_count = 0
            self.state = "jump"

    def attack(self):
        if not self.attacking and self.state != "hit":
            self.attacking = True
            self.attack_timer = 20  # Attack duration in frames
            self.animation_count = 0
            self.state = "attack"
            self.x_vel = 0 # Stop horizontal movement momentarily

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
        if self.state not in ["attack", "hit"]:
            if self.x_vel != 0:
                self.state = "run"
            else:
                self.state = "idle"

    def hit_head(self):
        self.y_vel = 0 # Stop upward movement

    def take_damage(self, damage, source_x):
        if not self.hit:
            self.health -= damage
            self.hit = True
            self.hit_timer = self.INVINCIBLE_DURATION
            self.state = "hit"
            self.animation_count = 0
            
            # Apply knockback
            knockback_dir = 1 if self.rect.centerx > source_x else -1
            self.x_vel = knockback_dir * 8
            self.y_vel = -4
            self.fall_count = 0

    def loop(self, fps, platforms):
        # Apply gravity
        self.y_vel += min(0.9, (self.fall_count / fps) * self.GRAVITY)
        self.fall_count += 1
        
        # Handle timers
        if self.hit:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.hit = False
                
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
                if self.state == "attack":
                    self.state = "idle"
                    
        # Update animations and textures
        self.update_sprite()

    def update_sprite(self):
        # Determine animation state
        if self.hit and self.hit_timer > self.INVINCIBLE_DURATION - 20:
            # First few frames of damage show hit pose
            self.state = "hit"
            # We reuse attack frame for hit pose or make it flash
            sprite_sheet = "attack"
        elif self.attacking:
            self.state = "attack"
            sprite_sheet = "attack"
        elif self.y_vel < 0:
            self.state = "jump"
            sprite_sheet = "jump"
        elif self.y_vel > self.GRAVITY * 3:
            self.state = "fall"
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            self.state = "run"
            sprite_sheet = "run"
        else:
            self.state = "idle"
            sprite_sheet = "idle"

        sprite_sheet_name = f"{sprite_sheet}_{self.direction}"
        sprites = self.sprites.get(sprite_sheet_name, self.sprites["idle_right"])
        
        # Select frame
        frame_idx = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[frame_idx]
        self.animation_count += 1
        
        # Apply hit flashing effect
        if self.hit:
            # Alternate drawing and not drawing (flashing)
            if (self.hit_timer // 4) % 2 == 0:
                # Create a semi-transparent red tinted version
                tinted = self.image.copy()
                tinted.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = tinted

        self.update_mask()

    def get_attack_rect(self):
        """Returns the attack collision box when player is attacking."""
        if not self.attacking:
            return None
            
        # The sword slash reaches in front of the player
        reach = 50
        height = 60
        if self.direction == "right":
            return pygame.Rect(self.rect.right - 20, self.rect.centery - height // 2, reach, height)
        else:
            return pygame.Rect(self.rect.left - reach + 20, self.rect.centery - height // 2, reach, height)

    def draw(self, win, offset_x):
        # Draw player offset by camera horizontal position
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class SlimeEnemy(Entity):
    GRAVITY = 0.8
    ANIMATION_DELAY = 6

    def __init__(self, x, y, patrol_dist=200):
        super().__init__(x, y, 64, 64)
        self.assets_manager = AssetsManager()
        self.sprites = self.assets_manager.load_slime_sprites(target_size=64)
        
        self.image = self.sprites["idle_right"][0]
        self.update_mask()
        
        self.health = 2
        self.speed = 1.8
        self.x_vel = -self.speed  # Start walking left
        self.direction = "left"
        self.state = "walk"
        
        self.start_x = x
        self.patrol_dist = patrol_dist
        self.animation_count = 0
        
        # Hit response
        self.hit = False
        self.hit_timer = 0

    def take_damage(self, damage, source_x):
        if not self.hit:
            self.health -= damage
            self.hit = True
            self.hit_timer = 30  # Invincibility frames
            
            # Jump up and away when hit
            knockback_dir = 1 if self.rect.centerx > source_x else -1
            self.x_vel = knockback_dir * 5
            self.y_vel = -4
            self.fall_count = 0

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.state = "walk"
        # Resume patrol speed in correct direction
        self.x_vel = self.speed if self.direction == "right" else -self.speed

    def hit_head(self):
        self.y_vel = 0

    def loop(self, fps, platforms):
        # Apply gravity
        self.y_vel += min(0.9, (self.fall_count / fps) * self.GRAVITY)
        self.fall_count += 1
        
        # Handle hit recovery
        if self.hit:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.hit = False
                
        # Simple AI Patrol
        if not self.hit:
            # Check patrol limits and turn around
            if self.rect.x < self.start_x - self.patrol_dist:
                self.direction = "right"
                self.x_vel = self.speed
            elif self.rect.x > self.start_x + self.patrol_dist:
                self.direction = "left"
                self.x_vel = -self.speed
                
            # If hit a wall (x_vel was set to 0 by physics)
            if self.x_vel == 0:
                self.direction = "right" if self.direction == "left" else "left"
                self.x_vel = self.speed if self.direction == "right" else -self.speed

        self.update_sprite()

    def update_sprite(self):
        # Select sheet
        if self.y_vel < 0:
            sprite_sheet = "jump"
        elif self.y_vel > self.GRAVITY * 3:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "walk"
        else:
            sprite_sheet = "idle"
            
        sprite_sheet_name = f"{sprite_sheet}_{self.direction}"
        sprites = self.sprites.get(sprite_sheet_name, self.sprites["idle_right"])
        
        frame_idx = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[frame_idx]
        self.animation_count += 1
        
        # Flashing red if hit
        if self.hit:
            if (self.hit_timer // 3) % 2 == 0:
                tinted = self.image.copy()
                tinted.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = tinted
                
        self.update_mask()

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
