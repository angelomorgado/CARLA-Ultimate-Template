'''
Main window:
    It acts as the center of the entire program controlling the entire process.
    This depends on the project at hand.
    Various examples of mains that act as tutorials can be found in the examples folder.
'''

import carla

from src.vehicle import Vehicle
import configuration

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
    autonomous_vehicle.set_autopilot(True)
    autonomous_vehicle.print_vehicle_physics()

    # Change the vehicle's physics to a determined weather that is stated in the JSON file.
    autonomous_vehicle.change_vehicle_physics("wet")

    print("\n\n===========================================================================================================\n")
    autonomous_vehicle.print_vehicle_physics()

    autonomous_vehicle.destroy_vehicle()

if __name__ == '__main__':
    main()
