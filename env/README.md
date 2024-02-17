# CARLA Episode Generator

## Overview

The CARLA Episode Generator is a tool designed to facilitate the creation of diverse training scenarios for reinforcement learning (RL) models in the CARLA simulator. This tool allows you to define structured scenarios, controlling various environment parameters such as the map, weather conditions, traffic density, initial positions, and specific situations like roundabouts or junctions.

## Usage

### Scenario Definition

Define training scenarios in a structured format, such as a JSON file, specifying the following parameters:

- `map_name`: The name of the CARLA map.
- `weather_condition`: The weather conditions (e.g., "ClearNoon").
- `traffic_density`: Traffic density level ("Low," "Medium," "High").
- `initial_position`: Initial position of the ego vehicle (x, y, z coordinates).
- `initial_rotation`: Initial rotation of the ego vehicle (pitch, yaw, roll)
- `situation`: Type of scenario or situation (e.g., "Roundabout," "Junction").

### Randomization

Implement controlled randomness by randomizing scenario selection. Ensure that certain scenarios are sampled with specific probabilities to control the variability in training.

### CARLA Environment Setup

Implement the `setup_carla_environment` method to configure the CARLA environment based on the loaded scenario. Use the CARLA Python API to set weather conditions, traffic density, initial vehicle position, and other relevant parameters.

## Scenario Definition Example

```json
{
  "0": {
    "map_name": "Town01",
    "weather_condition": "ClearNoon",
    "traffic_density": "Low",
    "initial_position": {"x": 100.0, "y": 50.0, "z": 0.0},
    "initial_rotation": {"pitch": 0.0, "yaw": 90.0, "roll": 0.0},
    "situation": "Roundabout"
  },
  // Add more scenarios as needed
}
```

### Attributes

The name of the scenario will be based on these attributes, then because there can be many there will be a counter after the name to differentiate.

#### Available Maps:

TODO

#### Available Weather Conditions

TODO

#### Available Traffic Densities

TODO

#### Available Conditions

TODO