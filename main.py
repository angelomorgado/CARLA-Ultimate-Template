'''
Main window:
    It acts as the center of the entire program controlling the entire process.
    This depends on the project at hand.
    Various examples of mains that act as tutorials can be found in the examples folder.
'''

import time
from env.environment import CarlaEnv

def env_main():
    env = CarlaEnv('carla-rl-gym', time_limit=10)
    
    for i in range(10):
        print("================================ Episode", i, " ================================")
        obs, info = env.reset()
        time.sleep(0.2)
        while True:
            # Random action
            # action = env.action_space.sample()
            # Empty action
            action = [0.0, 0.0, 0.0]
            obs, reward, terminated, truncated, info = env.step(action)
            if terminated or truncated:
                print('Episode terminated closing environment')
                break

    env.close()

if __name__ == '__main__':
    env_main()
