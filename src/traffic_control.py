import carla

import random
import time

class TrafficControl:
    def __init__(self, world, client) -> None:
        self.active_vehicles = []
        self.active_pedestrians = []
        self.__world = world
        self.__client = client

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

    # TODO: Implement generation of other types of vehicles (e.g, trucks, motorcycles, bicycles, etc.)
            
    # ============ Pedestrian Control ============
    def spawn_pedestrians(self, num_pedestrians=10):
        if num_pedestrians < 1:
            print("You need to spawn at least 1 pedestrian.")
            return

        # Get spawn locations
        spawn_points = []
        for i in range(num_pedestrians):
            spawn_point = carla.Transform()
            loc = self.__world.get_random_location_from_navigation()
            if loc is not None:
                spawn_point.location = loc
                spawn_points.append(spawn_point)
        
        # Spawn pedestrians
        batch = []
        walker_speed = []

        for spawn_point in spawn_points:
            walker_bp = random.choice(self.__world.get_blueprint_library().filter('walker.pedestrian.*'))

            if walker_bp.has_attribute('is_invincible'):
                walker_bp.set_attribute('is_invincible', 'false')

            walker_bp.set_attribute('speed', str(random.uniform(0.5, 1.0)))

            batch.append(carla.command.SpawnActor(walker_bp, spawn_point))

        pedestrians = self.__client.apply_batch_sync(batch, True)

        for response in pedestrians:
            if response.error:
                # print(response.error)
                pass
            else:
                walker = response.actor_id
                self.active_pedestrians.append(walker)

        print(f"Successfully spawned {len(self.active_pedestrians)} pedestrians!")


    def destroy_pedestrians(self):
        for pedestrian in self.active_pedestrians:
            pedestrian.destroy()
        self.active_pedestrians = []
        print('Destroyed all pedestrians!')