import pygame

def get_collided_platform(entity, platforms):
    """Checks if the entity collides with any platform using sprite masks."""
    for platform in platforms:
        if pygame.sprite.collide_mask(entity, platform):
            return platform
    return None

def handle_movement(entity, platforms):
    """
    Moves the entity and resolves horizontal and vertical collisions 
    using pixel-perfect masks.
    """
    # 1. Horizontal Movement & Collision
    if entity.x_vel != 0:
        # Lift up temporarily by 2 pixels to prevent getting stuck on ground/slope overlaps
        entity.rect.y -= 2
        entity.update_mask()
        
        entity.rect.x += int(entity.x_vel)
        entity.update_mask()
        
        collided = get_collided_platform(entity, platforms)
        if collided:
            # Step back pixel-by-pixel until no longer colliding
            step = -1 if entity.x_vel > 0 else 1
            max_steps = abs(int(entity.x_vel)) + 2
            steps = 0
            while pygame.sprite.collide_mask(entity, collided) and steps < max_steps:
                entity.rect.x += step
                entity.update_mask()
                steps += 1
            entity.x_vel = 0
            
        # Restore vertical position
        entity.rect.y += 2
        entity.update_mask()
            
    # 2. Vertical Movement & Collision (Gravity & Jumping)
    if entity.y_vel != 0:
        entity.rect.y += int(entity.y_vel)
        entity.update_mask()
        
        collided = get_collided_platform(entity, platforms)
        if collided:
            if entity.y_vel > 0:
                # Falling / Landing on top of a platform
                step = -1
                max_steps = abs(int(entity.y_vel)) + 2
                steps = 0
                while pygame.sprite.collide_mask(entity, collided) and steps < max_steps:
                    entity.rect.y += step
                    entity.update_mask()
                    steps += 1
                entity.landed()
            elif entity.y_vel < 0:
                # Jumping / Hitting head on the bottom of a platform
                step = 1
                max_steps = abs(int(entity.y_vel)) + 2
                steps = 0
                while pygame.sprite.collide_mask(entity, collided) and steps < max_steps:
                    entity.rect.y += step
                    entity.update_mask()
                    steps += 1
                entity.hit_head()
