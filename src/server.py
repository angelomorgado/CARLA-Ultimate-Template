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
        print('Starting Carla server, please wait...')
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        # Wait for the server to start
        time.sleep(15)
        print('Carla server started')

        return process
    
    @staticmethod
    def close_server(process):
        if os.name == 'posix':
            process.terminate()  # Terminate the process
            process.wait()  # Wait for it to complete
            print('Carla server closed')
        else:
            # On Windows, use taskkill to terminate the process and all its children
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)])
            print('Carla server closed')
