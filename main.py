'''
Main window:
    It acts as the center of the entire program controlling the entire process.
    This depends on the project at hand.
    Various examples of mains that act as tutorials can be found in the examples folder.
'''

import carla

from src.vehicle import Vehicle
import configuration
from src.display import Display
from src.world import World
from src.server import CarlaServer

def physics_main():
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

def control_main():
    # Carla client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    if world is None:
        print('Failed to load world')
        return
    
    # Create vehicle
    autonomous_vehicle = Vehicle(world=world)
    autonomous_vehicle.set_autopilot(False)

    # Create display
    display = Display('Carla Sensor feed', autonomous_vehicle)

    # [Steer (-1.0, 1.0), Speed (km/h), Brake (0.0, 1.0), Lights (True, False)]
    action = [0.0, 10.0, 0.0, True]

    while True:
        try:
            autonomous_vehicle.control_vehicle(action)
            display.play_window_tick()
        except KeyboardInterrupt:
            autonomous_vehicle.destroy_vehicle()
            display.close_window()
            break

def traffic_main():
    # Carla client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = World(client)

    # world.spawn_vehicles(20, True)
    world.spawn_pedestrians(50)
    print("Press Ctrl+C to exit...")
    while True:
        try:
            print("", end="")
            pass
        except KeyboardInterrupt:
            print("Exiting...")
            world.destroy_vehicles()
            world.destroy_pedestrians()
            break

    
def weather_main():
    # Carla client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = World(client)

    while True:
        try:
            # world.choose_weather()
            world.change_map()
            pass
        except KeyboardInterrupt:
            break

def server_main():
    process = CarlaServer.initialize_server(low_quality=True)
    CarlaServer.close_server(process)

def test_main():
    # Carla client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = World(client)

    world.print_available_maps()
    print('\n\n ========================================')
    world.print_all_weather_presets()

if __name__ == '__main__':
    # weather_main()
    server_main()

