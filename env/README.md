# CARLA Episode Generator

## Overview

The CARLA Episode Generator is a tool designed to facilitate the creation of diverse training scenarios for reinforcement learning (RL) models in the CARLA simulator. This tool allows you to define structured scenarios, controlling various environment parameters such as the map, weather conditions, traffic density, initial positions, and specific situations like roundabouts or junctions.

## Known Issues

- If the server quality level is set to "Low" the server might (most likely will) crash when trying to load the map. This is a known issue with the CARLA server and it's not related to the code.
- Throttle and brake aren't working

## Usage

### Scenario Definition

Define training scenarios in a structured format, such as a JSON file, specifying the following parameters:

- `map_name`: The name of the CARLA map.
- `weather_condition`: The weather conditions (e.g., "ClearNoon").
- `initial_position`: Initial position of the ego vehicle (x, y, z coordinates).
- `initial_rotation`: Initial rotation of the ego vehicle (pitch, yaw, roll)
- `situation`: Type of scenario or situation (e.g., "Roundabout," "Junction")
- `target_position`: Target position for the ego vehicle

### Randomization

Implement controlled randomness by randomizing scenario selection. Ensure that certain scenarios are sampled with specific probabilities to control the variability in training.

Also in each scenario, both the vehicle and pedestrian density are random between None/Low/Medium/High values.

However, during testing , it is paramount to keep the vehicle and pedestrians location the same, so a seed will be created using the scenario name for the vehicle locations.

### CARLA Environment Setup

Implement the `setup_carla_environment` method to configure the CARLA environment based on the loaded scenario. Use the CARLA Python API to set weather conditions, initial vehicle position, and other relevant parameters.

## Scenario Definition Example

```json
{
  "Town01-ClearNoon-Road-0": {
    "map_name": "Town01",
    "weather_condition": "ClearNoon",
    "initial_position": {"x": 392.2, "y": 285.9, "z": 0.3},
    "initial_rotation": {"pitch": 0.0, "yaw": 90.0, "roll": 0.0},
		"target_position": {"x": 365.3, "y": 326.6, "z": 0.3},
    "situation": "Road"
  },
  // More scenarios
}
```

### Attributes

The name of the scenario will be based on these attributes, then because there can be many there will be a counter after the name to differentiate.

#### Available Maps:

- /Game/Carla/Maps/Town01 <- small city roads with junctions with lightpoles
- /Game/Carla/Maps/Town02 <- Has city roads and junctions (neighborhood)
- /Game/Carla/Maps/Town03 <- Big city with roundabouts lightpoles, big junctions and inclined roads, also has big road and even a tunnel.
- /Game/Carla/Maps/Town04 <- Highway with small city in the center with lightpoles and junctions
- /Game/Carla/Maps/Town05 <- Highway with big city in the center with big junctions, lightpoles
- /Game/Carla/Maps/Town07 <- Village road with street signs and small intersections with lightpoles
- /Game/Carla/Maps/Town10HD <- Default map, big city with intersections, lightpoles
- /Game/Carla/Maps/Town15 <- This is the biggest city and it has every type of scenario possible, it’s used for testing the carla leaderboard challenge

Each map has a variation with the suffix “_opt”. This means that the map is layered and different layers can be removed and added with scripts. But these won't be used.

#### Available Weather Conditions

- Clear Night
- Clear Noon
- Clear Sunset
- Cloudy Night
- Cloudy Noon
- Cloudy Sunset
- Default
- Dust Storm
- Hard Rain Night
- Hard Rain Noon
- Hard Rain Sunset
- Mid Rain Sunset
- Mid Rainy Night
- Mid Rainy Noon
- Soft Rain Night
- Soft Rain Noon
- Soft Rain Sunset
- Wet Cloudy Night
- Wet Cloudy Noon
- Wet Cloudy Sunset
- Wet Night
- Wet Noon
- Wet Sunset

#### Available Traffic Densities

- None
- Low
- Medium
- High

TODO: Maybe separate densities for vehicles and pedestrians

#### Available Situations

- Road
- Roundabout
- Junction
- Tunnel?

---

# Carla RL Environment

This environment follows the OpenAI gym method. It works in Windows and Linux

## Configuration

- Set the environmental variable `CARLA_SERVER` as the location of the Carla server's directory.

- TODO: Make requirements.txt

## Env Attributes

### Observation space

The observation space uses gymnasium.Spaces to store data, to make it compatible with common RL libraries.

```
Observation Space:
    [RGB image, LiDAR point cloud, Current position, Target position, Current situation]

    The current situation cannot be a string therefore it was converted to a numerical value using a dictionary to map the string to a number

    Dict:{
        Road:       0,
        Roundabout: 1,
        Junction:   2,
        Tunnel:     3,
    }
```

Code format:
```python
    self.observation_space = spaces.Dict({
        'rgb_data': spaces.Box(low=0, high=255, shape=*rgb_shape*, dtype=np.uint8),
        'lidar_data': spaces.Box(low=-np.inf, high=np.inf, shape=*lidar_shape*, dtype=np.float32),
        'position': spaces.Box(low=-np.inf, high=np.inf, shape=*position_shape*, dtype=np.float32),
        'target_position': spaces.Box(low=-np.inf, high=np.inf, shape=*target_shape*, dtype=np.float32),
        'situation': spaces.Discrete(4)
    })
```

### Action space

The action space also uses gymnasium.Spaces to store data

```
Action Space:
    Continuous:
        [Steering (-1.0, 1.0), Throttle (0.0, 1.0), Brake (0.0, 1.0)]
    Discrete:
        [Action] (0: Accelerate, 1: Decelerate, 2: Left, 3: Right) <- It's a number from 0 to 3
```

Code format:

```python
# For continuous actions
self.action_space = spaces.Box(low=np.array([-1.0, 0.0, 0.0]), high=np.array([1.0, 1.0, 1.0]), dtype=np.float32)

# For discrete actions
self.action_space = spaces.Discrete(4)
```

## Env Methods

- Constructor(flag)
    - flag: This flag contains all the information about the scenario generation. 
    It's structure is: 
      - `"carla-rl-gym_{cont/disc}"` <- for any situation (`cont` for continuous, `disc` for discrete);
      - `"carla-rl-gym_{cont/disc}_{situation}-{situation2}"` <- for a specific situation(s) (It can contain 1 or more situations)

- reset(): Resets the environment to the initial state and returns the initial observation. Returns the observation space and the scenario dictionary (info).

## Training

To train the weather is random for testing it uses the specified in the scenarios JSON file.