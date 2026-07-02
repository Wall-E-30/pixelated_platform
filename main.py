import pygame
from game import Game

def main():
    pygame.init()
    
    # Establish the resolution
    WIDTH, HEIGHT = 1000, 800
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chronicles of the Pixel Realm")
    
    # Start the game
    game = Game(window)
    game.run()

if __name__ == "__main__":
    main()
