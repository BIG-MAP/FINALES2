# FINALES 2
next **F**ast **IN**tention **A**gnostic **LE**arning **S**erver

This is the next generation of FINALES.

# Documents

Documents related to this project and its broader context can be found on the respective Wiki page of this project: [https://github.com/BIG-MAP/FINALES2/wiki/Links](https://github.com/BIG-MAP/FINALES2/wiki/Links)

# Setup of the Docker environment

Follow these steps to set up Docker for deplying the latest development version of FINALES2.

1. You need an ssh key for the reposiory. You can follow this tutorial to set it up: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
    1. If you encounter an error when running the command `$ ssh-keygen -t ed25519 -C "your_email@example.com"` stating, that the command is not found, try to type the command manually instead of copying and pasting it.

1. Install Docker on your system (make sure to keep the WSL configuration unchanged)

1. Download the docker file and the docker-compose.yml file from the FINALES2/Dockerfiles directory in the repository and save them to a directory of your choice

1. Run the Docker container for the FINALES environment using the following commands:

    1. In a terminal, navigate to the directory, where the two files are saved

    1. Run `docker build -t finales:v0.1 .` (Do not overlook the trailing dot.)

    1. Run `docker volume create finales_data`

    1. Run `docker-compose up`\
    The first two commands are only ran the first time and are used to create the image and the volume (for data persistence) respectively. The third command uses the image to start a container: it will block the terminal when it is executed but it can be stopped by pressing the <CTRL + C> keys. This will also stop the container, but then it can be restarted by running the command again. Once again, you don't need to re-create the image and the volume each time you restart the container (unless you specifically want to update the software inside the container or delete the old data), you just need to re-run this last command `docker-compose up`.

        1. Modify environment variable to make endpoint for database dump applicable for the instance of the server \
        If one wish to open the endpoint database-dump in the API for a user, allowing the user to download the entire database e.g. for an archiving tenant, first open the docker-compose.yml file. Here the environment variable KEY_DATABASE_DUMP_ENDPOINT_ACCESS defines the key the user needs to access the endpoint. The default variable is called "DEFAULT_KEY_PLACEHOLDER", which is the only string not allowed for secruity measure. Change the key and run 'docker-compose up' to initiate the newly defined environment variable as the key


    1. Visit http://127.0.0.1:8888/lab?token=qwerty0123 in your browser to check, if the container is running or use the Docker desktop app for this

1. If you use VS code, download and install the following extensions:
    1. Docker
    1. Dev Containers

1. Open the Docker Desktop application

1. Click on the Docker icon in the left sided navigation bar in VS Code and start the container called finalesv0.1

1. Click on the icon for the remote explorer in the left sided navigation bar in VS Code

1. Find the finales2 docker in the list (if you did not run any other containers before, it is the first one in the list under the drop-down menu in DevContainers), hover over it and click the left most icon that pops up

1. This opens a new VS Code window within the Docker

1. Open the root folder `/`

1. Navigate to the directory called "data"

1. Create a folder called "ssh_keys"

1. Create a file called "github_key" and add your private key to this file

1. Navigate into the "ssh_keys" directory

1. Use the command `chmod 400 github_key` to change the permissions of the "github_key" file to read only

1. Navigate back to the "data" directory and clone the FINALES2 Github repository

# Get started with FINALES2

1. Install the FINALES2 package in editable mode
    1. Navigate to the FINALES2 repository in the Docker
    1. `pip install -e .`

# Start FINALES2

1. Initialize the database of FINALES by running `finales db init`

1. Populate the database with dummy values, if you need to retrieve data for your tests by running `finales devtest populate-db`

1. Start the FINALES server by running `finales server start --ip 0.0.0.0`

# Make FINALES2 accessible from within a network
1. Follow all the above instructions

1. Stop the Docker image

1. Ping the host, which ran your docker from within the network and make sure this is successful

1. Change the line number 7 in the docker-compose.yml to `- "8888:13372"`

1. Add the following below line number 12 inside the finales seciton
   ```
   extra_hosts:
   - "FINALEShost:<the IP of your host in the network>"
   ```

1. Save the .yml file

1. Open the Dockerfile and change line 26 to the following `CMD ["jupyter-lab","--ip=0.0.0.0", "--no-browser","--allow-root","--port=13371"]`

1. Save the Dockerfile

1. Open a terminal and navigate to the directory, in which the Dockerfile and the docker-compose.yml file are saved

1. Run the Docker container for the FINALES environment using the following commands:

    1. In a terminal, navigate to the directory, where the two files are saved

    1. Run `docker build -t finales:v0.1 .` (Do not overlook the trailing dot.)

    1. Run `docker volume create finales_data`

    1. Run `docker-compose up`

1. Follow the steps described under Start FINALES2 except for the last one. Exchange this to be `finales server start --ip 0.0.0.0 --port 13372`

1. Check the connection by running the following command on another computer *in the same network*
   ```
   python
   mport requests

    r = requests.get('http://<the IP of your host in the network>:8888')

    print(r.status_code)
    ```
    The response should be 200 and the server should also show a response 200

# Local installation of the package

The FINALES2 repository has a file structure, which allows it to be installed like a regular Python package using pip. For this to work, please follow the steps below:

1. Clone the repository to your local machine.

1. Navigate to the folder containing the repository. This folder should contain the src folder.

1. Open a terminal in this path and enter `pip install -e ./` to install the package as an editable package, which applies changes to your local clone of the repository. You can also use `pip install ./` or `pip install .` to install it in non-editable mode, which is rather advisable for deployment, but not for development.

All the code for the FINALES2 package needs to go to the src/FINALES2 folder. Sub folders to this directory are possible.

The tutorial I followed and further details can be found in the following two links:
[https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html](https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html)
[https://packaging.python.org/en/latest/tutorials/packaging-projects/](https://packaging.python.org/en/latest/tutorials/packaging-projects/)


# Acknowledgements

This project received funding from the European Union’s [Horizon 2020 research and innovation programme](https://ec.europa.eu/programmes/horizon2020/en) under grant agreement [No 957189](https://cordis.europa.eu/project/id/957189) (BIG-MAP). The authors acknowledge BATTERY2030PLUS, funded by the European Union’s Horizon 2020 research and innovation program under grant agreement no. 957213. This work contributes to the research performed at CELEST (Center for Electrochemical Energy Storage Ulm-Karlsruhe) and was co-funded by the German Research Foundation (DFG) under Project ID 390874152 (POLiS Cluster of Excellence).
