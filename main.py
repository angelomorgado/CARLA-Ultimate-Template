'''
Main window:
    It acts as the center of the entire program controlling the entire process.
    This depends on the project at hand.
    Various examples of mains that act as tutorials can be found in the examples folder.
'''

import time
from env.environment import CarlaEnv

def env_main():
    env = CarlaEnv('carla-rl-gym', time_limit=5, initialize_server=True)
    # l = ["Town10HD-ClearNoon-Junction-1", "Town01-ClearNoon-Junction-1"]
    
    for i in range(10):
        print("================================ Episode", i, " ================================")
        obs, info = env.reset()
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

def main():
    env = CarlaEnv('carla-rl-gym', time_limit=5)
    l = ["Town01", "Town10HD", "Town2"]

    for i in range(len(l)):
        env.load_world(l[i])
        print(f"World {l[i]} loaded")

if __name__ == '__main__':
    env_main()
    # main()
