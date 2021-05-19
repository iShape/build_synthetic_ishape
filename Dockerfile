FROM diyer22/bpycv

RUN pip install zcs
WORKDIR /tmp/build_synthetic_ishape
# docker build . -t ishape; docker run -it -v $(dirname `pwd`):/tmp -v /home/dl:/home/dl ishape blender -b -P branch.py -- DIR /tmp/dataset_tmp IMG_NUM 200 RESOLUTION 256,256
