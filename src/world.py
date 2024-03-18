'''
World:
    This module is a compilation of the various other modules for easier use inside a script. Instead of importing various modules, simply import this one.
    Available Modules:
        - Traffic
        - WeatherControl
        - Map
'''

import carla

from src.weather_control import WeatherControl
from src.traffic_control import TrafficControl
from src.weather_control import WeatherControl
from src.map_control     import MapControl
import configuration as config
import time

class World:
    def __init__(self, client=None, synchronous_mode=False) -> None:
        self.__client = client
        if self.__client is None:
            self.__client = carla.Client(config.SIM_HOST, config.SIM_PORT)
            self.__client.set_timeout(config.SIM_TIMEOUT)
        self.__world = self.__client.get_world()
        self.__weather_control = WeatherControl(self.__world)
        self.__traffic_control = TrafficControl(self.__world)
        self.__map_control     = MapControl(self.__world)
        # self.__available_maps = [m for m in self.__client.get_available_maps() if 'Opt' not in m] # Took out the layered maps
        # self.__map_dict = {m.split("/")[-1]: idx for idx, m in enumerate(self.__available_maps)}
        # self.__active_map = list(self.__map_dict).index(self.__world.get_map().name.split("/")[-1].split("_")[0])
        self.__map = self.__map_control.get_map()
        
        self.synchronous_mode = synchronous_mode
        if self.synchronous_mode:
            self.__settings = self.__world.get_settings()
            self.__settings.synchronous_mode = True
            self.__settings.fixed_delta_seconds = config.SIM_DELTA_SECONDS
            self.__world.apply_settings(self.__settings)
        if config.VERBOSE:
            print("World initialized!")

    def get_client(self):
        return self.__client
    
    def get_world(self):
        return self.__world

    def destroy_world(self):
        self.destroy_pedestrians()
        self.destroy_vehicles()
    
    def tick(self):
        self.__world.tick()

    # ============ Weather Control ============
    # The output is a tuple (carla.WeatherPreset, Str: name of the weather preset)
    def get_weather_presets(self):
        return self.__weather_control.get_weather_presets()
    
    def print_all_weather_presets(self):    
        for idx, weather in enumerate(self.weather_list):
            print(f'{idx}: {weather[1]}')

    def set_active_weather_preset(self, weather):
        self.__weather_control.set_active_weather_preset(weather)
    
    def set_random_weather(self):
        self.__weather_control.set_random_weather_preset()

    # This method let's the user choose with numbers the active preset. It serves as more of a debug.
    def choose_weather(self):
        self.__weather_control.choose_weather()

    # ============ Map Control =================
    # Commented until testes. After testing delete
    # def get_active_map_name(self):
    #     return self.__map.name.split("/")[-1].split("_")[0]

    # def get_map(self):
    #     return self.__map
    
    # def print_available_maps(self):
    #     for idx, m in enumerate(self.__available_maps):
    #         print(f'{idx}: {m}')
    
    # def set_active_map(self, map_name, reload_map=False):
    #     # Check if the map is already loaded
    #     if self.__map_dict[map_name] == self.__active_map and not reload_map:
    #         return
        
    #     self.__active_map = self.__map_dict[map_name]
    #     if map_name in ["Town15", "Town11", "Town12", "Town13"]:
    #         map_name += f"/{map_name}"
    #     self.__client.load_world('/Game/Carla/Maps/' + map_name)
    #     time.sleep(3)
    #     self.__map = self.__world.get_map()

    # # Serves for debugging purposes
    # def change_map(self):
    #     self.print_available_maps()
    #     map_idx = int(input('Choose a map index: '))
    #     self.set_active_map(map_idx)
    
    # def reload_map(self):
    #     self.set_active_map(self.get_active_map_name(), reload_map=True)
    
    def get_active_map_name(self):
        return self.__map_control.get_active_map_name()        
    
    def get_map(self):
        self.__map = self.__map_control.get_map()
        return self.__map_control.get_map()
    
    def print_available_maps(self):
        self.__map_control.print_available_maps()

    def set_active_map(self, map_name, reload_map=False):
        self.__map_control.set_active_map(map_name=map_name, reload_map=reload_map)
        self.__map = self.__map_control.get_map()
    
    def change_map(self):
        self.__map_control.change_map()
    
    def reload_map(self):
        self.__map_control.reload_map()
    
    # ============ Traffic Control ============
    def spawn_vehicles(self, num_vehicles = 10, autopilot_on = False):
        self.__traffic_control.spawn_vehicles(num_vehicles, autopilot_on)
    
    def spawn_vehicles_around_ego(self, ego_vehicle, radius, num_vehicles_around_ego, seed=None):
        self.__traffic_control.spawn_vehicles_around_ego(ego_vehicle, radius, num_vehicles_around_ego, seed)
    
    def destroy_vehicles(self):
        self.__traffic_control.destroy_vehicles()
    
    def toggle_autopilot(self, autopilot_on = True):
        self.__traffic_control.toggle_autopilot(autopilot_on)
    
    def spawn_pedestrians(self, num_pedestrians=10):
        self.__traffic_control.spawn_pedestrians(num_pedestrians)
    
    def spawn_pedestrians_around_ego(self, ego_vehicle_location, num_pedestrians=10, radius=50):
        self.__traffic_control.spawn_pedestrians_around_ego(ego_vehicle_location, num_pedestrians, radius)
    
    def destroy_pedestrians(self):
        self.__traffic_control.destroy_pedestrians()

    def toggle_lights(self, lights_on=True):
        self.__traffic_control.toggle_lights(lights_on)
    
    def update_traffic_map(self):
        self.__traffic_control.update_map(self.__map)
        return self.__map
    
    # ============ Weather Control ===============
    def get_weather_presets(self):
        return self.__weather_control.get_weather_presets()
    
    def print_all_weather_presets(self):
        self.__weather_control.print_all_weather_presets()
    
    def set_active_weather_preset(self, weather):
        self.__weather_control.set_active_weather_preset(weather)
    
    def choose_weather(self):
        self.__weather_control.choose_weather()
    
    def get_active_weather(self):
        return self.__weather_control.get_active_weather()
    
    # ============ Spectator Control ============
    def place_spectator_above_location(self, location):
        spectator = self.__world.get_spectator()
        spectator.set_transform(carla.Transform(location + carla.Location(z=50),
        carla.Rotation(pitch=-90)))

    def place_spectator_behind_location(self, location, rotation):
        spectator = self.__world.get_spectator()
        location += carla.Location(x = -6, y=0, z = 2.5)
        transform = carla.Transform(location, rotation)
        spectator.set_transform(transform)

        # Calculate the new spectator location
        spectator_location = transform.location

        spectator.set_transform(carla.Transform(location=spectator_location, rotation=transform.rotation))
