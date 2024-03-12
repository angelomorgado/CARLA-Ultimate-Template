from gymnasium.envs.registration import register
# Example for the CartPole environment
register(
    # unique identifier for the env `name-version`
    id="carla-rl-gym",
    # path to the class for creating the env
    # Note: entry_point also accept a class as input (and not only a string)
    entry_point="env.environment:CarlaEnv",
    # Max number of steps per episode, using a `TimeLimitWrapper`
    max_episode_steps=10000,
)