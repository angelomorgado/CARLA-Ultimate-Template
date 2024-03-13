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

# def spawn_walkers_near_vehicle(world, num_walkers, vehicle_location):
#     """
#     Spawns a specified number of walkers on sidewalks near a given vehicle location.

#     Args:
#         world: A carla.World object representing the Carla simulation.
#         num_walkers: Number of walkers to spawn.
#         vehicle_location: The location of the vehicle to spawn walkers near.
#     """

#     walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
#     map = world.get_map()

#     for _ in range(num_walkers):

#         # Find a sidewalk waypoint within a radius of the vehicle location.
#         max_distance = 25.0  # Adjust this distance as needed
#         sidewalk_waypoint = None
#         while sidewalk_waypoint is None:
#             random_offset = carla.Location(
#                 x=random.uniform(-max_distance, max_distance),
#                 y=random.uniform(-max_distance, max_distance))
#             potential_location = vehicle_location + random_offset
#             waypoint = map.get_waypoint(potential_location, project_to_road=True, lane_type=(carla.LaneType.Sidewalk))
#             if waypoint:
#                 sidewalk_waypoint = waypoint

#         # Spawn walker and controller at the sidewalk waypoint.
#         walker_bp = random.choice(world.get_blueprint_library().filter('walker.pedestrian.*'))
#         try:
#             walker = world.spawn_actor(walker_bp, sidewalk_waypoint.transform)
#         except RuntimeError:
#             continue
#         walkers.append(walker)

#         walker_controller = world.spawn_actor(walker_controller_bp, carla.Transform(), walker)
#         walker_controllers.append(walker_controller)

#     print("Spawned", num_walkers, "walkers near the vehicle.")


def spawn_walkers_near_vehicle(world, num_walkers, vehicle_location):
    """
    Spawns a specified number of walkers on sidewalks near a given vehicle location, 
    assigning them random walk destinations on sidewalks.

    Args:
        world: A carla.World object representing the Carla simulation.
        num_walkers: Number of walkers to spawn.
        vehicle_location: The location of the vehicle to spawn walkers near.
    """

    walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
    map = world.get_map()

    for _ in range(num_walkers):

        # Find a sidewalk waypoint within a radius of the vehicle location.
        max_distance = 25.0  # Adjust this distance as needed
        sidewalk_waypoint = None
        while sidewalk_waypoint is None:
            random_offset = carla.Location(
                  x=random.uniform(-max_distance, max_distance),
                  y=random.uniform(-max_distance, max_distance))
            potential_location = vehicle_location + random_offset
            waypoint = map.get_waypoint(potential_location, project_to_road=True, lane_type=(carla.LaneType.Sidewalk))
            if waypoint:
                sidewalk_waypoint = waypoint

        # Spawn walker and controller.
        walker_bp = random.choice(world.get_blueprint_library().filter('walker.pedestrian.*'))
        try:
            walker = world.spawn_actor(walker_bp, sidewalk_waypoint.transform)
        except RuntimeError:
            continue
        walkers.append(walker)

        # # Find a random destination waypoint on a sidewalk.
        # random_destination_waypoint = None
        # while random_destination_waypoint is None:
        #     # Get a random waypoint from the world.
        #     random_waypoint = map.get_waypoint(random.choice(map.get_spawn_points()).location, project_to_road=True, lane_type=(carla.LaneType.Sidewalk))
        #     # Check if the waypoint is on a sidewalk lane.
        #     if random_waypoint.lane_type & carla.LaneType.Sidewalk:
        #         random_destination_waypoint = random_waypoint

        # # Spawn walker controller and set the random sidewalk waypoint as destination.
        # walker_controller = world.spawn_actor(walker_controller_bp, carla.Transform(), walker)
        # walker_controller.start()  # Start AI control
        # walker_controller.go_to_location(random_destination_waypoint.transform.location)
        # walker_controllers.append(walker_controller)

    print("Spawned", num_walkers, "walkers near the vehicle with random sidewalk destinations.")

def destroy_walkers():
    for walker in walkers:
        walker.destroy()
    for walker_controller in walker_controllers:
        walker_controller.destroy()
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
    display = Display('Carla Sensor feed', autonomous_vehicle)
    
    # Traffic and pedestrians
    # world.spawn_vehicles_around_ego(autonomous_vehicle.get_vehicle(), num_vehicles_around_ego=40, radius=150)

    spawn_walkers_near_vehicle(world.get_world(), 50, autonomous_vehicle.get_location())

    action = (0.0, 0.0, 0.0) # (steer, throttle, brake)

    while True:
        try:
            autonomous_vehicle.control_vehicle(action)
            world.tick()
            display.play_window_tick()
        except KeyboardInterrupt:
            destroy_walkers()
            autonomous_vehicle.destroy_vehicle()
            display.close_window()
            CarlaServer.kill_carla_linux()
            break

if __name__ == '__main__':
    main()