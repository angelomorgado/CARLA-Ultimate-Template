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
        
    def get_vehicle(self):
        return self.__vehicle

    def set_autopilot(self, boolean):
        self.__vehicle.set_autopilot(boolean)

    def create_vehicle(self, world):
        vehicle_bp = world.get_blueprint_library().filter(configuration.VEHICLE_MODEL)
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
    # Control the vehicle based on the action space provided by the environment. The action space is steering_angle,throttle,brake,lights_on]. The first three are continuous values normalized between [-1, 1] for the steering angle and [0, 1] for the throttle and brake and the last one is a boolean.
    def control_vehicle(self, action):
        # action = self.normalize_action(action)
        control = carla.VehicleControl()
        control.steering = action[0]
        control.throttle = action[1]
        control.brake = action[2]
        control.reverse = False
        control.use_adaptive_cruise_control = False
        control.lights = carla.VehicleLightState.NONE
        if action[3] == 1:
            control.lights = carla.VehicleLightState(carla.VehicleLightState.Position | carla.VehicleLightState.LowBeam | carla.VehicleLightState.LowBeam)
        self.__vehicle.apply_control(control)

    def normalize_action(self, action):
        # Check if the steering angle is normalized between [-1, 1] if not normalize it
        if action[0] > 1:
            action[0] = 1
        elif action[0] < -1:
            action[0] = -1
        
        # Check if the throttle is normalized between [0, 1] if not normalize it
        if action[1] > 1:
            action[1] = 1
        elif action[1] < 0:
            action[1] = 0
        return action