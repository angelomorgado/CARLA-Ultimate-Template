import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


import pygame
import carla
from src.vehicle import Vehicle
from src.display import Display
from src.world import World
from src.server import CarlaServer

class KeyboardControl:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        pygame.init()
        self.throttle = 0.0
        self.steering = 0.0
        self.reverse = False

    def initialize(self):
        # Pygame screen setup
        self.screen = pygame.display.set_mode((300, 300))
        self.clock = pygame.time.Clock()

    def update_controls(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.throttle = 1.0
                elif event.key == pygame.K_s:
                    self.throttle = -1.0
                elif event.key == pygame.K_a:
                    self.steering = -1.0
                elif event.key == pygame.K_d:
                    self.steering = 1.0
                elif event.key == pygame.K_q:
                    self.reverse = not self.reverse

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_w, pygame.K_s):
                    self.throttle = 0.0
                elif event.key in (pygame.K_a, pygame.K_d):
                    self.steering = 0.0

    def apply_controls(self):
        # Apply controls to the vehicle
        control = carla.VehicleControl()
        control.throttle = self.throttle if not self.reverse else -self.throttle
        control.steer = self.steering
        self.vehicle.apply_control(control)

    def tick(self):
        # Clear the screen
        self.screen.fill((255, 255, 255))

        # Update controls and apply them
        self.update_controls()
        self.apply_controls()

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        self.clock.tick(60)


def main():
    CarlaServer.initialize_server()
    world = World()
    
    ego_vehicle = Vehicle(world=world.get_world())
    ego_vehicle.spawn_vehicle()

    keyboard_control = KeyboardControl(ego_vehicle.get_vehicle())
    keyboard_control.initialize()
    
    world.place_spectator_behind_vehicle(ego_vehicle.get_vehicle())
    # world.place_spectator_above_vehicle(ego_vehicle.get_vehicle())

    while True:
        try:
            world.tick()
            keyboard_control.tick()
        except KeyboardInterrupt:
            ego_vehicle.destroy_vehicle()
            world.close()
            CarlaServer.close_server()
            break
    
if __name__ == '__main__':
    main()