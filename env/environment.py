'''
Environment class for the carla environment.

It is a wrapper around the carla environment, and it is used to interact with the environment in a more convenient way.

It implements the following methods:
 - reset: resets the environment and returns the initial state
 - step: takes an action and returns the next state, the reward, a flag indicating if the episode is done, and a dictionary with extra information
 - close: closes the environment

Observation Space:
    [RGB image, LiDAR point cloud, Current position, Target position, Current situation]

    The current situation cannot be a string therefore it was converted to a numerical value using a dictionary to map the string to a number

    Dict:{
        Road:       0,
        Roundabout: 1,
        Junction:   2,
        Tunnel:     3,
    }

Action Space:
    Continuous:
        [Steering (-1.0, 1.0), Throttle/Brake (-1.0, 1.0)]
    Discrete:
        [Action] (0: Accelerate, 1: Decelerate, 2: Left, 3: Right) <- It's a number from 0 to 3

'''

import numpy as np
import json
import time
import random
import carla

import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register

register(
    id="carla-rl-gym-v0", # name-version
    entry_point="env.environment:CarlaEnv",
    max_episode_steps=10000,
)

from src.world import World
from src.server import CarlaServer
from src.vehicle import Vehicle
from src.display import Display
import configuration as config

# Name: 'carla-rl-gym-v0'
class CarlaEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": config.SIM_FPS}
    def __init__(self, continuous=True, scenarios=[], time_limit=60, initialize_server=True, random_weather=False, random_traffic=False, synchronous_mode=True, show_sensor_data=False, has_traffic=True, verbose=True):
        super().__init__()
        # Read the environment settings
        self.is_continuous = continuous
        self.random_weather = random_weather
        self.random_traffic = random_traffic
        self.synchronous_mode = synchronous_mode
        self.show_sensor_data = show_sensor_data
        self.has_traffic = has_traffic
        self.verbose = verbose

        # 1. Start the server
        self.automatic_server_initialization = initialize_server
        if self.automatic_server_initialization:
            self.server_process = CarlaServer.initialize_server(low_quality = config.SIM_LOW_QUALITY, offscreen_rendering = config.SIM_OFFSCREEN_RENDERING)
        
        # 2. Connect to the server
        self.world = World(synchronous_mode=self.synchronous_mode)

        # 3. Read the flag and get the appropriate situations
        self.__get_situations(scenarios)
        # 4. Create the vehicle
        self.vehicle = Vehicle(self.world.get_world())

        # 5. Create the observation space: TODO: Make the observation space more dynamic.
        # Lidar: (122,4) for default settings
        # Change this according to your needs.
        self.rgb_image_shape = (360, 640, 3)
        self.lidar_point_cloud_shape = (500*4,) # (500, 4) I'm trying it flattened to check if it works with stable-baselines3
        self.current_position_shape = (3,)
        self.target_position_shape = (3,)
        self.number_of_situations = 4

        self.observation_space = spaces.Dict({
            'rgb_data': spaces.Box(low=0, high=255, shape=self.rgb_image_shape, dtype=np.uint8),
            'lidar_data': spaces.Box(low=-np.inf, high=np.inf, shape=self.lidar_point_cloud_shape, dtype=np.float32),
            'position': spaces.Box(low=-np.inf, high=np.inf, shape=self.current_position_shape, dtype=np.float32),
            'target_position': spaces.Box(low=-np.inf, high=np.inf, shape=self.target_position_shape, dtype=np.float32),
            'situation': spaces.Discrete(self.number_of_situations)
        })

        self.observation = None

        # Action space
        if self.is_continuous:
            # For continuous actions
            self.action_space = spaces.Box(low=np.array([-1.0, -1.0]), high=np.array([1.0, 1.0]), dtype=np.float32)
        else:
            # For discrete actions
            self.action_space = spaces.Discrete(4)

        # Reward lambda values
        self.reward_lambdas = config.ENV_REWARDS_LAMBDAS
        
        # Truncated flag
        self.time_limit = time_limit
        self.time_limit_reached = False
        self.truncated = False  # Used for an episode that was terminated due to a time limit or errors

        # Variables to store the current state
        self.active_scenario_name = None
        self.active_scenario_dict = None

        self.situations_map = {
            "Road": 0,
            "Roundabout": 1,
            "Junction": 2,
            "Tunnel": 3
        }

        # Auxiliar variables
        self.has_stopped = False
        self.inside_stop_area = False
        self.first_episode = True
        
    # ===================================================== GYM METHODS =====================================================                
    # This reset loads a random scenario and returns the initial state plus information about the scenario
    # Options may include the name of the scenario to load    
    def reset(self, seed=None, options={'scenario_name': None}):
        # 1. Choose a scenario
        if options['scenario_name'] is not None:
            self.active_scenario_name = options['scenario_name']
        else:
            self.active_scenario_name = self.__chose_situation(seed)
        
        # 2. Load the scenario
        print(f"Loading scenario {self.active_scenario_name}...")
        try:
            self.load_scenario(self.active_scenario_name, seed)
        except KeyboardInterrupt as e:
            self.clean_scenario()
            print("Scenario loading interrupted!")
            exit(0)
        print("Scenario loaded!")
        
        # 3. Place the spectator
        self.place_spectator_above_vehicle()
        
        # 4. Get the initial state (Get the observation data)
        time.sleep(0.5)
        self.__update_observation()
        
        # 5. Start the timer
        self.__start_timer()
        print("Episode started!")
        
        self.number_of_steps = 0
        self.__is_done = False
        # Return the observation and the scenario information
        return self.observation, self.active_scenario_dict
    
    def render(self, mode='human'):
        if mode == 'human':
            self.world.tick()
            self.display.play_window_tick()
        else:
            raise NotImplementedError("This mode is not implemented yet")

    def step(self, action):
        # 0. Tick the world if in synchronous mode
        if self.synchronous_mode:
            try:
                self.world.tick()
            except KeyboardInterrupt:
                self.clean_scenario()
                print("Episode interrupted!")
                exit(0)
        self.number_of_steps += 1
        # 1. Control the vehicle
        self.__control_vehicle(np.array(action))
        # 1.5 Tick the display if it is active
        if self.show_sensor_data:
            self.display.play_window_tick()
        # 2. Update the observation
        self.__update_observation()
        # 3. Calculate the reward
        reward = self.__calculate_reward()
        # 4. Check if the episode is terminated
        terminated = self.__is_done
        # 5. Check if the episode is truncated
        try:
            self.truncated = self.__timer_truncated()
        except KeyboardInterrupt:
            self.clean_scenario()
            print("Episode interrupted!")
            exit(0)
        if self.truncated or terminated:
            self.clean_scenario()
        # 5. Return the observation, the reward, the terminated flag and the scenario information
        return self.observation, reward, terminated, self.truncated, self.active_scenario_dict

    # Closes everything, more precisely, destroys the vehicle, along with its sensors, destroys every npc and then destroys the world
    def close(self):
        # 1. Destroy the vehicle
        self.vehicle.destroy_vehicle()
        # 2. Destroy pedestrians and traffic vehicles
        self.world.destroy_vehicles()
        self.world.destroy_pedestrians()
        # 2. Destroy the world
        self.world.destroy_world()
        # 3. Close the server
        if self.automatic_server_initialization:
            CarlaServer.close_server(self.server_process)
    
    # ===================================================== REWARD METHODS =====================================================
    # More complex reward function for every driving task
    # def __calculate_reward(self):
    #     vehicle_location = self.vehicle.get_location()
    #     waypoint = self.__map.get_waypoint(vehicle_location, project_to_road=True, lane_type=carla.LaneType.Driving)
    #     target_position = np.array([self.active_scenario_dict['target_position']['x'], self.active_scenario_dict['target_position']['y'], self.active_scenario_dict['target_position']['z']])
    #     return self.reward_lambdas['orientation'] * self.__get_orientation_reward(waypoint, vehicle_location) + \
    #             self.reward_lambdas['distance'] * self.__get_distance_reward(waypoint, vehicle_location) + \
    #             self.reward_lambdas['speed'] * self.__get_speed_reward(self.vehicle.get_speed()) + \
    #             self.reward_lambdas['destination'] * self.__get_destination_reward(vehicle_location, target_position) + \
    #             self.reward_lambdas['collision'] * self.__get_collision_reward() + \
    #             self.reward_lambdas['light_pole_transgression'] * self.__get_light_pole_trangression_reward() + \
    #             self.reward_lambdas['stop_sign_transgression'] * self.__get_stop_sign_reward() + \
    #             self.reward_lambdas['time_limit'] * self.__get_time_limit_reward() + \
    #             self.reward_lambdas['time_driving'] * self.__get_time_driving_reward()

    # Simple reward function only for the vehicle's movement learning
    def __calculate_reward(self):
        vehicle_location = self.vehicle.get_location()
        waypoint = self.__map.get_waypoint(vehicle_location, project_to_road=True, lane_type=carla.LaneType.Driving)
        return self.reward_lambdas['orientation']               * self.__get_orientation_reward(waypoint, vehicle_location) + \
                self.reward_lambdas['distance']                 * self.__get_distance_reward(waypoint, vehicle_location) + \
                self.reward_lambdas['collision']                * self.__get_collision_reward() + \
                self.reward_lambdas['time_driving']             * self.__get_time_driving_reward()
    
    # This reward is based on the orientation of the vehicle according to the waypoint of where the vehicle is
    # R_orientation = \lambda * cos(\theta), where \theta is the angle between the vehicle and the waypoint
    def __get_orientation_reward(self, waypoint, vehicle_location):
        vh_yaw = self.__correct_yaw(self.vehicle.get_vehicle().get_transform().rotation.yaw)
        wp_yaw = self.__correct_yaw(waypoint.transform.rotation.yaw)

        return np.cos((vh_yaw - wp_yaw)*np.pi/180.)
    
    # This reward is based on the distance between the vehicle and the waypoint
    def __get_distance_reward(self, waypoint, vehicle_location):
        x_wp = waypoint.transform.location.x
        y_wp = waypoint.transform.location.y

        x_vehicle = vehicle_location.x
        y_vehicle = vehicle_location.y

        return np.linalg.norm([x_wp - x_vehicle, y_wp - y_vehicle])
    
    def __get_speed_reward(self, vehicle_speed, speed_limit=50):
        return vehicle_speed - speed_limit if vehicle_speed > speed_limit else 0.0
    
    # This reward is based on if the vehicle reached the destination. the reward will be based on the number of steps taken to reach the destination. The less steps, the higher the reward, but reaching the destination is the highest reward
    def __get_destination_reward(self, current_position, target_position, threshold=2.0): 
        if np.linalg.norm(current_position - target_position) < threshold:
            self.__is_done = True
            return max(-self.number_of_steps * (1 / config.ENV_MAX_STEPS) + 1, 0.35)
        else:
            return 0
    
    # Collision with other vehicles or pedestrians and even lane invasions
    def __get_collision_reward(self):
        if self.vehicle.collision_occurred() or self.vehicle.lane_invasion_occurred():
            self.__is_done = True
            return 1
        else:
            return 0

    # TODO: Implement for the stop sign as well
    def __get_light_pole_trangression_reward(self):
        # Get the current waypoint of the vehicle
        current_waypoint = self.__map.get_waypoint(self.vehicle.get_location(), project_to_road=True)

        # Get the traffic lights affecting the current waypoint
        traffic_lights = self.world.get_world().get_traffic_lights_from_waypoint(current_waypoint, distance=10.0)

        for traffic_light in traffic_lights:
            # Check if the traffic light is red
            if traffic_light.get_state() == carla.TrafficLightState.Red:
                # Get the stop waypoints for the traffic light
                stop_waypoints = traffic_light.get_stop_waypoints()

                # Check if the vehicle has passed the stop line
                for stop_waypoint in stop_waypoints:
                    if current_waypoint.transform.location.distance(stop_waypoint.transform.location) < 2.0 and self.vehicle.get_speed() > 0.1:
                        return 1
                        print("Red light infringement detected!")

        return 0
    
    def __get_time_limit_reward(self):
        return 1 if self.time_limit_reached else 0
    
    def __get_time_driving_reward(self):
        return 1 if not self.__is_done and self.vehicle.get_speed() > 1.0 else 0
    
    def __get_stop_sign_reward(self):        
        distance = 20.0  # meters (adjust as needed)
        
        current_location = self.vehicle.get_location()
        current_waypoint = self.__map.get_waypoint(current_location, project_to_road=True)
        
        # Get all the stop sign landmarks within a certain distance from the vehicle and on the same road
        stop_signs_on_same_road = []
        for landmark in current_waypoint.get_landmarks_of_type(distance, carla.LandmarkType.StopSign):
            landmark_waypoint = self.__map().get_waypoint(landmark.transform.location, project_to_road=True)
            if landmark_waypoint.road_id == current_waypoint.road_id:
                stop_signs_on_same_road.append(landmark)

        if len(stop_signs_on_same_road) == 0:
            if self.inside_stop_area and self.has_stopped:
                print("Vehicle has stopped at the stop sign.")
                self.has_stopped = False
                self.inside_stop_area = False
                return 0
            elif self.inside_stop_area and not self.has_stopped:
                print("Vehicle has not stopped at the stop sign.")
                self.has_stopped = False
                self.inside_stop_area = False
                return 1
            else:            
                return 0
        else:
            self.inside_stop_area = True

        # The vehicle entered the stop sign area
        for stop_sign in stop_signs_on_same_road:
            # Check if the vehicle has stopped
            if self.vehicle.get_speed() < 1.0:
                self.has_stopped = True

    # ===================================================== OBSERVATION/ACTION METHODS =====================================================
    def __update_observation(self):        
        observation_space = self.vehicle.get_observation_data()
        rgb_image = observation_space[0]
        lidar_point_cloud = observation_space[1]
        current_position = observation_space[2]
        target_position = np.array([self.active_scenario_dict['target_gnss']['lat'], self.active_scenario_dict['target_gnss']['lon'], self.active_scenario_dict['target_gnss']['alt']])
        situation = self.situations_map[self.active_scenario_dict['situation']]

        self.observation = {
            'rgb_data': np.uint8(rgb_image),
            'lidar_data': np.float32(lidar_point_cloud.flatten()),
            'position': np.float32(current_position),
            'target_position': np.float32(target_position),
            'situation': situation
        }
    
    # Change here if you have more sensors in the sensors file
    def __get_observation_shape(self):
        with open(config.VEHICLE_SENSORS_FILE, 'r') as f:
            sensors_dict = json.load(f)
        
        if "rgb_camera" in sensors_dict:
            self.rgb_image_shape = (sensors_dict["rgb_camera"]["image_size_y"], sensors_dict["rgb_camera"]["image_size_x"], 3)
        if "lidar" in sensors_dict:
            self.lidar_point_cloud_shape = (sensors_dict["lidar"]["channels"], 4)

    # ===================================================== SCENARIO METHODS =====================================================
    def load_scenario(self, scenario_name, seed=None):
        try:
            scenario_dict = self.situations_dict[scenario_name]
        except KeyError:
            new_name = self.__choose_random_situation(seed)
            scenario_dict = self.situations_dict[new_name]
            print(f"Scenario {scenario_name} not found! Loading random scenario {new_name}...")
        self.active_scenario_name = scenario_name
        self.__seed = seed
        self.active_scenario_dict = scenario_dict
         
        # World
        # This is a fix to a weird bug that happens when the first town is the same as the default map (comment and run a couple of times to see the bug)
        if self.first_episode and self.active_scenario_dict['map_name'] == self.world.get_active_map_name():
            self.world.reload_map()
        self.first_episode = False
        
        self.load_world(scenario_dict['map_name'])
        self.__map = self.world.update_traffic_map()
        time.sleep(2.0)
        if self.verbose:
            print("World loaded!")
        
        # Weather
        self.__load_weather(scenario_dict['weather_condition'])
        if self.verbose:
            print(self.world.get_active_weather(), " weather preset loaded!")
        
        # Ego vehicle
        self.__spawn_vehicle(scenario_dict)
        if self.show_sensor_data:   
            self.display = Display('Ego Vehicle Sensor feed', self.vehicle)
            self.display.play_window_tick()
        if self.verbose:
            print("Vehicle spawned!")
        
        # Traffic
        if self.has_traffic:
            self.__spawn_traffic(seed=seed)
            # self.world.spawn_pedestrians_around_ego(self.vehicle.get_location(), num_pedestrians=10)
            if self.verbose:
                print("Traffic spawned!")
        self.__toggle_lights()

    def clean_scenario(self):
        self.vehicle.destroy_vehicle()
        self.world.destroy_vehicles()
        self.world.destroy_pedestrians()
        if self.verbose:
            print("Scenario cleaned!")
    
    def print_all_scenarios(self):
        for idx, i in enumerate(self.situations_list):
            print(idx, ": ", i)
    
    def __spawn_vehicle(self, s_dict):
        location = (s_dict['initial_position']['x'], s_dict['initial_position']['y'], s_dict['initial_position']['z'])
        rotation = (s_dict['initial_rotation']['pitch'], s_dict['initial_rotation']['yaw'], s_dict['initial_rotation']['roll'])
        self.vehicle.spawn_vehicle(location, rotation)
    
    def load_world(self, name):
        self.world.set_active_map(name)
    
    def __toggle_lights(self):
        if "night" in self.world.get_active_weather().lower() or "noon" in self.world.get_active_weather().lower():
            self.world.toggle_lights(lights_on=True)
            self.vehicle.toggle_lights(lights_on=True)
        else:
            self.world.toggle_lights(lights_on=False)
            self.vehicle.toggle_lights(lights_on=False)

    def __load_weather(self, weather_name):
        if self.random_weather:
            self.world.set_random_weather()
        else:
            self.world.set_active_weather_preset(weather_name)
    
    # If the seed is not none send the seed, else make the scenario based on its name
    def __spawn_traffic(self, seed):
        if not self.random_traffic and self.active_scenario_dict['traffic_density'] == 'None':
            return

        # The traffic isn't random, so it will be based on the scenario name
        if not self.random_traffic:
            random.seed(self.active_scenario_name)
            seed = self.active_scenario_name
        
        if seed is not None:
            random.seed(seed)
        
        # Give density to the traffic
        if not self.random_traffic:
            if self.active_scenario_dict['traffic_density'] == 'Low':
                num_vehicles = random.randint(1, 5)
            else:
                num_vehicles = random.randint(10, 20)
        else:
            num_vehicles = random.randint(1, 20)
        
        self.world.spawn_vehicles_around_ego(self.vehicle.get_vehicle(), radius=100, num_vehicles_around_ego=num_vehicles, seed=seed)
    
    def __choose_random_situation(self, seed=None):
        if seed:
            np.random.seed(seed)
        return np.random.choice(self.situations_list)

    def __chose_situation(self, seed):
        if isinstance(seed, str):
            print("Seed needs to be an integer! Loading a random scenario...")
            return self.__choose_random_situation()
        else:
            return self.__choose_random_situation(seed)
    
    # ===================================================== SITUATIONS PARSING =====================================================
    # Filter the current situations based on the flag
    def __get_situations(self, scenarios):
        with open(config.ENV_SCENARIOS_FILE, 'r') as f:
            self.situations_dict = json.load(f)

        if scenarios:
            self.situations_dict = {key: value for key, value in self.situations_dict.items() if value['situation'] in scenarios}

        self.situations_list = list(self.situations_dict.keys())

            
    # ===================================================== AUX METHODS =====================================================
    def __control_vehicle(self, action):
        if self.is_continuous:
            self.vehicle.control_vehicle(action)
        else:
            self.vehicle.control_vehicle_discrete(action)

    def __timer_truncated(self):
        if time.time() - self.start_time > self.time_limit:
            self.time_limit_reached = True
            return True
        else:
            return False
    
    def __start_timer(self):
        self.start_time = time.time()
        
    # This function is used to correct the yaw angle to be between 0 and 360 degrees
    def __correct_yaw(self, x):
        return(((x%360) + 360) % 360)
    
    # ===================================================== DEBUG METHODS =====================================================
    def place_spectator_above_vehicle(self):
        self.world.place_spectator_above_location(self.vehicle.get_location())    

    def output_all_waypoints(self, spacing=5):
        waypoints = self.__map.generate_waypoints(distance=spacing)

        for w in waypoints:
            self.world.get_world().debug.draw_string(w.transform.location, 'O', draw_shadow=False,
                                       color=carla.Color(r=255, g=0, b=0), life_time=120.0,
                                       persistent_lines=True)
            
    def output_waypoints_to_target(self, spacing=5):
        current_location = self.vehicle.get_location()
        map_ = self.__map
        target_location = carla.Location(x=self.active_scenario_dict['target_position']['x'], y=self.active_scenario_dict['target_position']['y'], z=self.active_scenario_dict['target_position']['z'])

        # Find the closest waypoint to the current location
        current_waypoint = map_.get_waypoint(current_location)

        # Find the closest waypoint to the target location
        target_waypoint = map_.get_waypoint(target_location)

        # Generate waypoints along the route with the specified spacing
        waypoints = []
        while current_waypoint.transform.location.distance(target_waypoint.transform.location) > spacing:
            waypoints.append(current_waypoint.transform.location)
            current_waypoint = current_waypoint.next(spacing)[0]

        # Draw the waypoints
        for w in waypoints:
            self.world.get_world().debug.draw_string(w, 'O', draw_shadow=False,
                                                    color=carla.Color(r=255, g=0, b=0), life_time=10.0,
                                                    persistent_lines=True)