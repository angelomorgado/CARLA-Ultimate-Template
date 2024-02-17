'''
Environment class for the carla environment. It follows the OpenAI Gym format. 

It is a wrapper around the carla environment, and it is used to interact with the environment in a more convenient way.

It implements the following methods:
 - reset: resets the environment and returns the initial state
 - step: takes an action and returns the next state, the reward, a flag indicating if the episode is done, and a dictionary with extra information
 - close: closes the environment

It has the following attributes:
 - action_space: the action space of the environment
 - observation_space: the observation space of the environment
 - reward_range: the reward range of the environment
 - metadata: metadata of the environment
'''

import carla
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from src.world import World
import configuration as config

class Environment(gym.Env):
    def __init__(self, client, vehicle):
        super(Environment, self).__init__()

        self.client = client
        self.world = client.get_world()
        self.map = self.world.get_map()
        self.vehicle = vehicle

        # Define the observation space
        # self.observation_space = spaces.Box(low=0, high=255, shape=(height, width, channels), dtype=np.uint8)

        # Define the action space
        # self.action_space = spaces.Discrete(n_actions) # For discrete actions

    # This reset loads a random scenario
    def reset(self):
        pass

    # This takes an action in the environment and then returns the new state, the reward of that state and the done flag, along with additional info if necessary
    def step(self, action):
        pass

    # Closes everything, more precisely, destroys the vehicle, along with its sensors, destroys every npc and then destroys the world
    def close(self):
        pass

