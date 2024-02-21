'''
Main window:
    It acts as the center of the entire program controlling the entire process.
    This depends on the project at hand.
    Various examples of mains that act as tutorials can be found in the examples folder.
'''

import time
from env.environment import CarlaEnv

def env_main():
    env = CarlaEnv('carla-rl-gym_cont')

    print(env.action_space.n)
    obs, info = env.reset()
    # print(obs)
    # time.sleep(20)
    
    env.close()

if __name__ == '__main__':
    env_main()
