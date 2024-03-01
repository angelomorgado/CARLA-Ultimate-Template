'''
scene_setup.py

- This script demonstrates how to use this template to create and configure a scene in Carla.
- It provides an overview of how to create a Carla server, a Carla client, a vehicle, and a display.
'''

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.vehicle import Vehicle
import configuration
from src.display import Display
from src.world import World
from src.server import CarlaServer
import carla
import random

def spawn_walkers(world, n):
    # Get the blueprint of the walker
    walker_bp = random.choice(world.get_blueprint_library().filter('walker.pedestrian.*'))

    for _ in range(n):
        # Spawn point for the walker
        spawn_point = carla.Transform()
        spawn_point.location = world.get_random_location_from_navigation()

        # Spawn the walker
        walker = world.spawn_actor(walker_bp, spawn_point)

        # Attach an AIWalker to the walker
        walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
        walker_controller = world.spawn_actor(walker_controller_bp, carla.Transform(), attach_to=walker)

        # Set the target location for the walker
        target_location = world.get_random_location_from_navigation()
        walker_controller.start()

        # Set the target location for the walker
        walker_controller.go_to_location(target_location)


def main():
    # Carla server
    # server_process = CarlaServer.initialize_server()

    # Carla client
    world = World(synchronous_mode=True)
    # world.set_active_map('Town01')
    world.set_random_weather()

    # Create vehicle
    autonomous_vehicle = Vehicle(world=world.get_world())
    autonomous_vehicle.spawn_vehicle()  # Spawn vehicle at random location

    # Create display
    display = Display('Carla Sensor feed', autonomous_vehicle)
    
    # Traffic and pedestrians
    world.spawn_vehicles_around_ego(autonomous_vehicle.get_vehicle(), num_vehicles_around_ego=40, radius=150)

    # spawn_walkers(world.get_world(), 50)

    action = (0.0, 0.0, 0.0) # (steer, throttle, brake)

    while True:
        try:
            autonomous_vehicle.control_vehicle(action)
            world.tick()
            display.play_window_tick()
        except KeyboardInterrupt:
            autonomous_vehicle.destroy_vehicle()
            display.close_window()
            # CarlaServer.close_server(server_process)
            break

if __name__ == '__main__':
    main()