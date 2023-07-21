FROM continuumio/miniconda3:4.12.0

# --- Installing relevant tools
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git vim screen

RUN conda install \
    xarray \
    netCDF4 \
    bottleneck \
    numpy \
    nodejs \
    pandas \
    matplotlib \
    jupyterlab

# --- Installing FINALES
COPY . /root/app
WORKDIR /root/app
RUN pip install -e .
WORKDIR /root

# --- For when developing in the container
RUN mkdir -p /root/.ssh
RUN echo 'Host github.com' > /root/.ssh/config
RUN echo '  HostName github.com' >> /root/.ssh/config
RUN echo '  IdentityFile ~/data/ssh_keys/github_key' >> /root/.ssh/config

# ---
CMD ["jupyter-lab","--ip=0.0.0.0","--no-browser","--allow-root"]
