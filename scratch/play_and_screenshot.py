import os
import sys
sys.path.append(os.getcwd())
import pygame
from game import Game

def main():
    pygame.init()
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    try:
        window = pygame.display.set_mode((1000, 800))
    except Exception:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        window = pygame.display.set_mode((1000, 800))
        
    game = Game(window)
    game.state = "playing" # Bypass menu and intro
    game.reset_game()
    game.draw()
    
    os.makedirs("scratch", exist_ok=True)
    pygame.image.save(window, "scratch/game_screenshot.png")
    print("Screenshot saved to scratch/game_screenshot.png")
    pygame.quit()

if __name__ == "__main__":
    main()
