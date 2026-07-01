import pygame
import math
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

    def get_hitbox(self):
        return self.rect


class Player(Entity):
    GRAVITY = 0.5
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
        
        # Snare trap state
        self.snared = False
        self.snare_timer = 0

    def jump(self):
        # Jump or Double Jump (cannot jump if snared)
        if self.jump_count < 2 and not self.snared:
            # Crisp jumping velocity matching standard gravity
            self.y_vel = -10.5
            self.jump_count += 1
            self.fall_count = 0
            self.animation_count = 0
            self.state = "jump"

    def attack(self):
        if not self.attacking and self.state != "hit":
            if self.snared:
                self.snare_timer -= 30 # Mash attack to break free early!
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
            
            # Damage breaks the snare
            self.snared = False
            self.snare_timer = 0
            
            # Apply knockback
            knockback_dir = 1 if self.rect.centerx > source_x else -1
            self.x_vel = knockback_dir * 8
            self.y_vel = -4
            self.fall_count = 0

    def get_hitbox(self):
        # Centered hitbox of size 48x80 (narrower than 96x96 to avoid weapons)
        hitbox = pygame.Rect(0, 0, 48, 80)
        hitbox.center = self.rect.center
        return hitbox

    def loop(self, fps, platforms):
        # Apply gravity
        self.y_vel += self.GRAVITY
        if self.y_vel > 12:
            self.y_vel = 12
        self.fall_count += 1
        
        # Handle snare constraint
        if self.snared:
            self.x_vel = 0
            if self.snare_timer <= 0:
                self.snared = False
            else:
                self.snare_timer -= 1
        
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
            sprite_sheet = "hit"
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
    GRAVITY = 0.5
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
        
        # Attack and hit timers
        self.hit = False
        self.hit_timer = 0
        self.charge_timer = 0
        self.attack_cooldown = 0

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
            self.state = "walk"

    def get_hitbox(self):
        # Centered hitbox of size 44x44
        hitbox = pygame.Rect(0, 0, 44, 44)
        hitbox.center = self.rect.center
        return hitbox

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        if self.state == "jump_attack":
            self.state = "walk"
            self.attack_cooldown = 90  # 1.5 seconds cooldown before next leap
        else:
            self.state = "walk"
        # Resume patrol speed in correct direction
        self.x_vel = self.speed if self.direction == "right" else -self.speed

    def hit_head(self):
        self.y_vel = 0

    def loop(self, fps, platforms, player=None, projectiles=None):
        # Apply gravity
        self.y_vel += self.GRAVITY
        if self.y_vel > 12:
            self.y_vel = 12
        self.fall_count += 1
        
        # Decelerate cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Handle hit recovery
        if self.hit:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.hit = False
                
        # Simple AI Patrol and Leaping Attack
        if not self.hit:
            if self.state == "walk":
                # Check distance to player for leap attack trigger
                if player and self.attack_cooldown <= 0:
                    dist_x = player.rect.centerx - self.rect.centerx
                    dist_y = player.rect.centery - self.rect.centery
                    if abs(dist_x) < 180 and abs(dist_y) < 100:
                        self.state = "charge"
                        self.charge_timer = 20  # Charge for ~0.33 seconds
                        self.x_vel = 0
                        self.direction = "right" if dist_x > 0 else "left"

                # If still walking, do normal patrol bounds check
                if self.state == "walk":
                    if self.rect.x < self.start_x - self.patrol_dist:
                        self.direction = "right"
                        self.x_vel = self.speed
                    elif self.rect.x > self.start_x + self.patrol_dist:
                        self.direction = "left"
                        self.x_vel = -self.speed
                        
                    # If hit a wall
                    if self.x_vel == 0:
                        self.direction = "right" if self.direction == "left" else "left"
                        self.x_vel = self.speed if self.direction == "right" else -self.speed
            
            elif self.state == "charge":
                self.x_vel = 0
                self.charge_timer -= 1
                if self.charge_timer <= 0:
                    # Leap attack launched!
                    self.state = "jump_attack"
                    leap_dir = 1 if self.direction == "right" else -1
                    self.x_vel = leap_dir * 6.5
                    self.y_vel = -8.0
                    self.fall_count = 0
            
            elif self.state == "jump_attack":
                # Keep traveling forward during jump attack
                pass

        self.update_sprite()

    def update_sprite(self):
        # Select sheet
        if self.state == "charge":
            sprite_sheet = "idle"
        elif self.y_vel < 0:
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
        if self.state == "charge":
            # Squash down and stretch horizontally to charge up leap
            w = int(self.rect.width * 1.3)
            h = int(self.rect.height * 0.7)
            squashed = pygame.transform.scale(self.image, (w, h))
            render_rect = squashed.get_rect(midbottom=self.rect.midbottom)
            win.blit(squashed, (render_rect.x - offset_x, render_rect.y))
        else:
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class SpearProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.assets_manager = AssetsManager()
        # Extract rock projectile from Forest_Goblin sheet
        sheet = self.assets_manager.load_image("assets/Enemies/Forest_Goblin.png")
        self.image = self.assets_manager.extract_and_scale_sprite(sheet, (1603, 493, 75, 70), 24)
        if direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = 7.0
        self.mask = pygame.mask.from_surface(self.image)
        self.alive = True

    def loop(self, platforms):
        dx = self.speed if self.direction == "right" else -self.speed
        self.rect.x += dx
        
        # Check collision with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                self.alive = False
                break

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class RootSnare(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.assets_manager = AssetsManager()
        sheet = self.assets_manager.load_image("assets/Enemies/Horned_Beast.png")
        # Extract root snare from Horned_Beast.png and scale to size 56
        self.image = self.assets_manager.extract_and_scale_sprite(sheet, (1541, 747, 157, 152), 56)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.mask = pygame.mask.from_surface(self.image)
        
        self.lifetime = 110 # ~2 seconds
        self.snared_player = False
        self.alive = True

    def loop(self, player):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
            
        # Check collision with player
        if not self.snared_player and pygame.sprite.collide_mask(self, player):
            player.snared = True
            player.snare_timer = 90  # 1.5 seconds
            self.snared_player = True
            self.alive = False  # Snare dissolves after successful trap

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class ForestGoblinEnemy(Entity):
    GRAVITY = 0.5
    ANIMATION_DELAY = 6

    def __init__(self, x, y, patrol_dist=200):
        super().__init__(x, y, 72, 72)
        self.assets_manager = AssetsManager()
        self.sprites = self.assets_manager.load_goblin_sprites(target_size=72)
        
        self.image = self.sprites["cloak_right"][0]
        self.update_mask()
        
        self.health = 3
        self.speed = 3.2
        self.x_vel = 0
        self.direction = "left"
        self.state = "cloak"  # cloak, idle, run, melee, throw, hit
        
        self.start_x = x
        self.patrol_dist = patrol_dist
        self.animation_count = 0
        
        # Timers/cooldowns
        self.hit = False
        self.hit_timer = 0
        
        self.shoot_cooldown = 120
        self.action_timer = 0
        self.revealed = False

    def get_hitbox(self):
        # Centered hitbox of size 48x64 (slightly narrower to avoid clipping weapon swings)
        hitbox = pygame.Rect(0, 0, 48, 64)
        hitbox.center = self.rect.center
        return hitbox

    def take_damage(self, damage, source_x):
        # Cannot damage while in leaf cloak camouflage
        if self.state == "cloak":
            return
            
        if not self.hit:
            self.health -= damage
            self.hit = True
            self.hit_timer = 25
            self.state = "hit"
            self.animation_count = 0
            
            knockback_dir = 1 if self.rect.centerx > source_x else -1
            self.x_vel = knockback_dir * 6
            self.y_vel = -3
            self.fall_count = 0

    def get_hitbox(self):
        # Centered hitbox of size 36x64 (much narrower than 72x72 to avoid wide weapon frames)
        hitbox = pygame.Rect(0, 0, 36, 64)
        hitbox.center = self.rect.center
        return hitbox

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        if self.state == "hit":
            self.state = "idle"
            self.x_vel = 0

    def hit_head(self):
        self.y_vel = 0

    def loop(self, fps, platforms, player=None, projectiles=None):
        # Apply gravity
        self.y_vel += self.GRAVITY
        if self.y_vel > 12:
            self.y_vel = 12
        self.fall_count += 1
        
        # Handle hit recovery
        if self.hit:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.hit = False
                self.state = "idle"
                self.x_vel = 0
                
        if not self.hit and player:
            dist_to_player = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            
            # State 1: Leaf Cloak (invisible/invulnerable)
            if self.state == "cloak":
                self.x_vel = 0
                if dist_to_player < 300:
                    self.state = "idle"
                    self.revealed = True
                    self.animation_count = 0
                    
            # State 2: Active Behaviors
            elif self.state in ["idle", "run", "throw", "melee"]:
                # Turn to face player if not extremely close horizontally to prevent rapid jittering
                dx = player.rect.centerx - self.rect.centerx
                if abs(dx) > 10:
                    self.direction = "right" if dx > 0 else "left"
                    
                # Decrement shoot cooldown
                if self.shoot_cooldown > 0:
                    self.shoot_cooldown -= 1
                    
                if self.state == "throw":
                    self.x_vel = 0
                    self.action_timer -= 1
                    # Spawn spear projectile
                    if self.action_timer == 15 and projectiles is not None:
                        spear_y = self.rect.centery - 6
                        spear_x = self.rect.right if self.direction == "right" else self.rect.left
                        proj = SpearProjectile(spear_x, spear_y, self.direction)
                        projectiles.append(proj)
                    if self.action_timer <= 0:
                        self.state = "idle"
                        
                elif self.state == "melee":
                    self.x_vel = 0
                    self.action_timer -= 1
                    if self.action_timer <= 0:
                        self.state = "idle"
                        
                else:
                    # Melee swipe if player is extremely close
                    if dist_to_player < 60:
                        self.state = "melee"
                        self.action_timer = 20
                        self.animation_count = 0
                        if player.state != "hit" and not player.hit:
                            player.take_damage(1, self.rect.centerx)
                            
                    # Throw spear if in range and off cooldown
                    elif dist_to_player < 320 and self.shoot_cooldown <= 0:
                        self.state = "throw"
                        self.action_timer = 30
                        self.shoot_cooldown = 150  # 2.5 second cooldown
                        self.animation_count = 0
                        
                    # Chase player if revealed but too far for melee
                    elif dist_to_player >= 60 and dist_to_player < 400:
                        self.state = "run"
                        # If almost directly aligned horizontally, stand still to prevent jitter
                        if abs(player.rect.centerx - self.rect.centerx) < 15:
                            self.x_vel = 0
                            self.state = "idle"
                        else:
                            self.x_vel = self.speed if self.direction == "right" else -self.speed
                    else:
                        self.state = "idle"
                        self.x_vel = 0
                        
        self.update_sprite()

    def update_sprite(self):
        if self.state == "cloak":
            sprite_sheet = "cloak"
        elif self.state == "hit":
            sprite_sheet = "hit"
        elif self.state == "melee":
            sprite_sheet = "melee"
        elif self.state == "throw":
            sprite_sheet = "throw"
        elif self.x_vel != 0:
            sprite_sheet = "run"
        else:
            sprite_sheet = "idle"
            
        sprite_sheet_name = f"{sprite_sheet}_{self.direction}"
        sprites = self.sprites.get(sprite_sheet_name, self.sprites["idle_right"])
        
        frame_idx = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[frame_idx]
        self.animation_count += 1
        
        if self.hit:
            if (self.hit_timer // 3) % 2 == 0:
                tinted = self.image.copy()
                tinted.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = tinted
                
        self.update_mask()

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class HornedBeastEnemy(Entity):
    GRAVITY = 0.5
    ANIMATION_DELAY = 8

    def __init__(self, x, y):
        super().__init__(x, y, 120, 120)
        self.assets_manager = AssetsManager()
        self.sprites = self.assets_manager.load_horned_beast_sprites(target_size=120)
        
        self.image = self.sprites["idle_right"][0]
        self.update_mask()
        
        self.health = 10
        self.speed = 1.0  # Slow heavyweight
        self.x_vel = -self.speed
        self.direction = "left"
        self.state = "idle"  # idle, roar, snare, hit
        
        self.start_x = x
        self.animation_count = 0
        
        self.hit = False
        self.hit_timer = 0
        
        # Ability cooldowns
        self.roar_cooldown = 240 # 4 seconds
        self.snare_cooldown = 360 # 6 seconds
        self.action_timer = 0

    def take_damage(self, damage, source_x):
        if not self.hit:
            self.health -= damage
            self.hit = True
            self.hit_timer = 30
            self.state = "hit"
            self.animation_count = 0
            
            # Heavy beast has minimal knockback
            knockback_dir = 1 if self.rect.centerx > source_x else -1
            self.x_vel = knockback_dir * 2
            self.y_vel = -2
            self.fall_count = 0

    def get_hitbox(self):
        # Centered hitbox of size 80x100
        hitbox = pygame.Rect(0, 0, 80, 100)
        hitbox.center = self.rect.center
        return hitbox

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        if self.state == "hit":
            self.state = "idle"
            self.x_vel = 0

    def hit_head(self):
        self.y_vel = 0

    def loop(self, fps, platforms, player=None, projectiles=None):
        # Apply gravity
        self.y_vel += self.GRAVITY
        if self.y_vel > 12:
            self.y_vel = 12
        self.fall_count += 1
        
        if self.hit:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.hit = False
                self.state = "idle"
                self.x_vel = 0
                
        if not self.hit and player:
            dist_to_player = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            
            # Decrement ability timers
            if self.roar_cooldown > 0:
                self.roar_cooldown -= 1
            if self.snare_cooldown > 0:
                self.snare_cooldown -= 1
                
            # Face player
            if player.rect.centerx > self.rect.centerx:
                self.direction = "right"
            else:
                self.direction = "left"
                
            if self.state == "roar":
                self.x_vel = 0
                self.action_timer -= 1
                # Trigger Forest Roar screenshake & AoE knockback
                if self.action_timer == 25:
                    if hasattr(player, "game_ref") and player.game_ref:
                        player.game_ref.screenshake = 25
                    if dist_to_player < 220:
                        player.take_damage(1, self.rect.centerx)
                        # Massive knockback from roar shockwave
                        player.x_vel = (1 if player.rect.centerx > self.rect.centerx else -1) * 12
                        player.y_vel = -5
                if self.action_timer <= 0:
                    self.state = "idle"
                    self.roar_cooldown = 300
                    
            elif self.state == "snare":
                self.x_vel = 0
                self.action_timer -= 1
                # Spawn snare trap on ground under player feet
                if self.action_timer == 20 and projectiles is not None:
                    snare_x = player.rect.centerx
                    snare_y = player.rect.bottom
                    snare = RootSnare(snare_x, snare_y)
                    projectiles.append(snare)
                if self.action_timer <= 0:
                    self.state = "idle"
                    self.snare_cooldown = 420
                    
            else:
                # Combat Decision AI
                if dist_to_player < 180 and self.roar_cooldown <= 0:
                    self.state = "roar"
                    self.action_timer = 50
                    self.animation_count = 0
                elif dist_to_player < 380 and self.snare_cooldown <= 0:
                    self.state = "snare"
                    self.action_timer = 40
                    self.animation_count = 0
                elif dist_to_player < 500:
                    # Patrol slowly towards player
                    self.x_vel = self.speed if self.direction == "right" else -self.speed
                else:
                    self.x_vel = 0
                    
        self.update_sprite()

    def update_sprite(self):
        if self.state == "hit":
            sprite_sheet = "hit"
        elif self.state in ["roar", "snare"]:
            sprite_sheet = "slam"
        else:
            sprite_sheet = "idle"
            
        sprite_sheet_name = f"{sprite_sheet}_{self.direction}"
        sprites = self.sprites.get(sprite_sheet_name, self.sprites["idle_right"])
        
        frame_idx = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[frame_idx]
        self.animation_count += 1
        
        if self.hit:
            if (self.hit_timer // 3) % 2 == 0:
                tinted = self.image.copy()
                tinted.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = tinted
                
        self.update_mask()

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

