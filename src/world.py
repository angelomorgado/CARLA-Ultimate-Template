import carla

from src.weather_control import WeatherControl
from src.traffic_control import TrafficControl
from src.weather_control import WeatherControl
import configuration as config

class World:
    def __init__(self, client=None) -> None:
        self.__client = client
        if self.__client is None:
            self.__client = carla.Client(config.SIM_HOST, config.SIM_PORT)
            self.__client.set_timeout(config.SIM_TIMEOUT)
        self.__world = self.__client.get_world()
        self.weather_control = WeatherControl(self.__world)
        self.traffic_control = TrafficControl(self.__world)
        self.weather_control = WeatherControl(self.__world)
        self.available_maps = [m for m in self.__client.get_available_maps() if 'Opt' not in m] # Took out the layered maps
        self.active_map = 7 # Default map is Town10HD

    def get_client(self):
        return self.__client

    def destroy_world(self):
        self.destroy_pedestrians()
        self.destroy_vehicles()

    # ============ Weather Control ============
    # The output is a tuple (carla.WeatherPreset, Str: name of the weather preset)
    def get_weather_presets(self):
        return self.weather_control.get_weather_presets()
    
    def print_all_weather_presets(self):    
        for idx, weather in enumerate(self.weather_list):
            print(f'{idx}: {weather[1]}')

    def set_active_weather_preset(self, weather):
        self.weather_control.set_active_weather_preset(weather)

    # This method let's the user choose with numbers the active preset. It serves as more of a debug.
    def choose_weather(self):
        self.weather_control.choose_weather()

    # ============ Map Control =================
    def get_map(self):
        return self.active_map
    
    def print_available_maps(self):
        for idx, m in enumerate(self.available_maps):
            print(f'{idx}: {m}')

    def set_active_map(self, map_idx):
        self.active_map = map_idx
        self.__client.load_world(self.available_maps[map_idx])
    
    def set_active_map_name(self, map_name):
        for idx, m in enumerate(self.available_maps):
            if map_name in m:
                self.active_map = idx
                self.__client.load_world(self.available_maps[idx])
                return
    
    # Serves for debugging purposes
    def change_map(self):
        self.print_available_maps()
        map_idx = int(input('Choose a map index: '))
        self.set_active_map(map_idx)
    
    # ============ Traffic Control ============
    def spawn_vehicles(self, num_vehicles = 10, autopilot_on = False):
        self.traffic_control.spawn_vehicles(num_vehicles, autopilot_on)
    
    def destroy_vehicles(self):
        self.traffic_control.destroy_vehicles()
    
    def toggle_autopilot(self, autopilot_on = True):
        self.traffic_control.toggle_autopilot(autopilot_on)
    
    def spawn_pedestrians(self, num_pedestrians=10):
        self.traffic_control.spawn_pedestrians(num_pedestrians)
    
    def destroy_pedestrians(self):
        self.traffic_control.destroy_pedestrians()
    
    # ============ Weather Control ===============
    def get_weather_presets(self):
        return self.weather_control.get_weather_presets()
    
    def print_all_weather_presets(self):
        self.weather_control.print_all_weather_presets()
    
    def set_active_weather_preset(self, weather):
        self.weather_control.set_active_weather_preset(weather)
    
    def choose_weather(self):
        self.weather_control.choose_weather()


    