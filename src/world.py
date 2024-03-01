import carla

from src.weather_control import WeatherControl
from src.traffic_control import TrafficControl
from src.weather_control import WeatherControl
import configuration as config

class World:
    def __init__(self, client=None, synchronous_mode=False) -> None:
        self.__client = client
        if self.__client is None:
            self.__client = carla.Client(config.SIM_HOST, config.SIM_PORT)
            self.__client.set_timeout(config.SIM_TIMEOUT)
        self.__world = self.__client.get_world()
        self.weather_control = WeatherControl(self.__world)
        self.traffic_control = TrafficControl(self.__world)
        self.weather_control = WeatherControl(self.__world)
        self.available_maps = [m for m in self.__client.get_available_maps() if 'Opt' not in m] # Took out the layered maps
        self.map_dict = {m.split("/")[-1]: idx for idx, m in enumerate(self.available_maps)}
        self.set_active_map("Town10HD")
        self.active_map = 7
        self.synchronous_mode = synchronous_mode
        if self.synchronous_mode:
            self.__settings = self.__world.get_settings()
            self.__settings.synchronous_mode = True
            self.__settings.fixed_delta_seconds = config.SIM_DELTA_SECONDS
            self.__world.apply_settings(self.__settings)
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
        return self.weather_control.get_weather_presets()
    
    def print_all_weather_presets(self):    
        for idx, weather in enumerate(self.weather_list):
            print(f'{idx}: {weather[1]}')

    def set_active_weather_preset(self, weather):
        self.weather_control.set_active_weather_preset(weather)
    
    def set_random_weather(self):
        self.weather_control.set_random_weather_preset()

    # This method let's the user choose with numbers the active preset. It serves as more of a debug.
    def choose_weather(self):
        self.weather_control.choose_weather()

    # ============ Map Control =================
    def get_map(self):
        return self.active_map
    
    def print_available_maps(self):
        for idx, m in enumerate(self.available_maps):
            print(f'{idx}: {m}')
    
    def set_active_map(self, map_name):
        # Check if the map is already loaded
        if self.map_dict[map_name] == self.active_map:
            return

        self.active_map = self.map_dict[map_name]
        self.__client.load_world('/Game/Carla/Maps/' + map_name)

    # Serves for debugging purposes
    def change_map(self):
        self.print_available_maps()
        map_idx = int(input('Choose a map index: '))
        self.set_active_map(map_idx)
    
    # ============ Traffic Control ============
    def spawn_vehicles(self, num_vehicles = 10, autopilot_on = False):
        self.traffic_control.spawn_vehicles(num_vehicles, autopilot_on)
    
    def spawn_vehicles_around_ego(self, ego_vehicle, radius, num_vehicles_around_ego, scene_name=None):
        self.traffic_control.spawn_vehicles_around_ego(ego_vehicle, radius, num_vehicles_around_ego, scene_name)
    
    def destroy_vehicles(self):
        self.traffic_control.destroy_vehicles()
    
    def toggle_autopilot(self, autopilot_on = True):
        self.traffic_control.toggle_autopilot(autopilot_on)
    
    def spawn_pedestrians(self, num_pedestrians=10):
        self.traffic_control.spawn_pedestrians(num_pedestrians)
    
    def spawn_pedestrians_around_ego(self, ego_vehicle, num_pedestrians=10, distance_range=(5,30)):
        self.traffic_control.spawn_pedestrians_around_ego(ego_vehicle, num_pedestrians, distance_range)
    
    def destroy_pedestrians(self):
        self.traffic_control.destroy_pedestrians()

    def toggle_lights(self, lights_on=True):
        self.traffic_control.toggle_lights(lights_on)
    
    # ============ Weather Control ===============
    def get_weather_presets(self):
        return self.weather_control.get_weather_presets()
    
    def print_all_weather_presets(self):
        self.weather_control.print_all_weather_presets()
    
    def set_active_weather_preset(self, weather):
        self.weather_control.set_active_weather_preset(weather)
    
    def choose_weather(self):
        self.weather_control.choose_weather()
    
    def get_active_weather(self):
        return self.weather_control.get_active_weather()
    
    # ============ Spectator Control ============
    def place_spectator_above_vehicle(self, vehicle):
        spectator = self.__world.get_spectator()
        transform = vehicle.get_transform()
        spectator.set_transform(carla.Transform(transform.location + carla.Location(z=50),
        carla.Rotation(pitch=-90)))
    