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

from env.environment import CarlaEnv

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
    world = World()
    world.set_active_map_name('/Game/Carla/Maps/Town01')
    
    # Create vehicle
    autonomous_vehicle = Vehicle(world=world.get_world())
    # Location: Y (Latitude): -0.000439, X (Longitude): 0.000155, Z (Altitude): 0.001821
    # Rotation: Pitch: 0.000000, Yaw: 0.000000, Roll: 0.000000
    # autonomous_vehicle.spawn_vehicle()
    autonomous_vehicle.spawn_vehicle((92.2, 485.9, 0.0), (0.0, 90.0, 0.0))

    # Create display
    display = Display('Carla Sensor feed', autonomous_vehicle)

    # [Steer (-1.0, 1.0), Speed (km/h)]
    action = [0.0, 50.0]

    while True:
        try:
            # autonomous_vehicle.control_vehicle(action)
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

    print(client.get_available_maps())
    print('\n\n ========================================')
    world.print_all_weather_presets()

def env_main():
    env = CarlaEnv('carla-rl-gym_cont_tunnel-roundabout')

    env.close()


if __name__ == '__main__':
    control_main()
    # test_main()
    # weather_main()
    # server_main()
    # env_main()

