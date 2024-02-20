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
# import gymnasium as gym
# from gymnasium import spaces

from src.world import World
import configuration as config

class Environment():
    def __init__(self, flag):
        self.world = World()


    # This reset loads a random scenario
    def reset(self):
        pass

    # Closes everything, more precisely, destroys the vehicle, along with its sensors, destroys every npc and then destroys the world
    def close(self):
        pass

