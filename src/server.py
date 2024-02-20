import os
import subprocess
import time

class CarlaServer:    
    @staticmethod
    def initialize_server(low_quality = False, offscreen_rendering = False):
        # Get environment variable CARLA_SERVER that contains the path to the Carla server directory
        carla_server = os.getenv('CARLA_SERVER')

        # If it is Unix add the CarlaUE4.sh to the path else add CarlaUE4.exe
        if os.name == 'posix':
            carla_server = os.path.join(carla_server, 'CarlaUE4.sh')
            command = f"bash {carla_server} {'--quality-level=Low' if low_quality else ''} {'--RenderOffScreen' if offscreen_rendering else ''}"
        else:
            carla_server = os.path.join(carla_server, 'CarlaUE4.exe')
            command = f"{carla_server} {'--quality-level=Low' if low_quality else ''} {'--RenderOffScreen' if offscreen_rendering else ''}"

        # Run the command
        print('Starting Carla server, please wait 10 seconds...')
        subprocess.run(command, shell=True)
    
        # Wait for the server to start
        time.sleep(10)
        print('Carla server started')
    
    @staticmethod
    def close_server():
        subprocess.run("kill -9 $ps aux |grep Unreal")
        print('Carla server closed')
