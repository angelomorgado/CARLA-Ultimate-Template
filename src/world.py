import carla

from src.weather_control import WeatherControl

class World:
    def __init__(self, world) -> None:
        self.__world = world
        self.weather_control = WeatherControl(self.__world)


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

    # ============ Traffic Control =================


    