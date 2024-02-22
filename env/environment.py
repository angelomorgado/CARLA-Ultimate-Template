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

import numpy as np
import json
import time

# TODO: Incorporate the environment into a proper gym environment
# import gymnasium as gym
from gymnasium import spaces

from src.world import World
from src.server import CarlaServer
from src.vehicle import Vehicle
import configuration as config

class CarlaEnv():
    def __init__(self, name, continuous=True, scenarios=[], time_limit=10):
        # 1. Start the server
        self.server_process = CarlaServer.initialize_server(low_quality = config.SIM_LOW_QUALITY, offscreen_rendering = config.SIM_OFFSCREEN_RENDERING)
        # 2. Connect to the server
        self.world = World()
        # 3. Read the flag and get the appropriate situations
        self.is_continuous = continuous
        self.__get_situations(scenarios)
        # 4. Create the vehicle TODO: Change vehicle module to not spawn the vehicle in the constructor, only with a function
        self.vehicle = Vehicle(self.world.get_world())

        # 5. Create the observation space: TODO: Make the observation space more dynamic.
        # Lidar: (122,4) for default settings
        # Change this according to your needs.
        self.rgb_image_shape = (369, 640, 3)
        self.lidar_point_cloud_shape = (122, 4)
        self.current_position_shape = (3,)
        self.target_position_shape = (3,)
        self.number_of_situations = 4

        self.observation_space = spaces.Dict({
            'rgb_data': spaces.Box(low=0, high=255, shape=self.rgb_image_shape, dtype=np.uint8),
            'lidar_data': spaces.Box(low=-np.inf, high=np.inf, shape=self.lidar_point_cloud_shape, dtype=np.float32),
            'position': spaces.Box(low=-np.inf, high=np.inf, shape=self.current_position_shape, dtype=np.float32),
            'target_position': spaces.Box(low=-np.inf, high=np.inf, shape=self.target_position_shape, dtype=np.float32),
            'situation': spaces.Discrete(self.number_of_situations)
        })

        self.observation = None

        # Action space
        if self.is_continuous:
            # For continuous actions
            self.action_space = spaces.Box(low=np.array([-1.0, 0.0, 0.0]), high=np.array([1.0, 1.0, 1.0]), dtype=float)
        else:
            # For discrete actions
            self.action_space = spaces.Discrete(4)
        
        # Truncated flag
        self.time_limit = time_limit
        self.truncated = False  # Used for an episode that was terminated due to a time limit or errors

        # Variables to store the current state
        self.active_scenario_name = None
        self.active_scenario_dict = None

        self.situations_map = {
            "Road": 0,
            "Roundabout": 1,
            "Junction": 2,
            "Tunnel": 3
        }
        
    # ===================================================== GYM METHODS =====================================================                
    # This reset loads a random scenario and returns the initial state plus information about the scenario
    def reset(self, episode_name=None):
        # 1. Choose a random scenario
        if episode_name:
            self.active_scenario_name = episode_name
        else:
            self.active_scenario_name = self.__choose_random_situation()
        print(f"Chosen scenario: {self.active_scenario_name}")
        self.active_scenario_dict = self.situations_dict[self.active_scenario_name]
        # 2. Load the scenario
        self.load_scenario(self.active_scenario_name)
        # 3. Get the initial state (Get the observation data)
        self.__update_observation()
        # 4. Start the timer
        self.__start_timer()
        print("Episode started!")
        # 5. Place the spectator
        self.world.place_spectator_above_vehicle(self.vehicle.get_vehicle())
        # Return the observation and the scenario information
        return self.observation, self.active_scenario_dict
    
    def step(self, action):
        # 1. Control the vehicle
        self.__control_vehicle(np.array(action))
        # 2. Update the observation
        self.__update_observation()
        # 3. Calculate the reward
        reward = self.__calculate_reward()
        # 4. Check if the episode is terminated
        terminated = self.__is_done()
        # 5. Check if the episode is truncated
        self.truncated = self.__timer_truncated()
        # 5. Return the observation, the reward, the terminated flag and the scenario information
        return self.observation, reward, terminated, self.truncated, self.active_scenario_dict

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
        return 0 # Placeholder
    
    def __is_done(self):
        return False # Placeholder


    # ===================================================== OBSERVATION/ACTION METHODS =====================================================
    def __update_observation(self):
        observation_space = self.vehicle.get_observation_data()
        rgb_image = observation_space[0]
        lidar_point_cloud = observation_space[1]
        current_position = observation_space[2]
        target_position = np.array([self.active_scenario_dict['target_position']['x'], self.active_scenario_dict['target_position']['y'], self.active_scenario_dict['target_position']['z']])
        situation = self.situations_map[self.active_scenario_dict['situation']]

        self.observation = {
            'rgb_data': rgb_image,
            'lidar_data': lidar_point_cloud,
            'position': current_position,
            'target_position': target_position,
            'situation': situation
        }

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
    
    # ===================================================== SITUATIONS PARSING =====================================================
    # Filter the current situations based on the flag
    def __get_situations(self, scenarios):
        with open(config.ENV_SCENARIOS_FILE, 'r') as f:
            self.situations_dict = json.load(f)

        if scenarios:
            self.situations_dict = {key: value for key, value in self.situations_dict.items() if value['situation'] in scenarios}

        self.situations_list = list(self.situations_dict.keys())

            
    # ===================================================== AUX METHODS =====================================================
    def __control_vehicle(self, action):
        if self.is_continuous:
            self.vehicle.control_vehicle(action)
        else:
            self.vehicle.control_vehicle_discrete(action)

    def __timer_truncated(self):
        return time.time() - self.start_time > self.time_limit
    
    def __start_timer(self):
        self.start_time = time.time()