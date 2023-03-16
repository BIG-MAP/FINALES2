FROM continuumio/miniconda3:4.12.0
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git vim
RUN conda install \
    xarray \
    netCDF4 \
    bottleneck \
    numpy \
    pandas \
    matplotlib \
    jupyterlab
RUN mkdir -p /root/.ssh
RUN echo 'Host github.com' > /root/.ssh/config
RUN echo '  HostName github.com' >> /root/.ssh/config
RUN echo '  IdentityFile ~/data/ssh_keys/github_key' >> /root/.ssh/config
# WORKDIR data
#RUN git clone git@github.com:BIG-MAP/FINALES2.git
CMD ["jupyter-lab","--ip=0.0.0.0","--no-browser","--allow-root"]