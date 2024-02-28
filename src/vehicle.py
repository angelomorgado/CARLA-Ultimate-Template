'''
Vehicle Module:
    It provides the functionality to create and destroy the vehicle and attach the sensors present in a JSON file to it.

    It also provides the functionlity to control the vehicle based on the action space provided by the environment.
'''

import carla
import random
import json
import os

import configuration
import src.sensors as sensors

class Vehicle:
    def __init__(self, world):
        self.__vehicle = None
        self.__sensor_dict = {}
        self.__world = world

        self.__control = carla.VehicleControl()
        self.__ackermann_control = carla.VehicleAckermannControl()

        # Vehicle Control attributes for discrete action space
        self.__throttle = 0.0
        self.__steering_angle = 0.0 # [-1.0, 1.0]

    def get_vehicle(self):
        return self.__vehicle

    def set_autopilot(self, boolean):
        if self.__vehicle:
            self.__vehicle.set_autopilot(boolean)
        else:
            print("Error: No vehicle to set autopilot. Try spawning the vehicle first.")

    def spawn_vehicle(self, location=None, rotation=None):
        # Check if the vehicle is already spawned
        if self.__vehicle is not None:
            if configuration.VERBOSE:
                print("Error: Vehicle already spawned. Destroy the vehicle first.")
            
            self.destroy_vehicle()

        vehicle_id = self.read_vehicle_file(configuration.VEHICLE_PHYSICS_FILE)["id"]

        vehicle_bp = self.__world.get_blueprint_library().filter(vehicle_id)
        
        # If location is not provided, spawn the vehicle in a random location
        if location is None:
            spawn_points = self.__world.get_map().get_spawn_points()
            while self.__vehicle is None:
                spawn_point = random.choice(spawn_points)
                transform = carla.Transform(
                    spawn_point.location,
                    spawn_point.rotation
                )
                try:
                    self.__vehicle = self.__world.try_spawn_actor(random.choice(vehicle_bp), transform)
                except:
                    # try again if failed to spawn vehicle
                    pass
            print("Spawning vehicle at random location: ", spawn_point.location, " and rotation: ", spawn_point.rotation, " Spawn point: ", spawn_point)
        # If location is provided, spawn the vehicle in the provided location and rotation
        else:
            carla_location = carla.Location(x=location[0], y=location[1], z=location[2])
            carla_rotation = carla.Rotation(pitch=rotation[0], yaw=rotation[1], roll=rotation[2])
            transform = carla.Transform(
                carla_location,
                carla_rotation
            )
            print("Spawning vehicle at location: ", carla_location, " and rotation: ", carla_rotation, " Transform: ", transform)
            try:
                self.__vehicle = self.__world.try_spawn_actor(random.choice(vehicle_bp), transform)
            except:
                print("Error: Failed to spawn vehicle. Check the location and rotation provided.")
                return
        
        # Attach sensors
        vehicle_data = self.read_vehicle_file(configuration.VEHICLE_SENSORS_FILE)
        self.attach_sensors(vehicle_data, self.__world)

    def get_sensor_dict(self):
        return self.__sensor_dict

    def read_vehicle_file(self, vehicle_json):
        with open(vehicle_json) as f:
            vehicle_data = json.load(f)
        
        return vehicle_data
    
    def destroy_vehicle(self):
        if self.__vehicle is None:
            return

        # Destroy sensors
        for sensor in self.__sensor_dict:
            self.__sensor_dict[sensor].destroy()
        self.__vehicle.destroy()
        if configuration.VERBOSE:
            print("Successfully destroyed the ego vehicle and its sensors.")
        self.__vehicle = None

    # ====================================== Vehicle Sensors ======================================
    def attach_sensors(self, vehicle_data, world):
        for sensor in vehicle_data:
            if sensor == 'rgb_camera':
                self.__sensor_dict[sensor]    = sensors.RGB_Camera(world=world, vehicle=self.__vehicle, sensor_dict=vehicle_data['rgb_camera'])
                os.makedirs('data/rgb_camera', exist_ok=True)
            elif sensor == 'lidar':
                self.__sensor_dict[sensor]    = sensors.Lidar(world=world, vehicle=self.__vehicle, sensor_dict=vehicle_data['lidar'])
                os.makedirs('data/lidar', exist_ok=True)
            elif sensor == 'radar':
                self.__sensor_dict[sensor]    = sensors.Radar(world=world, vehicle=self.__vehicle, sensor_dict=vehicle_data['radar'])
                os.makedirs('data/radar', exist_ok=True)
            elif sensor == 'gnss':
                self.__sensor_dict[sensor]    = sensors.GNSS(world=world, vehicle=self.__vehicle, sensor_dict=vehicle_data['gnss'])
            elif sensor == 'imu':
                self.__sensor_dict[sensor]    = sensors.IMU(world=world, vehicle=self.__vehicle, sensor_dict=vehicle_data['imu'])
            elif sensor == 'collision':
                self.__sensor_dict[sensor]    = sensors.Collision(world=world, vehicle=self.__vehicle, sensor_dict=vehicle_data['collision'])
            elif sensor == 'lane_invasion':
                self.__sensor_dict[sensor]    = sensors.Lane_Invasion(world=world, vehicle=self.__vehicle, sensor_dict=vehicle_data['lane_invasion'])
            else:
                print('Error: Unknown sensor ', sensor)
    
    # This method returns the observation data from the used sensors in the environment (it excludes the collision and lane invasion sensors, which are used for the reward function only). If you're using a different environment, you should change this method to return the observation data that you need.
    # TODO: Make it dynamic to each model.
    # In this case [RGB image, LiDAR point cloud, Current position], the target position and the current situation are added in the environment module.
    def get_observation_data(self):
        rgb_data = self.__sensor_dict['rgb_camera'].get_data()
        lidar_data = self.__sensor_dict['lidar'].get_data()
        gnss_data = self.__sensor_dict['gnss'].get_data()

        # Perform necessary processing on the data # TODO: Should the data be really flattened?
        # rgb_data = rgb_data.reshape(-1) # Flatten the image so it can be concatenated with the rest of the data point cloud

        return [rgb_data, lidar_data, gnss_data]

    # ====================================== Vehicle Physics ======================================

    # Change the vehicle physics to a determined weather that is stated in the JSON file.
    def change_vehicle_physics(self, weather_condition):
        # Read JSON file
        physics_data = self.read_vehicle_file(configuration.VEHICLE_PHYSICS_FILE)

        # Check if the provided weather exists
        if weather_condition not in physics_data["weather_conditions"]:
            print(f"Weather physics configuration {weather_condition} does not exist!")
            return

        physics_control = self.__vehicle.get_physics_control()
        physics_data = physics_data["weather_conditions"][weather_condition]

        # Create Wheels Physics Control (This simulation assumes that wheels on the same axle have the same physics control)
        front_wheels  = carla.WheelPhysicsControl(tire_friction=physics_data["front_wheels"]["tire_friction"], 
                                                    damping_rate=physics_data["front_wheels"]["damping_rate"], 
                                                    long_stiff_value=physics_data["front_wheels"]["long_stiff_value"])

        rear_wheels   = carla.WheelPhysicsControl(tire_friction=physics_data["rear_wheels"]["tire_friction"], 
                                                    damping_rate=physics_data["rear_wheels"]["damping_rate"], 
                                                    long_stiff_value=physics_data["rear_wheels"]["long_stiff_value"])

        wheels = [front_wheels, front_wheels, rear_wheels, rear_wheels]

        physics_control.wheels = wheels
        physics_control.mass = physics_data["vehicle"]["mass"]
        physics_control.drag_coefficient = physics_data["vehicle"]["drag_coefficient"]
        self.__vehicle.apply_physics_control(physics_control)
        print(f"Vehicle's physics changed to {weather_condition} weather")

    def print_vehicle_physics(self):
        vehicle_physics = self.__vehicle.get_physics_control()
        print("Vehicle's attributes:")
        print(f"Vehicle's name: {self.__vehicle.type_id}")
        print(f"mass: {vehicle_physics.mass}")
        print(f"drag_coefficient: {vehicle_physics.drag_coefficient}")

        # Wheels' attributes
        print("\nFront Wheels' attributes:")
        print(f"tire_friction: {vehicle_physics.wheels[0].tire_friction}")
        print(f"damping_rate: {vehicle_physics.wheels[0].damping_rate}")
        print(f"long_stiff_value: {vehicle_physics.wheels[0].long_stiff_value}")

        print("\nRear Wheels' attributes:")
        print(f"tire_friction: {vehicle_physics.wheels[1].tire_friction}")
        print(f"damping_rate: {vehicle_physics.wheels[1].damping_rate}")
        print(f"long_stiff_value: {vehicle_physics.wheels[1].long_stiff_value}")

    # ====================================== Vehicle Control ======================================
    # Control the vehicle based on the continuous action space provided by the environment. The action space is steering_angle,throttle,brake,lights_on]. The first three are continuous values normalized between [-1, 1] for the steering angle and [0, 1] for the throttle and brake.
    def control_vehicle(self, action):                
        self.__control.steer = max(-1.0, min(action[0], 1.0))
        self.__control.throttle = min(action[1], 1.0)
        self.__control.brake = min(action[2], 1.0)
        
        self.__vehicle.apply_control(self.__control)

    # Control the vehicle based on the discrete action space provided by the environment. The action space is [accelerate, decelerate, left, right]. Out of these, only one action can be taken at a time.
    # TODO: Change to throttle and brakes
    def control_vehicle_discrete(self, action):
        # Accelerate
        if action == 0:
            self.__throttle = min(self.__throttle + 0.05, 1.0)
        # Decelerate
        elif action == 1:
            self.__throttle = max(self.__throttle - 0.05, 0.0)
        # Brake More
        elif action == 2:
            self.__control.brake = min(self.__control.brake + 0.05, 1.0)
        # Brake Less
        elif action == 3:
            self.__control.brake = max(self.__control.brake - 0.05, 0.0)
        # Left
        elif action == 4:
            self.__steering_angle = max(-1.0, self.__steering_angle - 0.1)
        # Right
        elif action == 5:
            self.__steering_angle = min(1.0, self.__steering_angle + 0.1)

        self.__control.throttle = self.__throttle
        self.__control.steer = self.__steering_angle
        self.__vehicle.apply_control(self.__control)
            
    # TODO: Add debug to vehicle through world.debug

