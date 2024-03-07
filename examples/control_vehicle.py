import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.vehicle import Vehicle
from src.display import Display
from src.world import World
from src.server import CarlaServer
from src.vehicle_control import KeyboardControl

def main():
    process = CarlaServer.initialize_server()
    world = World()
    
    ego_vehicle = Vehicle(world=world.get_world())
    ego_vehicle.spawn_vehicle()
    
    world.place_spectator_above_vehicle(ego_vehicle.get_vehicle())

    keyboard_control = KeyboardControl(ego_vehicle.get_vehicle())

    display = Display('Carla Sensor feed', ego_vehicle)

    while True:
        try:
            world.tick()
            keyboard_control.tick()
            display.play_window_tick()
        except:
            CarlaServer.close_server(process=process)
            display.close_window()
            ego_vehicle.destroy_vehicle()
            keyboard_control.clean()
            break
    
if __name__ == '__main__':
    main()