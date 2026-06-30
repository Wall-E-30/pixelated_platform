import pygame

def get_collided_platform(entity, platforms):
    """Checks if the entity's hitbox collides with any platform using bounding boxes (AABB)."""
    hitbox = entity.get_hitbox()
    for platform in platforms:
        if hitbox.colliderect(platform.rect):
            return platform
    return None

def handle_movement(entity, platforms):
    """
    Moves the entity and resolves horizontal and vertical collisions 
    using bounding boxes (AABBs) for pixel-perfect stability.
    """
    # 1. Horizontal Movement & Collision
    if entity.x_vel != 0:
        entity.rect.x += int(entity.x_vel)
        
        # Check for platform collision using entity's hitbox
        hitbox = entity.get_hitbox()
        for platform in platforms:
            if hitbox.colliderect(platform.rect):
                if entity.x_vel > 0:
                    # Moving right -> align right of hitbox to left of platform
                    entity.rect.x += platform.rect.left - hitbox.right
                elif entity.x_vel < 0:
                    # Moving left -> align left of hitbox to right of platform
                    entity.rect.x += platform.rect.right - hitbox.left
                entity.x_vel = 0
                break
        entity.update_mask()

    # 2. Vertical Movement & Collision (Gravity & Jumping)
    if entity.y_vel != 0:
        entity.rect.y += int(entity.y_vel)
        
        # Check for platform collision using entity's hitbox
        hitbox = entity.get_hitbox()
        for platform in platforms:
            if hitbox.colliderect(platform.rect):
                if entity.y_vel > 0:
                    # Falling down -> align bottom of hitbox to top of platform
                    entity.rect.y += platform.rect.top - hitbox.bottom
                    entity.landed()
                elif entity.y_vel < 0:
                    # Hitting head -> align top of hitbox to bottom of platform
                    entity.rect.y += platform.rect.bottom - hitbox.top
                    entity.hit_head()
                break
        entity.update_mask()
