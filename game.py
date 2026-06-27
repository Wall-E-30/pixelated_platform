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
        
        self.offset_x = 0
        self.offset_y = 0
        
        # Load tiled background
        self.bg_tile = self.assets_manager.load_background_tile(self.level.background_name)
        self.bg_w, self.bg_h = self.bg_tile.get_size()
        
        # Pre-render background tiling list
        self.bg_tiles = []
        for i in range(-1, (self.level.finish_x + 500) // self.bg_w + 2):
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
        
        # Block movement during hit knockback or attacking
        if self.player.state != "hit" and not self.player.attacking:
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
            enemy.loop(self.FPS, self.level.platforms)
            
        # 3. Entity loops
        self.player.loop(self.FPS, self.level.platforms)
        
        # 4. Check for Hazards (Spikes) Collisions
        for hazard in self.level.hazards:
            if pygame.sprite.collide_mask(self.player, hazard):
                self.player.take_damage(1, hazard.rect.centerx)
                
        # 5. Check Player Attack overlap with Enemies
        if self.player.attacking:
            attack_rect = self.player.get_attack_rect()
            if attack_rect:
                for enemy in self.level.enemies:
                    if attack_rect.colliderect(enemy.rect):
                        enemy.take_damage(1, self.player.rect.centerx)
                        
        # Remove dead enemies
        self.level.enemies = [e for e in self.level.enemies if e.health > 0]
        
        # 6. Check Enemy attack contact on Player
        if not self.player.hit:
            for enemy in self.level.enemies:
                if pygame.sprite.collide_mask(self.player, enemy):
                    self.player.take_damage(1, enemy.rect.centerx)

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
        
        # Vertical scrolling (if climbing high)
        if self.player.rect.top - self.offset_y < self.SCROLL_AREA_HEIGHT:
            self.offset_y += (self.player.rect.top - self.offset_y - self.SCROLL_AREA_HEIGHT) * 0.1
        elif self.player.rect.bottom - self.offset_y > self.HEIGHT - self.SCROLL_AREA_HEIGHT:
            self.offset_y += (self.player.rect.bottom - self.offset_y - (self.HEIGHT - self.SCROLL_AREA_HEIGHT)) * 0.1
            
        self.offset_y = max(-300, min(self.offset_y, 0))

    def draw_heart(self, surface, x, y, size):
        """Helper to draw a pixelated glowing heart shape on the HUD."""
        # Main heart body (two top circles + lower triangle)
        # Left circle
        pygame.draw.circle(surface, (255, 60, 60), (x - size // 4, y - size // 4), size // 4)
        # Right circle
        pygame.draw.circle(surface, (255, 60, 60), (x + size // 4, y - size // 4), size // 4)
        # Pointy bottom triangle
        points = [
            (x - size // 2, y - size // 8),
            (x + size // 2, y - size // 8),
            (x, y + size // 2)
        ]
        pygame.draw.polygon(surface, (255, 60, 60), points)
        
        # Soft highlight circle inside left lobe
        pygame.draw.circle(surface, (255, 180, 180), (x - size // 3, y - size // 3), size // 10)

    def draw_hud(self):
        # 1. Health Hearts
        heart_size = 28
        spacing = 35
        start_x = 30
        start_y = 40
        for i in range(self.player.max_health):
            # Draw empty/black heart back for missing health
            if i >= self.player.health:
                pygame.draw.circle(self.window, (40, 40, 40), (start_x + i * spacing - heart_size // 4, start_y - heart_size // 4), heart_size // 4)
                pygame.draw.circle(self.window, (40, 40, 40), (start_x + i * spacing + heart_size // 4, start_y - heart_size // 4), heart_size // 4)
                points = [
                    (start_x + i * spacing - heart_size // 2, start_y - heart_size // 8),
                    (start_x + i * spacing + heart_size // 2, start_y - heart_size // 8),
                    (start_x + i * spacing, start_y + heart_size // 2)
                ]
                pygame.draw.polygon(self.window, (40, 40, 40), points)
            else:
                self.draw_heart(self.window, start_x + i * spacing, start_y, heart_size)
                
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
        self.window.blit(lbl_health, (start_x - 10, start_y - 32))
        
        lbl_progress = font.render(f"PROGRESS {int(progress * 100)}%", True, (255, 255, 255))
        self.window.blit(lbl_progress, (bar_x + 50, bar_y - 22))

    def draw(self):
        # 1. Tile Tiled Parallax Background
        # Tiled with offset_x and offset_y
        for tile_pos in self.bg_tiles:
            # Tiled background follows camera scroll at 0.1x speed (deep background effect)
            x = tile_pos[0] - int(self.offset_x * 0.1) % self.bg_w
            y = tile_pos[1] - int(self.offset_y * 0.1) % self.bg_h
            self.window.blit(self.bg_tile, (x, y))

        # 2. Draw Decorations (Trees, stumps)
        for decor in self.level.decorations:
            decor.draw(self.window, self.offset_x, self.offset_y)

        # 3. Draw Platforms & Spikes
        for platform in self.level.platforms:
            platform.draw(self.window, self.offset_x)
            
        for hazard in self.level.hazards:
            hazard.draw(self.window, self.offset_x)

        # 4. Draw Enemies
        for enemy in self.level.enemies:
            enemy.draw(self.window, self.offset_x)

        # 5. Draw Player
        self.player.draw(self.window, self.offset_x)

        # 6. Draw HUD overlays
        if self.state == "playing":
            self.draw_hud()
            # Draw attack range outline for debug/visual clarity if desired (uncomment if helpful)
            # if self.player.attacking:
            #     att_rect = self.player.get_attack_rect()
            #     if att_rect:
            #         pygame.draw.rect(self.window, (255,0,0), (att_rect.x - self.offset_x, att_rect.y, att_rect.width, att_rect.height), 2)
        
        # 7. State Screens
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
            "Code of Antigravity has been shattered by corrupt",
            "slimes. Physics is collapsing, tiles are floating!",
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
            "The Code of Antigravity is safe once more.",
            "Thank you for playing!"
        ]
        
        for i, line in enumerate(lines):
            color = (255, 220, 50) if i == 0 else (200, 255, 200)
            rendered = font_normal.render(line, True, color)
            self.window.blit(rendered, (box_x + 60, box_y + 95 + i * 28))
            
        lbl_restart = font_sub.render("Press 'R' to Play Again or 'M' for Menu", True, (0, 255, 120))
        lbl_restart_rect = lbl_restart.get_rect(center=(self.WIDTH // 2, box_y + 290))
        self.window.blit(lbl_restart, lbl_restart_rect)
