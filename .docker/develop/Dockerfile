FROM ubuntu:22.04

WORKDIR /usr/FINALES

# --- Installing relevant tools
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git vim pip

RUN apt-get remove python
RUN apt-get -y install python[3.9.12]

# VOLUME finales_code

# COPY .. finales_code/FINALES

# RUN git clone https://github.com/BIG-MAP/FINALES2.git /finales_code/FINALES2
# RUN pip install -e finales_code/FINALES