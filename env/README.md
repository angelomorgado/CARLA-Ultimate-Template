# CARLA Episode Generator

## Overview

The CARLA Episode Generator is a tool designed to facilitate the creation of diverse training scenarios for reinforcement learning (RL) models in the CARLA simulator. This tool allows you to define structured scenarios, controlling various environment parameters such as the map, weather conditions, traffic density, initial positions, and specific situations like roundabouts or junctions.

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
  "Town01-ClearNoon-Roundabout-0": {
    "map_name": "Town01",
    "weather_condition": "ClearNoon",
    "initial_position": {"x": 100.0, "y": 50.0, "z": 0.0},
    "initial_rotation": {"pitch": 0.0, "yaw": 90.0, "roll": 0.0},
    "target_position": {"x": 150.0, "y": 50.0, "z": 0.0},
    "situation": "Roundabout"
  },
  // More scenarios
}
```

### Attributes

The name of the scenario will be based on these attributes, then because there can be many there will be a counter after the name to differentiate.

#### Available Maps:

(Choose only the most appropriate)

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

- City Road
- Roundabout
- Junction
- Tunnel?
