FROM diyer22/bpycv
WORKDIR /
RUN mkdir /tmp/synthetic_ishape_dataset && ln -s /tmp/synthetic_ishape_dataset /synthetic_ishape_dataset

RUN git clone https://github.com/iShape/source_asset
COPY . /build_synthetic_ishape
RUN python /build_synthetic_ishape/tool/download_background_hdri.py

RUN pip install zcs
WORKDIR /build_synthetic_ishape
# CMD blender --background --python branch.py -- DIR ../synthetic_ishape_dataset/branch/train/ IMG_NUM 2000
CMD python build_synthetic_ishape.py

# docker build . -t diyer22/ishape; docker run -it -v /tmp:/tmp diyer22/ishape blender -b -P branch.py -- DIR /tmp/dataset_tmp IMG_NUM 200 RESOLUTION 256,256
