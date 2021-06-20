# Source code of building iShape synthetic data by Blender

## Require
Ubuntu (tested on 18.04)  
Python >= 3.7  
Blender >= 2.90  

## Install

1. Download and install [Blender](https://www.blender.org/download/)
2. Install [`bpycv`](https://github.com/DIYer22/bpycv) for Blender's bundled Python
3. Prepare code and asset
```shell
mkdir ishape_dataset && cd ishape_dataset
# prepare code and source asset
git clone git@github.com:iShape/build_synthetic_ishape.git
git clone git@github.com:iShape/source_asset.git
```
4. Prepare background
    - `python build_synthetic_ishape/tool/download_background_hdri.py`
    - Which will download hdr file from [HDRI Haven](https://hdrihaven.com/) to `build_synthetic_ishape/source_asset/shared/hdri/all`

5. Synthesis dataset by Blender
    - `cd build_synthetic_ishape`
    - You can build some sub-datsets by:
        - `blender --background --python log.py --    DIR ../synthetic_ishape_dataset/log/train/ IMG_NUM 2000`
    - Or build whole iShape synthetic dataset by: `python build_synthetic_ishape.py`
```
