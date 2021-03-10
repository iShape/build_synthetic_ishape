# Source code of building iShape synthetic data by Blender




```shell
mkdir ishape_dataset && cd ishape_dataset

# prepare code and source asset
git clone git@github.com:iShape/build_synthetic_ishape.git
git clone git@github.com:iShape/source_asset.git

# build dataset
python build_synthetic_ishape.py
# blender --background --python log.py --    DIR ../synthetic_ishape_dataset/log/train/ IMG_NUM 2000
```
