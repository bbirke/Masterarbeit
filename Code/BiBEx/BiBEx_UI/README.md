# BiBEx UI
A docker image with the name *bibex_ui* of the BiBEx UI application can be created by running the `setup.sh` or `setup.bat` installation file. The BiBEx API endpoint can be set as docker build argument in the installation script `bibex_model_endpoint=http://localhost:8000`.

After the image was created, an user can create a docker container by executing the `run_container.sh` or `run_container.bat` file.

The application can be reached at [http://localhost](http://localhost). The default listening port is `80`. To change the default port an user can alter the `run_container.sh` or `run_container.bat` file.