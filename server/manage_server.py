from posix import environ
import boto3
import paramiko
import time
import os
import threading

class Server:

    def __init__(self):
        self.start_lock = threading.Lock()
        self.start_state = ""
        self.start_logs = []

        self.stop_lock = threading.Lock()
        self.stop_state = ""
        self.stop_logs = []

        self.instance_id = os.environ.get("EC2_ID")
        self.instance_user = os.environ.get("EC2_USER")
        self.ec2 = boto3.resource('ec2')
        self.instance = self.ec2.Instance(self.instance_id)

        ssh_dir = os.path.expanduser(os.environ.get("SSH_KEY_DIR"))
        ssh_pkey_filename = os.environ.get("SSH_KEY")
        self.privkey = paramiko.RSAKey.from_private_key_file(ssh_dir + ssh_pkey_filename)

        self.last_trigger = ""

    def start(self):
        
        with self.start_lock and self.stop_lock:
            self.start_state = "running"
            self.start_logs = []
            self.last_trigger = "start"

        # check state
        instance_state = self.instance.state['Name']
        if instance_state == 'stopped':
            # start if stopped
            print("EC2 instance not currently running. Starting instance...")
            with self.start_lock:
                self.start_logs.append("EC2 instance not currently running. Starting instance...")
            self.instance.start()
            self.instance.wait_until_running(WaiterConfig={'Delay': 5})
            time.sleep(5)
            self.instance.reload()
            print("EC2 instance started.")
            with self.start_lock:
                self.start_logs.append("EC2 instance started.")
            print("Waiting 20 seconds to allow the server to warmup...")
            with self.start_lock:
                self.start_logs.append("Waiting 20 seconds to allow the server to warmup before SSH...")
            time.sleep(20)
        elif instance_state != 'running':
            # exit if any other state
            print("EC2 instance currently", instance_state, ", try again later.")
            with self.start_lock:
                self.start_logs.append("EC2 instance currently", instance_state, ", try again later.")
                self.start_state = "done"
            return
        else:
            print("EC2 instance already running.")
            with self.start_lock:
                self.start_logs.append("EC2 instance already running.")

        # connect to instance via SSH
        print("Attempting SSH connection to EC2 instance...")
        with self.start_lock:
            self.start_logs.append("Attempting SSH connection to EC2 instance...")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.instance.public_ip_address, username=self.instance_user, pkey=self.privkey)
        except Exception as e:
            print("SSH failed to connect.")
            with self.start_lock:
                self.start_logs.append("SSH failed to connect.")
            print(e)
            with self.start_lock:
                self.start_logs.append(f"{e}")
                self.start_state = "done"
            ssh.close()
            return
        print("SSH successfully connected.")
        with self.start_lock:
            self.start_logs.append("SSH successfully connected.")

        # execute startup script
        print("Executing minecraft startup script...")
        with self.start_lock:
            self.start_logs.append("Executing minecraft startup script...")
        stdin, stdout, stderr = ssh.exec_command("./startup")
        while not stdout.channel.exit_status_ready():
            line = stdout.readline()
            line = line.rstrip()
            if line == "": continue
            print(line)
            with self.start_lock:
                self.start_logs.append(line)
        ssh.close()
        if (self.start_logs[-1] == "Minecraft server already running."):
            with self.start_lock:
                self.start_state = "done"
            return

        print("Minecraft server starting. Please wait atleast 10 seconds before attempting to connect.")
        with self.start_lock:
            self.start_logs.append("Minecraft server starting. Please wait atleast 10 seconds before attempting to connect.")
            self.start_state = "done"


    def run_start_thread(self):
        start_thread = threading.Thread(target=self.start, daemon=True)
        start_thread.start()
        

    def stop(self):

        with self.stop_lock and self.start_lock:
            self.stop_state = "running"
            self.stop_logs = []
            self.last_trigger = "stop"

        instance_state = self.instance.state['Name']
        if instance_state != "running":
            print("EC2 server not currently running.")
            with self.stop_lock:
                self.stop_logs.append("EC2 server not currently running.")
                self.stop_state = "done"
            return

        # connect to instance vs SSH
        print("Attempting SSH connection to EC2 instance...")
        with self.stop_lock:
            self.stop_logs.append("Attempting SSH connection to EC2 instance...")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.instance.public_ip_address, username=self.instance_user, pkey=self.privkey)
        except Exception as e:
            print("SSH failed to connect.")
            print(e)
            with self.stop_lock:
                self.stop_logs.append("SSH failed to connect.")
                self.stop_logs.append(f"{e}")
                self.stop_state = "done"
            ssh.close()
            return
        print("SSH successfully connected.")
        with self.stop_lock:
            self.stop_logs.append("SSH successfully connected.")

        # execute shutdown script
        print("Executing minecraft shutdown script...")
        with self.stop_lock:
            self.stop_logs.append("Executing minecraft shutdown script...")
        stdin, stdout, stderr = ssh.exec_command("./shutdown")
        while not stdout.channel.exit_status_ready():
            line = stdout.readline()
            line = line.rstrip()
            if line == "": continue
            print(line)
            with self.stop_lock:
                self.stop_logs.append(line)
        ssh.close()

        try:
            print("Stopping EC2 instance...")
            with self.stop_lock:
                self.stop_logs.append("Stopping EC2 instance...")
            self.instance.stop()
            self.instance.wait_until_stopped(WaiterConfig={'Delay': 5})
            self.instance.reload()
            print("EC2 instance stopped.")
            with self.stop_lock:
                self.stop_logs.append("EC2 instance stopped.")
        except Exception as e:
            print("Failed to stop EC2 instance.")
            print(e)
            with self.stop_lock:
                self.stop_logs.append("Failed to stop EC2 instance.")
                self.stop_logs.append(f"{e}")
        finally:
            with self.stop_lock:
                self.stop_state = "done"

    def run_stop_thread(self):
        stop_thread = threading.Thread(target=self.stop, daemon=True)
        stop_thread.start()

    def current_status(self):
        response = {}

        self.instance.reload()
        response['ec2_state'] = self.instance.state["Name"]
        with self.start_lock and self.stop_lock:
            response['start_state'] = self.start_state
            response['start_logs'] = self.start_logs
            response['stop_state'] = self.stop_state
            response['stop_logs'] = self.stop_logs
            response['last_trigger'] = self.last_trigger

        return response
