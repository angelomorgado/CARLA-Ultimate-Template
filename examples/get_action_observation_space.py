import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from env.environment import CarlaEnv

def main():
    env = CarlaEnv('carla-rl-gym', initialize_server=True, has_traffic=False, verbose=False)
    obs, info = env.reset()

    print("Action Space:", env.action_space)
    print("Observation Space:", env.observation_space)

    env.close()

if __name__ == '__main__':
    main()