# BiBEx Model
A docker image with the name *bibex_model* of the BiBEx Model application can be created by running the `setup.sh` or `setup.bat` installation file.

> **Note:**  This process may take a while, since this process includes downloading all utilized models and required dependencies

After an image was created, an user can create a docker container by executing the `run_container.sh` or `run_container.bat` file.

> **Note:** Due to HuggingFace's asynchronous creation of a cache directory on the first startup, the initial start of the container may fail. A consecutive restart of the container with `docker start bibex_model` should resolve this issue.

The documentation page of this application can be reached at [http://localhost:8000/docs](http://localhost:8000/docs). The default listening port is `8000`. To change the default port an user can alter the `run_container.sh` or `run_container.bat` file.