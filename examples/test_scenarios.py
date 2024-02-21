from env.environment import CarlaEnv

# Used to checkout all the scenarios
def env_test():
    env = CarlaEnv('carla-rl-gym_cont')
    env.load_scenario('Town01-ClearNoon-Road-0')
    active_s = 0

    while True:
        try:
            i = int(input("Enter scenario index: "))
            if i == active_s:
                continue
            active_s = i
            env.clean_scenario()
            env.load_scenario(env.situations_list[i])

        except KeyboardInterrupt:
            break

    env.close()

if __name__ == '__main__':
    env_test()