# JupyterHub configuration
import os
import sys
import nativeauthenticator
pjoin = os.path.join

# jupyterhub_config.py
c = get_config()

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.JupyterHub.authenticator_class = 'nativeauthenticator.NativeAuthenticator'

# from jupyter_client.localinterfaces import public_ips
# c.JupyterHub.hub_ip = public_ips()[0]
c.JupyterHub.hub_ip = '0.0.0.0' # os.environ['HUB_IP'] # 'jupyterhub'
# c.JupyterHub.hub_port = 8888
c.JupyterHub.hub_connect_ip = os.environ['HUB_IP']
c.JupyterHub.template_paths = [f"{os.path.dirname(nativeauthenticator.__file__)}/templates/"]

runtime_dir = os.path.join('/srv/jupyterhub')
# in /var/run/jupyterhub
c.JupyterHub.cookie_secret_file = pjoin(runtime_dir, 'cookie_secret')
c.JupyterHub.db_url = pjoin(runtime_dir, 'jupyterhub.sqlite')
# or `--db=/path/to/jupyterhub.sqlite` on the command-line


## Docker Spawner
c.DockerSpawner.image = os.environ['DOCKER_JUPYTERLAB_IMAGE']
# Connect containers to this Docker network
network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }
# Remove container once they are stopped
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")
rmcont = str2bool(os.environ['CONTAINER_JUPYTERLAB_REMOVE']) if 'CONTAINER_JUPYTERLAB_REMOVE' in list(os.environ) else True
c.DockerSpawner.remove = rmcont
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True
c.DockerSpawner.cmd = 'start-singleuser.sh'
c.DockerSpawner.default_url = os.environ['HUB_DEFAULT_URL']


# user data persistence
# see https://github.com/jupyterhub/dockerspawner#data-persistence-and-dockerspawner
lab_work_dir = '/home/jovyan/work' # os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
lab_share_dir = '/home/jovyan/share'
c.DockerSpawner.notebook_dir = lab_work_dir

volumes_dict = {'jupyterlab-share': lab_share_dir}
if 'HOST_WORK_DIR' in list(os.environ):
  volumes_dict[os.environ['HOST_WORK_DIR']+'/{username}'] = {"bind": lab_work_dir, "mode": "rw"}
else:
  volumes_dict['jupyterlab-user-{username}'] = lab_work_dir
c.DockerSpawner.volumes = volumes_dict


# authenticator
c.Authenticator.admin_users = {os.environ['HUB_ADMIN_USER']}
c.Authenticator.check_common_password = True
c.Authenticator.minimum_password_length = 6
c.Authenticator.allowed_failed_logins = 3


# # Other stuff
# c.Spawner.cpu_limit = 1
# c.Spawner.mem_limit = '2G'

# c.Spawner.http_timeout = 600
# c.Spawner.start_timeout = 600
# Services
c.JupyterHub.services = [
    {
        "name": "idle-culler",
        "command": [
            sys.executable, "-m",
            "jupyterhub_idle_culler",
            "--timeout=3600"
        ],
    }
]

c.JupyterHub.load_roles = [
    {
        "name": "idle-culler",
        "description": "Culls idle servers",
        "scopes": ["read:users:name", "read:users:activity", "servers"],
        "services": ["idle-culler"],
    }
]
