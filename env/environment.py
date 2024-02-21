'''
Environment class for the carla environment.

It is a wrapper around the carla environment, and it is used to interact with the environment in a more convenient way.

It implements the following methods:
 - reset: resets the environment and returns the initial state
 - step: takes an action and returns the next state, the reward, a flag indicating if the episode is done, and a dictionary with extra information
 - close: closes the environment

Observation Space:
    [RGB image, LiDAR point cloud, Current position, Target position, Current situation]

    The current situation cannot be a string therefore it was converted to a numerical value using a dictionary to map the string to a number

    Dict:{
        Road:       0,
        Roundabout: 1,
        Junction:   2,
        Tunnel:     3,
    }

Action Space:
    Continuous:
        [Steering (-1.0, 1.0), Throttle (0.0, 1.0), Brake (0.0, 1.0)]
    Discrete:
        [Action] (0: Accelerate, 1: Decelerate, 2: Left, 3: Right) <- It's a number from 0 to 3

'''

import carla
import numpy as np
import json

# TODO: Incorporate the environment into a proper gym environment
# import gymnasium as gym
from gymnasium import spaces

from src.world import World
from src.server import CarlaServer
from src.vehicle import Vehicle
import configuration as config

class CarlaEnv():
    def __init__(self, flag):
        # 1. Start the server
        self.server_process = CarlaServer.initialize_server(low_quality = config.SIM_LOW_QUALITY, offscreen_rendering = config.SIM_OFFSCREEN_RENDERING)
        # 2. Connect to the server
        self.world = World()
        # 3. Read the flag and get the appropriate situations
        self.is_continuous, self.situations_list = self.__read_flag(flag)
        # 4. Create the vehicle TODO: Change vehicle module to not spawn the vehicle in the constructor, only with a function
        self.vehicle = Vehicle(self.world.get_world())

        # 5. Create the observation space: TODO: Make the observation space more dynamic.
        # Change this according to the needs.

        # Lidar: (122,4) (184, 3) for default settings
        self.observation_space = spaces.Dict({
            'rgb_data': spaces.Box(low=0, high=255, shape=(369, 640, 3), dtype=np.uint8),
            'lidar_data': spaces.Box(low=-np.inf, high=np.inf, shape=(184, 3), dtype=np.float32),
            'position': spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32),
            'target_position': spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32),
            'situation': spaces.Discrete(4)
        })

        # Action space
        if self.is_continuous:
            # For continuous actions
            self.action_space = spaces.Box(low=np.array([-1.0, 0.0, 0.0]), high=np.array([1.0, 1.0, 1.0]), dtype=np.float32)
        else:
            # For discrete actions
            self.action_space = spaces.Discrete(4)

        # Variables to store the current state
        self.active_scenario_name = None
        self.active_scenario_dict = None

        self.situations_map = {
            "Road": 0,
            "Roundabout": 1,
            "Junction": 2,
            "Tunnel": 3
        }
    
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
        scenarios_list = [s.capitalize() for s in scenarios_list]
        return is_continuous, list(self.__get_situations(self.situations_dict, scenarios_list))
    
    # Filter the current situations based on the flag
    def __get_situations(self, scene_dict, scenarios=[]):
        if scenarios:
            filtered_dict = {key: value for key, value in scene_dict.items() if value['situation'] in scenarios}
            return filtered_dict
        else:
            return scene_dict
        
    # ===================================================== GYM METHODS =====================================================                
    # This reset loads a random scenario and returns the initial state plus information about the scenario
    def reset(self):
        # 1. Choose a random scenario
        self.active_scenario_name = self.__choose_random_situation()
        self.active_scenario_dict = self.situations_dict[self.active_scenario_name]

        # 2. Load the scenario
        self.load_scenario(self.active_scenario_name)

        # 3. Get the initial state (Get the observation data)
        self.__update_observation_space()

        # Return the observation and the scenario information
        return self.observation_space, self.active_scenario_dict
    
    def step(self, action):
        pass
        

    # Closes everything, more precisely, destroys the vehicle, along with its sensors, destroys every npc and then destroys the world
    def close(self):
        # 1. Destroy the vehicle
        self.vehicle.destroy_vehicle()

        # 2. Destroy the world
        self.world.destroy_world()

        # 3. Close the server
        CarlaServer.close_server(self.server_process)
    
    # ===================================================== REWARD METHODS =====================================================
    def __calculate_reward(self):
        return 0


    # ===================================================== OBSERVATION/ACTION METHODS =====================================================
    def __update_observation_space(self):
        observation_space = self.vehicle.get_observation_data()
        rgb_image = observation_space[0]
        lidar_point_cloud = observation_space[1]
        current_position = observation_space[2]
        target_position = np.array([self.active_scenario_dict['target_position']['x'], self.active_scenario_dict['target_position']['y'], self.active_scenario_dict['target_position']['z']])
        situation = self.situations_map[self.active_scenario_dict['situation']]

        # Construct the observation space dictionary
        observation_space_dict = {
            'rgb_data': rgb_image,
            'lidar_data': lidar_point_cloud,
            'position': current_position,
            'target_position': target_position,
            'situation': situation
        }

        # Update the observation space with spaces.Box or spaces.Discrete
        self.observation_space.spaces['rgb_data'] = spaces.Box(low=0, high=255, shape=(360, 640, 4), dtype=np.uint8)
        self.observation_space.spaces['lidar_data'] = spaces.Box(low=-np.inf, high=np.inf, shape=(5316, 4), dtype=np.float32)
        self.observation_space.spaces['position'] = spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32)
        self.observation_space.spaces['target_position'] = spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32)
        self.observation_space.spaces['situation'] = spaces.Discrete(4)

        # NOT UPDATING


    # ===================================================== SCENARIO METHODS =====================================================
    
    def load_scenario(self, scenario_name):
        scenario_dict = self.situations_dict[scenario_name]
        self.__load_map(scenario_dict['map_name'])
        self.__load_weather(scenario_dict['weather_condition'])
        self.__spawn_vehicle(scenario_dict)

    def clean_scenario(self):
        self.vehicle.destroy_vehicle()
        self.world.destroy_vehicles()
        self.world.destroy_pedestrians()
    
    def print_all_scenarios(self):
        for idx, i in enumerate(self.situations_list):
            print(idx, ": ", i)
    
    def __spawn_vehicle(self, s_dict):
        location = (s_dict['initial_position']['x'], s_dict['initial_position']['y'], s_dict['initial_position']['z'])
        rotation = (s_dict['initial_rotation']['pitch'], s_dict['initial_rotation']['yaw'], s_dict['initial_rotation']['roll'])
        self.vehicle.spawn_vehicle(location, rotation)
    
    def __load_map(self, map_name):
        self.world.set_active_map_name('/Game/Carla/Maps/' + map_name)

    def __load_weather(self, weather_name):
        self.world.set_active_weather_preset(weather_name)
    
    def __choose_random_situation(self):
        return np.random.choice(self.situations_list)

    # ===================================================== AUX METHODS =====================================================


