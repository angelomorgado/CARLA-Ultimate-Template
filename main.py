'''
Main window:
    It acts as the center of the entire program controlling the entire process.
    This depends on the project at hand.
    Various examples of mains that act as tutorials can be found in the examples folder.
'''

import time
from env.environment import CarlaEnv

def env_main():
    env = CarlaEnv('carla-rl-gym', time_limit=5, initialize_server=False, is_training=True)
    l = ["Town01-ClearNoon-Road-0", "Town01-WetNight-Road-0"]
    
    for i in range(2):
        print("================================ Episode", i, " ================================")
        obs, info = env.reset(l[i])
        while True:
            # Random action TODO: Test this
            # action = env.action_space.sample()
            # Empty action
            action = [1.0, 1.0, 1.0]
            # print('Action:', action)
            obs, reward, terminated, truncated, info = env.step(action)
            # print('Observation:', obs)
            if terminated or truncated:
                print('Episode terminated closing environment')
                break

    env.close()

if __name__ == '__main__':
    env_main()
