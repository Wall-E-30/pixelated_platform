import os
import pygame

def get_bounding_boxes(image_path, min_size=(10, 10)):
    """Loads an image and returns a list of Rects representing individual non-transparent sprites."""
    if not os.path.exists(image_path):
        print(f"Error: {image_path} does not exist.")
        return []
        
    pygame.init()
    try:
        surface = pygame.image.load(image_path).convert_alpha()
    except Exception as e:
        print(f"Error loading {image_path}: {e}")
        return []
        
    width, height = surface.get_size()
    # Create mask of non-transparent pixels
    mask = pygame.mask.from_surface(surface)
    
    # List of rects already processed
    processed = pygame.mask.Mask((width, height))
    bounding_boxes = []
    
    # We scan pixel by pixel to find connected components
    for y in range(height):
        for x in range(width):
            if mask.get_at((x, y)) and not processed.get_at((x, y)):
                # Found a new component. Let's find its connected region
                component_mask = mask.connected_component((x, y))
                # Add this component to processed so we don't scan it again
                processed.draw(component_mask, (0, 0))
                
                # Get the bounding box of this component
                rect = component_mask.get_bounding_rects()
                if rect:
                    r = rect[0]
                    if r.width >= min_size[0] and r.height >= min_size[1]:
                        bounding_boxes.append(r)
                        
    return bounding_boxes

def main():
    targets = {
        "Goblin": "assets/Enemies/Copilot_20260628_094646.png",
        "Golem": "assets/Enemies/Copilot_20260628_094708.png",
        "Goblin Variant": "assets/Enemies/Copilot_20260628_095324.png",
        "Root Golem": "assets/Enemies/Copilot_20260628_100026.png",
    }
    
    pygame.init()
    # Set a tiny headless window because Pygame needs a display mode to convert_alpha()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    for name, path in targets.items():
        print(f"\nAnalyzing {name} ({path})...")
        boxes = get_bounding_boxes(path, min_size=(30, 30))
        print(f"Found {len(boxes)} sprites:")
        for i, box in enumerate(boxes):
            print(f"  Box {i}: Rect(x={box.x}, y={box.y}, w={box.width}, h={box.height})")

if __name__ == "__main__":
    main()
