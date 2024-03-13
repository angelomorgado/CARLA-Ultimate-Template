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

walkers = []
walker_controllers = []

def spawn_random_walkers(world, num_walkers=10):
    walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
    walker_bps = world.get_blueprint_library().filter('walker.pedestrian.*')
    map = world.get_map()

    # Get spawn points on sidewalks
    spawn_points = map.get_spawn_points()

    for _ in range(num_walkers):
        # Randomly select a spawn point
        spawn_point = random.choice(spawn_points)
        
        # Extract location from the spawn point
        spawn_location = spawn_point.location

        # Get waypoint from the location
        sidewalk_waypoint = map.get_waypoint(spawn_location, project_to_road=True, lane_type=(carla.LaneType.Sidewalk))

        # Spawn walker and controller at the sidewalk waypoint.
        walker_bp = random.choice(walker_bps)
        try:
            walker = world.spawn_actor(walker_bp, carla.Transform(sidewalk_waypoint.transform.location))
        except RuntimeError:
            continue
        walkers.append(walker)

        walker_controller = world.spawn_actor(walker_controller_bp, carla.Transform(), walker)
        walker_controllers.append(walker_controller)
        
        # Keep the commented code if you want to start and move the walkers
        # walker_controller.start()
        # walker_controller.go_to_location(world.get_random_location_from_navigation())

    print("Spawned", num_walkers, "walkers on random sidewalks.")

def destroy_walkers():
    for walker_controller in walker_controllers:
        walker_controller.stop()
        walker_controller.destroy()
    for walker in walkers:
        walker.destroy()
    print("Destroyed all walkers.")

def main():
    # Carla server
    # server_process = CarlaServer.initialize_server()

    # Carla client
    world = World(synchronous_mode=True)
    world.set_active_map('Town01')
    # world.set_random_weather()

    # Create vehicle
    autonomous_vehicle = Vehicle(world=world.get_world())
    autonomous_vehicle.spawn_vehicle()  # Spawn vehicle at random location
    
    world.place_spectator_above_vehicle(autonomous_vehicle.get_vehicle())

    # Create display
    # display = Display('Carla Sensor feed', autonomous_vehicle)
    
    # Traffic and pedestrians
    # world.spawn_vehicles_around_ego(autonomous_vehicle.get_vehicle(), num_vehicles_around_ego=40, radius=150)

    # spawn_walkers_near_vehicle(world.get_world(), 10, autonomous_vehicle.get_location())
    spawn_random_walkers(world.get_world(), 50)

    action = (0.0, 0.0, 0.0) # (steer, throttle, brake)

    while True:
        try:
            autonomous_vehicle.control_vehicle(action)
            world.tick()
            # display.play_window_tick()
        except KeyboardInterrupt:
            destroy_walkers()
            autonomous_vehicle.destroy_vehicle()
            # display.close_window()
            # CarlaServer.kill_carla_linux()
            break

if __name__ == '__main__':
    main()