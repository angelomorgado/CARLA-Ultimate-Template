import carla

import random
import time
import numpy as np
import math

'''
Traffic Controller module:
    It provides the functionality to spawn, destroy, and control vehicles and pedestrians in the Carla simulation.

    TODO: - Implement generation of other types of vehicles (e.g, trucks, motorcycles, bicycles, etc.)
          - Pedestrians still can't move
          - Make the spawning deterministic (e.g, using a json or a database to store the spawn points and the vehicles to spawn)
'''

class TrafficControl:
    def __init__(self, world) -> None:
        self.active_vehicles = []
        self.active_pedestrians = []
        self.active_ai_controllers = []
        self.__world = world


    # ============ Vehicle Control ============
    def spawn_vehicles(self, num_vehicles = 10, autopilot_on = False):
        if num_vehicles < 1:
            print("You need to spawn at least 1 vehicle.")
            return
        
        print(f"Spawning {num_vehicles} vehicle(s)...")

        vehicle_bp = self.__world.get_blueprint_library().filter('vehicle.*')
        spawn_points = self.__world.get_map().get_spawn_points()

        for i in range(num_vehicles):
            vehicle = None
            while vehicle is None:
                spawn_point = random.choice(spawn_points)
                transform = carla.Transform(
                    spawn_point.location,
                    spawn_point.rotation
                )
                try:
                    vehicle = self.__world.try_spawn_actor(random.choice(vehicle_bp), transform)
                except:
                    # try again if failed to spawn vehicle
                    continue
            
            self.active_vehicles.append(vehicle)
            # time.sleep(0.1)
        print('Successfully spawned {} vehicles!'.format(num_vehicles))
    
    def destroy_vehicles(self):
        for vehicle in self.active_vehicles:
            vehicle.destroy()
        self.active_vehicles = []
        print('Destroyed all vehicles!')
    
    def toggle_autopilot(self, autopilot_on = True):
        for vehicle in self.active_vehicles:
            vehicle.set_autopilot(autopilot_on)
    

    def spawn_vehicles_around_ego(self, ego_vehicle, radius, num_vehicles_around_ego):
        self.spawn_points = self.__world.get_map().get_spawn_points()
        np.random.shuffle(self.spawn_points)  # shuffle all the spawn points
        ego_location = ego_vehicle.get_location()
        accessible_points = []

        for spawn_point in self.spawn_points:
            dis = math.sqrt((ego_location.x - spawn_point.location.x)**2 +
                            (ego_location.y - spawn_point.location.y)**2)
            # it also can include z-coordinate, but it is unnecessary
            if dis < radius:
                print(dis)
                accessible_points.append(spawn_point)

        vehicle_bps = self.__world.get_blueprint_library().filter('vehicle.*.*')   # don't specify the type of vehicle
        # vehicle_bps = [x for x in vehicle_bps if int(
        #     x.get_attribute('number_of_wheels')) == 4]  # only choose car with 4 wheels

        vehicle_list = []  # keep the spawned vehicle in vehicle_list, because we need to link them with traffic_manager
        if len(accessible_points) < num_vehicles_around_ego:
            # if your radius is relatively small,the satisfied points may be insufficient
            num_vehicles_around_ego = len(accessible_points)

        for i in range(num_vehicles_around_ego):  # generate the free vehicle
            point = accessible_points[i]
            vehicle_bp = np.random.choice(vehicle_bps)
            try:
                vehicle = self.__world.spawn_actor(vehicle_bp, point)
                vehicle_list.append(vehicle)
            except:
                print('failed')  # if failed, print the hints.
                pass

    
            
    # ============ Pedestrian Control ============
    def spawn_pedestrians(self, num_pedestrians=10):
        if num_pedestrians < 1:
            print("You need to spawn at least 1 pedestrian.")
            return

        print(f"Spawning {num_pedestrians} pedestrian(s)...")

        for _ in range(num_pedestrians):
            walker_bp = random.choice(self.__world.get_blueprint_library().filter('walker.pedestrian.*'))

            if walker_bp.has_attribute('is_invincible'):
                walker_bp.set_attribute('is_invincible', 'false')

            walker_bp.set_attribute('speed', str(random.uniform(0.5, 1.0)))

            spawn_point = carla.Transform(location=self.__world.get_random_location_from_navigation())

            # Spawn the walker
            walker = self.__world.try_spawn_actor(walker_bp, spawn_point)
            if walker:
                self.active_pedestrians.append(walker)

                # Spawn the walker controller
                walker_controller_bp = self.__world.get_blueprint_library().find('controller.ai.walker')

                # Attach AI controller to the walker
                ai_controller = self.__world.try_spawn_actor(walker_controller_bp, carla.Transform(), walker)

                if ai_controller:
                    try:
                        # Start the walker controller
                        ai_controller.start()

                        # Set the walker's target location
                        ai_controller.go_to_location(self.__world.get_random_location_from_navigation())

                        # Set the walker's max speed
                        ai_controller.set_max_speed(1 + random.random())

                        # Store the AI controller
                        self.active_ai_controllers.append(ai_controller)
                    except Exception as e:
                        print(f"Error initializing walker controller: {e}")

        print(f"Successfully spawned {len(self.active_pedestrians)} pedestrians!")


    def destroy_pedestrians(self):
        for idx, pedestrian in enumerate(self.active_pedestrians):
            try:
                pedestrian.destroy()
                self.active_ai_controllers[idx].stop()
            except Exception as e:
                print(f"Error destroying pedestrians: {e}")

        self.active_pedestrians = []
        self.active_ai_controllers = []
        print('Destroyed all pedestrians!')
