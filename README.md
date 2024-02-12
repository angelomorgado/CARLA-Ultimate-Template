# CARLA Ultimate Template

This project acts as a template for the Carla Simulator. It is a collection of various features and functionalities that can be used to create a custom environment for the Carla Simulator. More features will be added as the project progresses.
This project can be seen as an engine of sorts, and acts as a starting point for creating various scenarios for the Carla Simulator with relative ease as all the necessary components are already in place.

All the modules are designed to be as modular as possible, so that they can be easily integrated into other projects and they are organized in classes and functions.

---

# TODO

- [ ] Add support for synchronous mode


---

## To Run the Project

1. It is recommended to use a virtual environment with python 3.8. 
2. Install the requirements with `pip install -r requirements.txt`
3. Run the CARLA server with the desired map
4. Run the project with `python main.py`

---

## Modules

- `main.py`: Main file, controls the entire process
- `display.py`: Contains the methods to display the sensors in a PyGame window
- `vehicle.py`: Contains the methods responsible for creating the ego vehicle, attaching sensors to it, destroying it, and in future versions, controlling it
- `sensors.py`: Contains classes for each sensor, with methods to attach them to the vehicle, and to get their data through callbacks
- 'config.py': Contains option parameters for the simulation

These modules are coded to be extremely dynamic, allowing their integration with any other project.

---

## Sensors

Available sensors:
- RGB Camera
- LiDAR
- Radar
- GNSS
- IMU
- Collision
- Lane Invasion

Future sensors:
- Semantic Segmentation Camera
- Instance Segmentation Camera
- Depth Camera
- Lidar Semantic Segmentation
- Obstacle Detection
- Optical Flow Camera (AKA: Motion Camera)

The collision and lane invasion sensors are special in the way that they are only triggered when the vehicle collides with something or invades a lane, respectively. And their information is not displayed in the PyGame window, but in the terminal.

---

## Features

### Custom Vehicular Sensory

By leveraging json files, it is possible to create various builds of vehicles with different sensors and configurations. This allows for the creation of custom vehicles with different sensor configurations. Such example of a build can be found in the `test_sensors.json` file.

### Sensor Visualization

Through Pygame, it is possible to visualize the sensor data in real-time. This is useful for debugging and testing purposes.


### Vehicle Physics Customization

Vehicles have their physics changed according to the weather. This template allows for the customization of a vehicle's physics based on the weather conditions. This is useful for simulating the effects of weather on a vehicle's performance. This can be achieved through JSON files. One such example can be found in the `test_vehicle_physics.json` file.

#### Affected Vehicle Physics by Weather Conditions Such as Rain

- **Mass** affects the vehicle's weight. A heavier vehicle may have more traction, but it may also be slower to accelerate and brake.

- **Tire friction** determines the friction between the tires and the road. Higher values result in more grip, while lower values can lead to reduced traction on slippery surfaces.
Damping Rate:

- **Damping Rate** affects the damping force applied to the wheels. It influences how quickly the wheel's vibrations are dampened. Adjusting this parameter can impact the vehicle's response on different surfaces.

- **Longitudinal Swiftness** influences how the tire responds to longitudinal forces, affecting acceleration and braking. Lower values may lead to wheel slip on slippery surfaces.

- **Drag Coefficient** influences the air resistance. While not directly related to the road surface, it can impact the overall dynamics of the vehicle, especially at higher speeds.
