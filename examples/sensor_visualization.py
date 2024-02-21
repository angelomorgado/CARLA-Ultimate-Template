# For tutorial purposes
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import carla

from src.display import Display
from src.vehicle import Vehicle

def main():
    # Carla client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    if world is None:
        print('Failed to load world')
        return
    
    # Create vehicle
    autonomous_vehicle = Vehicle(world=world)
    autonomous_vehicle.spawn_vehicle()
    autonomous_vehicle.set_autopilot(True)

    # Display the vehicle's sensors
    display = Display('Carla Sensor feed', autonomous_vehicle)
    display.play_window()

    # When terminated destroy the vehicle
    autonomous_vehicle.destroy_vehicle()

if __name__ == '__main__':
    main()
