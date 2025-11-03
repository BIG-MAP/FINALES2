FROM ubuntu:22.04

# --- Installing relevant tools
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git vim pip

RUN apt-get remove python
RUN apt-get -y install python[3.9.12]

WORKDIR /root/

RUN mkdir -p code
# finales_data finales_internals && \
#     mkdir -p finales_server_administration/capability_specs && \
#     mkdir -p finales_server_administration/tenant_specs && \
#     mkdir -p finales_server_administration/backups

COPY . ./code/FINALES

RUN pip install ./code/FINALES

CMD ["bash"]