'''
Environment class for the carla environment.

It is a wrapper around the carla environment, and it is used to interact with the environment in a more convenient way.

It implements the following methods:
 - reset: resets the environment and returns the initial state
 - step: takes an action and returns the next state, the reward, a flag indicating if the episode is done, and a dictionary with extra information
 - close: closes the environment

'''

import carla
import numpy as np
import json
# import gymnasium as gym
# from gymnasium import spaces

from src.world import World
from src.server import CarlaServer
import configuration as config

class CarlaEnv():
    def __init__(self, flag):
        # 1. Start the server
        # self.server_process = CarlaServer.initialize_server(low_quality = True, offscreen_rendering = False)

        # 2. Connect to the server
        # self.world = World()

        # 3. Read the flag and get the appropriate situations
        self.is_continuous, self.situations_list = self.__read_flag(flag)

        print(self.is_continuous)
        print(self.situations_list)

    
    # ===================================================== FLAG PARSING =====================================================
    # The flag is structured: "carla-rl-gym_{cont_disc}" <- for any situation or "carla-rl-gym_{cont_disc}_{situation}-{situation2}" <- for a specific situation(s) (It can contain 1 or more situations)
    def __read_flag(self, flag):
        
        # 1. Check if it is a continuous or discrete environment
        is_continuous = flag.split('_')[1] == 'cont'
        
        # 2. Get the scenarios dictionary
        with open(config.ENV_SCENARIOS_FILE, 'r') as f:
            self.situations_dict = json.load(f)
        
        # 3. Get the scenarios in a list
        scenarios_list = flag.split('_')[2].split('-') if len(flag.split('_')) > 2 else []
        return is_continuous, list(self.__get_situations(self.situations_dict, scenarios_list))
    
    def __get_situations(self, scene_dict, scenarios=[]):
        if scenarios:
            filtered_dict = {key: value for key, value in scene_dict.items() if value['situation'] in scenarios}
            return filtered_dict
        else:
            return scene_dict
                
    # This reset loads a random scenario
    def reset(self):
        pass

    # Closes everything, more precisely, destroys the vehicle, along with its sensors, destroys every npc and then destroys the world
    def close(self):
        pass

