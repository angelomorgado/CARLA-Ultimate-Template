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
from src.vehicle_control import KeyboardControl
import carla
import random

inside_stop_area = False
has_stopped = False

# TODO: Test this function
def check_stop_sign(vehicle, world):
    global has_stopped
    global inside_stop_area
    
    distance = 10.0  # meters
    
    current_location = vehicle.get_location()
    current_waypoint = world.get_map().get_waypoint(current_location, project_to_road=True)
    
    # Get all the stop sign landmarks within a certain distance from the vehicle
    stop_signs = current_waypoint.get_landmarks_of_type(distance, carla.LandmarkType.StopSign)
    
    if len(stop_signs) == 0:
        if inside_stop_area == True and has_stopped == True:
            print("Vehicle has stopped at the stop sign.")
            has_stopped = False
            inside_stop_area = False
        elif inside_stop_area == True and has_stopped == False:
            print("Vehicle has not stopped at the stop sign.")
            has_stopped = False
            inside_stop_area = False
        else:            
            return
    else:
        inside_stop_area = True

    # The vehicle entered the stop sign area
    for stop_sign in stop_signs:
        # Check if the vehicle has stopped
        if vehicle.get_speed() < 1.0:  # Adjust this threshold for stopped speed
            has_stopped = True


        
def main():
    # Carla server
    # server_process = CarlaServer.initialize_server()

    # Carla client
    world = World(synchronous_mode=True)
    world.set_active_map('Town07')
    # world.set_random_weather()

    # Create vehicle
    autonomous_vehicle = Vehicle(world=world.get_world())
    autonomous_vehicle.spawn_vehicle()  # Spawn vehicle at random location
    v_control = KeyboardControl(autonomous_vehicle.get_vehicle()) # Control vehicle with keyboard
    
    
    world.place_spectator_above_location(autonomous_vehicle.get_location())

    # Create display
    display = Display('Carla Sensor feed', autonomous_vehicle)
    
    # Traffic and pedestrians
    # world.spawn_vehicles_around_ego(autonomous_vehicle.get_vehicle(), num_vehicles_around_ego=40, radius=150)
    # world.spawn_pedestrians_around_ego(autonomous_vehicle.get_location(), num_pedestrians=40, radius=150)
    

    while True:
        try:
            world.tick()
            v_control.tick()
            display.play_window_tick()
            check_stop_sign(autonomous_vehicle, world)
        except KeyboardInterrupt:
            autonomous_vehicle.destroy_vehicle()
            display.close_window()
            # CarlaServer.kill_carla_linux()
            break

if __name__ == '__main__':
    main()