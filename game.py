import sys
import pygame
from os.path import join

from assets_manager import AssetsManager
from entities import Player
from level import Level
from physics import handle_movement

class Game:
    FPS = 60
    WIDTH, HEIGHT = 1000, 800
    SCROLL_AREA_WIDTH = 250
    SCROLL_AREA_HEIGHT = 200

    def __init__(self, window):
        self.window = window
        self.clock = pygame.time.Clock()
        self.assets_manager = AssetsManager()
        
        # Game State
        # menu, story_intro, playing, game_over, victory
        self.state = "menu"
        self.reset_game()

    def reset_game(self):
        # Reset level, player, camera
        self.level = Level(self.WIDTH, self.HEIGHT)
        self.player = Player(self.level.player_spawn_x, self.level.player_spawn_y)
        self.player.game_ref = self  # Give player access to screenshake/score
        
        self.offset_x = 0
        self.offset_y = 0
        self.screenshake = 0
        self.score = 0
        self.projectiles = []  # For Goblin Spears and Golem Snares
        
        # Load heart HUD image directly
        self.ui_heart = pygame.transform.scale(self.assets_manager.load_platform_image("ui_heart.png"), (28, 28))
        
        # Load tiled background
        self.bg_tile = self.assets_manager.load_background_tile(self.level.background_name)
        # Always scale the background tile to cover the full window size (1000x800)
        # to prevent performance drops (low FPS) and resolve tiled background clutter.
        self.bg_tile = pygame.transform.scale(self.bg_tile, (self.WIDTH, self.HEIGHT))
        self.bg_w, self.bg_h = self.bg_tile.get_size()
        
        # Pre-render background tiling list (only enough tiles to cover the screen scrolling area)
        self.bg_tiles = []
        for i in range(-1, self.WIDTH // self.bg_w + 2):
            for j in range(-1, self.HEIGHT // self.bg_h + 2):
                self.bg_tiles.append((i * self.bg_w, j * self.bg_h))


    def run(self):
        while True:
            self.clock.tick(self.FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_SPACE:
                        self.state = "story_intro"
                elif self.state == "story_intro":
                    if event.key == pygame.K_SPACE:
                        self.state = "playing"
                elif self.state == "playing":
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    elif event.key in [pygame.K_x, pygame.K_j]:
                        self.player.attack()
                elif self.state in ["game_over", "victory"]:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = "playing"
                    elif event.key == pygame.K_m:
                        self.reset_game()
                        self.state = "menu"

    def update(self):
        if self.state != "playing":
            return
            
        # 1. Keyboard Movement Inputs for Player
        keys = pygame.key.get_pressed()
        self.player.x_vel = 0
        
        # Decay camera screenshake
        if self.screenshake > 0:
            self.screenshake -= 1

        # Block movement during hit knockback, attacking, or being snared
        if self.player.state != "hit" and not self.player.attacking and not self.player.snared:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.x_vel = -5
                if self.player.direction != "left":
                    self.player.direction = "left"
                    self.player.animation_count = 0
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.x_vel = 5
                if self.player.direction != "right":
                    self.player.direction = "right"
                    self.player.animation_count = 0

        # 2. Physics & Movement Resolution
        handle_movement(self.player, self.level.platforms)
        
        for enemy in self.level.enemies:
            handle_movement(enemy, self.level.platforms)
            # Pass player reference and projectiles list to smart enemies (Goblin, Beast)
            try:
                enemy.loop(self.FPS, self.level.platforms, self.player, self.projectiles)
            except TypeError:
                enemy.loop(self.FPS, self.level.platforms)
            
        # Update projectiles and traps
        for proj in self.projectiles:
            if type(proj).__name__ == "RootSnare":
                proj.loop(self.player)
            else:
                proj.loop(self.level.platforms)
        self.projectiles = [p for p in self.projectiles if p.alive]
            
        # 3. Entity loops
        self.player.loop(self.FPS, self.level.platforms)
        
        # 4. Check for Hazards (Spikes) Collisions
        for hazard in self.level.hazards:
            if pygame.sprite.collide_mask(self.player, hazard):
                self.player.take_damage(1, hazard.rect.centerx)
                
        # 5. Check for Interactive Objects (springs, mushrooms)
        for obj in self.level.interactive_objects:
            obj.update()
            if pygame.sprite.collide_mask(self.player, obj):
                if self.player.y_vel >= -0.5: # only bounce when falling or moving down
                    obj.trigger_bounce(self.player)
                    self.score += 5 # small reward for bouncy physics trick
                    
        # 6. Check for Collectible Items (coins, chests)
        for item in self.level.collectibles:
            if not item.collected and pygame.sprite.collide_mask(self.player, item):
                item.collected = True
                if item.item_type == "coin":
                    self.score += 10
                elif item.item_type == "chest":
                    self.score += 200
                    # Chest is the final source code; complete the level!
                    self.state = "victory"
                
        # 7. Check Player Attack overlap with Enemies / Projectiles
        if self.player.attacking:
            attack_rect = self.player.get_attack_rect()
            if attack_rect:
                # Attack enemies
                for enemy in self.level.enemies:
                    if attack_rect.colliderect(enemy.get_hitbox()):
                        # Goblins in leaf cloak are immune
                        if hasattr(enemy, "state") and enemy.state == "cloak":
                            continue
                        enemy.take_damage(1, self.player.rect.centerx)
                        if enemy.health <= 0:
                            self.score += 50
                            
                # Deflect spears
                for proj in self.projectiles:
                    if type(proj).__name__ == "SpearProjectile":
                        if attack_rect.colliderect(proj.rect):
                            proj.alive = False
                            self.score += 25 # Deflection reward!
                        
        # Remove dead enemies
        self.level.enemies = [e for e in self.level.enemies if e.health > 0]
        
        # 8. Check Enemy attack contact on Player (standard contact damage)
        if not self.player.hit:
            # Check contact with active enemies
            for enemy in self.level.enemies:
                if hasattr(enemy, "state") and enemy.state == "cloak":
                    continue # Cloaked goblins don't deal damage by contact
                if self.player.get_hitbox().colliderect(enemy.get_hitbox()):
                    self.player.take_damage(1, enemy.rect.centerx)
                    
            # Check contact with projectiles (Spears)
            for proj in self.projectiles:
                if type(proj).__name__ == "SpearProjectile":
                    if pygame.sprite.collide_mask(self.player, proj):
                        self.player.take_damage(1, proj.rect.centerx)
                        proj.alive = False

        # 7. Check Boundaries (Falling out of screen or level)
        if self.player.rect.top > self.HEIGHT + 100:
            self.player.take_damage(5, self.player.rect.centerx) # Instantly die if fall in pit
            
        # Check Health / Game Over
        if self.player.health <= 0:
            self.state = "game_over"
            
        # Check Victory Checkpoint
        if self.player.rect.x >= self.level.finish_x:
            self.state = "victory"

        # 8. Parallax Camera Scrolling
        # Horizontal scrolling
        if ((self.player.rect.right - self.offset_x >= self.WIDTH - self.SCROLL_AREA_WIDTH) and self.player.x_vel > 0):
            self.offset_x += self.player.x_vel
        elif ((self.player.rect.left - self.offset_x <= self.SCROLL_AREA_WIDTH) and self.player.x_vel < 0):
            self.offset_x += self.player.x_vel
            
        # Restrict camera boundaries
        self.offset_x = max(0, min(self.offset_x, self.level.finish_x + 300 - self.WIDTH))
        
        # Lock vertical camera scrolling
        self.offset_y = 0

    def draw_hud(self):
        # 1. Health Hearts
        heart_w, heart_h = self.ui_heart.get_size()
        spacing = 35
        start_x = 30
        start_y = 40
        for i in range(self.player.max_health):
            x = start_x + i * spacing
            y = start_y
            if i >= self.player.health:
                # Draw empty/darkened heart
                dark_heart = self.ui_heart.copy()
                dark_heart.fill((40, 40, 40, 180), special_flags=pygame.BLEND_RGBA_MULT)
                self.window.blit(dark_heart, (x, y))
            else:
                self.window.blit(self.ui_heart, (x, y))
                
        # 2. Level Progress Bar
        bar_x = 750
        bar_y = 30
        bar_w = 200
        bar_h = 16
        # Draw frame
        pygame.draw.rect(self.window, (60, 60, 60), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), 2)
        pygame.draw.rect(self.window, (30, 30, 30), (bar_x, bar_y, bar_w, bar_h))
        
        # Calculate progress ratio
        progress = min(1.0, max(0.0, self.player.rect.x / self.level.finish_x))
        pygame.draw.rect(self.window, (40, 200, 100), (bar_x, bar_y, int(bar_w * progress), bar_h))
        
        # Text labels on HUD
        font = pygame.font.SysFont("Consolas", 18, bold=True)
        lbl_health = font.render("HERO LIFE", True, (255, 255, 255))
        self.window.blit(lbl_health, (start_x, start_y - 24))
        
        lbl_progress = font.render(f"PROGRESS {int(progress * 100)}%", True, (255, 255, 255))
        self.window.blit(lbl_progress, (bar_x + 35, bar_y - 22))

        # 3. Score UI (Centered top)
        lbl_score = font.render(f"SCORE: {self.score:05d}", True, (255, 215, 0))
        self.window.blit(lbl_score, (self.WIDTH // 2 - 60, start_y - 10))

    def draw(self):
        # Calculate screen shake offsets
        import random
        shake_x = 0
        shake_y = 0
        if self.screenshake > 0:
            shake_x = random.randint(-self.screenshake, self.screenshake)
            shake_y = random.randint(-self.screenshake, self.screenshake)

        # 1. Tile Tiled Parallax Background
        for tile_pos in self.bg_tiles:
            x = tile_pos[0] - int(self.offset_x * 0.1) % self.bg_w + shake_x
            y = tile_pos[1] - int(self.offset_y * 0.1) % self.bg_h + shake_y
            self.window.blit(self.bg_tile, (x, y))

        # 2. Draw Decorations (Trees, stumps)
        for decor in self.level.decorations:
            decor.draw(self.window, self.offset_x + shake_x, self.offset_y + shake_y)

        # 3. Draw Platforms & Spikes (with screenshake offsets)
        for platform in self.level.platforms:
            self.window.blit(platform.image, (platform.rect.x - self.offset_x - shake_x, platform.rect.y - shake_y))
            
        for hazard in self.level.hazards:
            self.window.blit(hazard.image, (hazard.rect.x - self.offset_x - shake_x, hazard.rect.y - shake_y))

        # 4. Draw Collectibles
        for item in self.level.collectibles:
            item.rect.y -= shake_y
            item.draw(self.window, self.offset_x + shake_x)
            item.rect.y += shake_y

        # 5. Draw Interactive springs
        for obj in self.level.interactive_objects:
            obj.rect.y -= shake_y
            obj.draw(self.window, self.offset_x + shake_x)
            obj.rect.y += shake_y

        # 6. Draw Projectiles and Snares
        for proj in self.projectiles:
            proj.rect.y -= shake_y
            proj.draw(self.window, self.offset_x + shake_x)
            proj.rect.y += shake_y

        # 7. Draw Enemies
        for enemy in self.level.enemies:
            enemy.rect.y -= shake_y
            enemy.draw(self.window, self.offset_x + shake_x)
            enemy.rect.y += shake_y

        # 8. Draw Player
        self.player.rect.y -= shake_y
        self.player.draw(self.window, self.offset_x + shake_x)
        self.player.rect.y += shake_y

        # 9. Draw HUD overlays
        if self.state == "playing":
            self.draw_hud()
        
        # 10. State Screens
        if self.state == "menu":
            self.draw_menu_screen()
        elif self.state == "story_intro":
            self.draw_story_intro_screen()
        elif self.state == "game_over":
            self.draw_game_over_screen()
        elif self.state == "victory":
            self.draw_victory_screen()

        pygame.display.update()

    def draw_overlay_box(self, width, height, title):
        """Draws a beautifully styled retro overlay window."""
        box_x = (self.WIDTH - width) // 2
        box_y = (self.HEIGHT - height) // 2
        
        # Semi-transparent dark background
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 160))
        self.window.blit(overlay, (0, 0))
        
        # Central Box Background
        box_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        box_surf.fill((25, 25, 35, 240))
        pygame.draw.rect(box_surf, (255, 94, 0), (0, 0, width, height), 4) # Orange Border
        pygame.draw.rect(box_surf, (255, 255, 255), (4, 4, width-8, height-8), 2) # Inner White Border
        self.window.blit(box_surf, (box_x, box_y))
        
        # Title
        font_title = pygame.font.SysFont("Courier New", 32, bold=True)
        txt_title = font_title.render(title, True, (255, 94, 0))
        title_rect = txt_title.get_rect(center=(self.WIDTH // 2, box_y + 35))
        self.window.blit(txt_title, title_rect)
        
        return box_x, box_y

    def draw_menu_screen(self):
        box_x, box_y = self.draw_overlay_box(700, 480, "FOREST CHRONICLES")
        
        # Custom retro menu font rendering
        font_normal = pygame.font.SysFont("Consolas", 18, bold=True)
        font_action = pygame.font.SysFont("Consolas", 22, bold=True)
        
        texts = [
            "Welcome, Adventurer!",
            "Embark on a pixelated retro quest to find",
            "the lost source code of the Forest Realm.",
            "",
            "=== CONTROLS ===",
            "Move Left/Right : Left/Right Arrow OR A/D Keys",
            "Jump / Dbl Jump : Spacebar",
            "Attack Enemies  : X Key OR J Key",
            "Pause/Restart   : R Key (when dead/won)"
        ]
        
        for i, text in enumerate(texts):
            color = (200, 200, 200) if "CONTROLS" not in text else (255, 200, 50)
            rendered = font_normal.render(text, True, color)
            self.window.blit(rendered, (box_x + 50, box_y + 90 + i * 28))
            
        # Glowing action text
        txt_action = font_action.render("Press SPACEBAR to start your journey", True, (0, 255, 120))
        action_rect = txt_action.get_rect(center=(self.WIDTH // 2, box_y + 420))
        # Animate flashing
        if (pygame.time.get_ticks() // 400) % 2 == 0:
            self.window.blit(txt_action, action_rect)

    def draw_story_intro_screen(self):
        box_x, box_y = self.draw_overlay_box(750, 450, "THE PROPHECY")
        
        font_normal = pygame.font.SysFont("Courier New", 18, bold=True)
        font_action = pygame.font.SysFont("Consolas", 22, bold=True)
        
        story_lines = [
            "Deep within the digital woods, the legendary",
            "Physics is collapsing, tiles are floating!",
            "",
            "Our brave hero must venture through the terrain,",
            "leap across spikes, defeat the guard slimes,",
            "and reach the golden gates on the far right.",
            "",
            "Prepare your sword and steady your boots..."
        ]
        
        for i, line in enumerate(story_lines):
            rendered = font_normal.render(line, True, (240, 240, 250))
            self.window.blit(rendered, (box_x + 50, box_y + 90 + i * 28))
            
        txt_action = font_action.render("Press SPACEBAR to begin the quest", True, (0, 220, 255))
        action_rect = txt_action.get_rect(center=(self.WIDTH // 2, box_y + 390))
        if (pygame.time.get_ticks() // 400) % 2 == 0:
            self.window.blit(txt_action, action_rect)

    def draw_game_over_screen(self):
        box_x, box_y = self.draw_overlay_box(600, 300, "HERO DEFEATED")
        
        font_normal = pygame.font.SysFont("Consolas", 20, bold=True)
        font_restart = pygame.font.SysFont("Consolas", 22, bold=True)
        
        lbl_msg = font_normal.render("You fell victim to the forest hazards...", True, (255, 100, 100))
        lbl_msg_rect = lbl_msg.get_rect(center=(self.WIDTH // 2, box_y + 110))
        self.window.blit(lbl_msg, lbl_msg_rect)
        
        lbl_restart = font_restart.render("Press 'R' to Restart or 'M' for Menu", True, (255, 255, 255))
        lbl_restart_rect = lbl_restart.get_rect(center=(self.WIDTH // 2, box_y + 200))
        self.window.blit(lbl_restart, lbl_restart_rect)

    def draw_victory_screen(self):
        box_x, box_y = self.draw_overlay_box(650, 360, "QUEST COMPLETE!")
        
        font_normal = pygame.font.SysFont("Courier New", 18, bold=True)
        font_sub = pygame.font.SysFont("Consolas", 22, bold=True)
        
        lines = [
            "Victory! You reached the Golden Gates",
            "and restored balance to the Forest Realm.",
            "",
            "The Chronicle Forest is safe once more.",
            "Thank you for playing!"
        ]
        
        for i, line in enumerate(lines):
            color = (255, 220, 50) if i == 0 else (200, 255, 200)
            rendered = font_normal.render(line, True, color)
            self.window.blit(rendered, (box_x + 60, box_y + 95 + i * 28))
            
        lbl_restart = font_sub.render("Press 'R' to Play Again or 'M' for Menu", True, (0, 255, 120))
        lbl_restart_rect = lbl_restart.get_rect(center=(self.WIDTH // 2, box_y + 290))
        self.window.blit(lbl_restart, lbl_restart_rect)
