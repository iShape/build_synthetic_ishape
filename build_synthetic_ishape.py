#!/usr/bin/env python3

import os
import sys
import time
import boxx

all_synthetic_dataset_names = ["branch", "fence", "hanger", "log", "wire"]


def build_one_dataset(name):
    boxx.pred(f"Build dataset: {name}")
    cmd = f"blender --background --python {name}.py --\
    DIR ../synthetic_ishape_dataset/{name}/train/ IMG_NUM {2000}"
    print(cmd)
    os.system(cmd)
    time.sleep(1)

    cmd = f"blender --background --python {name}.py --\
    DIR ../synthetic_ishape_dataset/{name}/val/ IMG_NUM {500}"
    print(cmd)
    os.system(cmd)


if __name__ == "__main__":
    synthetic_dataset_names = all_synthetic_dataset_names.copy()
    if len(sys.argv) > 1:
        synthetic_dataset_names = sys.argv[1:]
    for name in synthetic_dataset_names:
        if name.isdigit():
            name = all_synthetic_dataset_names[int(name)]
        assert (
            name in all_synthetic_dataset_names
        ), f'"{name}" not in {all_synthetic_dataset_names}'
        build_one_dataset(name)

    # If build on brainpp
    # python -m boxx.script  'p/mapmt(lambda i:os.system(f"rlaunch -P 50 --preemptible=best-effort --cpu=2 --memory=20000 -- python build_synthetic_ishape.py {i} ") ,range(5), pool=6)'
