import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


import pygame
import carla
from src.vehicle import Vehicle
from src.display import Display
from src.world import World
from src.server import CarlaServer

def control_vehicle_with_keyboard(vehicle):
    pygame.init()

    # Pygame screen setup
    screen = pygame.display.set_mode((300, 300))
    clock = pygame.time.Clock()

    # Initialize control values
    throttle = 0.0
    steering = 0.0
    reverse = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    throttle = 1.0
                elif event.key == pygame.K_s:
                    throttle = -1.0
                elif event.key == pygame.K_a:
                    steering = -1.0
                elif event.key == pygame.K_d:
                    steering = 1.0
                elif event.key == pygame.K_q:
                    reverse = not reverse

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_w, pygame.K_s):
                    throttle = 0.0
                elif event.key in (pygame.K_a, pygame.K_d):
                    steering = 0.0

        # Apply controls to the vehicle
        control = carla.VehicleControl()
        control.throttle = throttle if not reverse else -throttle
        control.steer = steering

        vehicle.apply_control(control)

        # Clear the screen
        screen.fill((255, 255, 255))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

def main():
    CarlaServer.initialize_server()
    world = World()
    
    ego_vehicle = Vehicle(world=world.get_world())
    ego_vehicle.spawn_vehicle()

    control_vehicle_with_keyboard(ego_vehicle.get_vehicle())

    while True:
        try:
            world.tick()
        except KeyboardInterrupt:
            ego_vehicle.destroy_vehicle()
            world.close()
            CarlaServer.close_server()
            break
    
if __name__ == '__main__':
    main()