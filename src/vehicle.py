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
        self.create_vehicle(world)

        # Vehicle Control attributes
        self.__speed = 0.0 # Km/h
        self.__steering_angle = 0.0 # [-1.0, 1.0]
        self.__lights_on = False

    def get_vehicle(self):
        return self.__vehicle

    def set_autopilot(self, boolean):
        self.__vehicle.set_autopilot(boolean)

    def create_vehicle(self, world):
        vehicle_id = self.read_vehicle_file(configuration.VEHICLE_PHYSICS_FILE)["id"]

        vehicle_bp = world.get_blueprint_library().filter(vehicle_id)
        spawn_points = world.get_map().get_spawn_points()
        
        while self.__vehicle is None:
            spawn_point = random.choice(spawn_points)
            transform = carla.Transform(
                spawn_point.location,
                spawn_point.rotation
            )
            try:
                self.__vehicle = world.try_spawn_actor(random.choice(vehicle_bp), transform)
            except:
                # try again if failed to spawn vehicle
                pass
        
        # Attach sensors
        vehicle_data = self.read_vehicle_file(configuration.VEHICLE_SENSORS_FILE)
        self.attach_sensors(vehicle_data, world)

    def get_sensor_dict(self):
        return self.__sensor_dict

    def read_vehicle_file(self, vehicle_json):
        with open(vehicle_json) as f:
            vehicle_data = json.load(f)
        
        return vehicle_data
    
    def destroy_vehicle(self):
        self.__vehicle.set_autopilot(False)

        # Destroy sensors
        for sensor in self.__sensor_dict:
            self.__sensor_dict[sensor].destroy()

        self.__vehicle.destroy()
    

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
    # Control the vehicle based on the continuous action space provided by the environment. The action space is steering_angle,throttle,brake,lights_on]. The first three are continuous values normalized between [-1, 1] for the steering angle and [0, 1] for the throttle and brake and the last one is a boolean.
    def control_vehicle(self, action):
        control = carla.VehicleControl()
        ackermann_control = carla.VehicleAckermannControl()
        ackermann_control.steer = action[0]
        # control.throttle = action[1]
        ackermann_control.speed = action[1]
        control.brake = action[2]
        control.lights = carla.VehicleLightState.NONE

        if action[3] == True:
            control.lights = carla.VehicleLightState.Position

        
        self.__vehicle.apply_control(control)
        self.__vehicle.apply_ackermann_control(ackermann_control)

    # Control the vehicle based on the discrete action space provided by the environment. The action space is [accelerate, decelerate, left, right, lights_on]. Out of these, only one action can be taken at a time.
    def control_vehicle_discrete(self, action):
        control = carla.VehicleControl()
        ackermann_control = carla.VehicleAckermannControl()

        # Accelerate
        if action == 0:
            self.__speed += 1
        # Decelerate
        elif action == 1:
            self.__speed -= 1
        # Left
        elif action == 2:
            self.__steering_angle = max(-1.0, self.__steering_angle - 0.1)
        # Right
        elif action == 3:
            self.__steering_angle = min(1.0, self.__steering_angle + 0.1)
        # Lights
        elif action == 4:
            self.__lights_on = not self.__lights_on
        
        ackermann_control.steer = self.__steering_angle 
        ackermann_control.speed = self.__speed / 3.6
        control.lights = carla.VehicleLightState.NONE

        if self.__lights_on:
            control.lights = carla.VehicleLightState.Position
        
        self.__vehicle.apply_control(control)
        self.__vehicle.apply_ackermann_control(ackermann_control)
            
    
    def normalize_action(self, action):
        # Normalize speed from km/h to m/s
        action[1] = action[1] / 3.6
    
    # TODO: Add debug to vehicle through world.debug

