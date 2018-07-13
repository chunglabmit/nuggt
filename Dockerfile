FROM ubuntu

RUN apt-get update
RUN apt-get install -y tzdata
RUN echo "America/Boston" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get install -y cmake swig python3 python3-dev tcl tcl-dev tk tk-dev
RUN apt-get install -y git
RUN git clone https://github.com/SuperElastix/SimpleElastix
RUN mkdir /build
RUN cd /build
RUN cd /build;cmake -D PYTHON_EXECUTABLE=`which python3` ../SimpleElastix/SuperBuild
RUN cd /build;make -j `nproc`
RUN cd /build/SimpleITK-build/Wrapping/Python/Packaging;python3 setup.py install
RUN apt-get install -y python3-pip
RUN pip3 install tornado==4.5.3 numpy
#
# Install Neuroglancer dev environment
#
RUN apt-get install -y wget
RUN wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
RUN git clone https://github.com/google/neuroglancer
WORKDIR /neuroglancer
RUN export NVM_DIR="$HOME/.nvm";[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"; nvm install 10.6.0 ; npm i
#
# Install Nuggt and dependencies
#
ADD . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN pip3 install --editable .
