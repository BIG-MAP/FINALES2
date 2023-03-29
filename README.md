# FINALES 2
next **F**ast **IN**tention **A**gnostic **LE**arning **S**erver

This is the next generation of FINALES.

# Documents

Documents related to this project and its broader context can be found on the respective Wiki page of this project: [https://github.com/BIG-MAP/FINALES2/wiki/Links](https://github.com/BIG-MAP/FINALES2/wiki/Links)

# Setup of the Docker environment

Follow these steps to set up Docker for deplying the latest development version of FINALES2.

1. Install Docker on your system (make sure to keep the WSL configuration unchanged)

1. Download the docker file and the docker-compose.yml file from the FINALES2/Dockerfiles directory in the repository and save them to a directory of your choice

1. Run the Docker container for the FINALES environment using the following commands:

    1. In a terminal, navigate to the directory, where the two files are saved

    1. Run 'docker build -t finales:v0.1 .' (Do not overlook the trailing dot.)

    1. Run 'docker-compose up'

    1. Visit http://127.0.0.1:8888/lab?token=qwerty0123 in your browser to check, if the container is running or use the Docker desktop app for this


1. Initialize the database of FINALES by running 'finales db init'

1. Populate the database with dummy values, if you need to retrieve data for your tests by running 'finales devtest populate-db'

1. Start the FINALES server by running 'finales server start --ip 0.0.0.0'


# Local installation of the package

The FINALES2 repository has a file structures, which allows it to be installed like a regular Python package using pip. For this to work, please follow the steps below:

1. Clone the repository to your local machine.

1. Navigate to the folder containing the repository. This folder should contain the src folder.

1. Open a terminal in this path and enter `pip install -e ./` to install the package as an editable package, which applies changes to your local clone of the repository. You can also use `pip install ./` or `pip install .` to install it in non-editable mode, which is rather advisable for deployment, but not for development.

All the code for the FINALES2 package needs to go to the src/FINALES2 folder. Sub folders to this directory are possible.

The tutorial I followed and further details can be found in the following two links:
[https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html](https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html)
[https://packaging.python.org/en/latest/tutorials/packaging-projects/](https://packaging.python.org/en/latest/tutorials/packaging-projects/)


## Acknowledgements

This project has received funding from the European Union’s [Horizon 2020 research and innovation programme](https://ec.europa.eu/programmes/horizon2020/en) under grant agreement [No 957189](https://cordis.europa.eu/project/id/957189).
