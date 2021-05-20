#!/usr/bin/env python3

import boxx
from boxx import *
from boxx import np

import os
import sys

sys.path.append(".")

import bpy
import bpycv
import random
from bpycv.dataset_utils.dataset_generator import MetaDatasetGenerator
from cfg_utils import get_arguments, get_default_cfg


class FenceGenerator(MetaDatasetGenerator):
    def __init__(self, cfg):
        bpy.ops.wm.open_mainfile(
            filepath=os.path.join(cfg.SOURCE_ASSET, "fence/fence.blend")
        )
        super().__init__(cfg)
        self.hdri_manager = bpycv.HdriManager(
            hdri_dir=os.path.join(cfg.SOURCE_ASSET, "shared/hdri/all"),
            category="indoor",
        )

    def generate_one(self, dirr, index, meta_seed=0):
        [bpycv.remove_obj(obj) for obj in bpy.data.objects if obj.get("is_duplicate")]
        cfg = self.cfg
        random.seed(f"{cfg.DIR},{meta_seed},{index}")
        bpy.context.scene.frame_set(0)
        bpycv.remove_useless_data()

        hdri_path = self.hdri_manager.sample()
        bpycv.load_hdri_world(hdri_path)

        cam_radius = random.uniform(1.5, 1.8)
        cam_deg = random.uniform(60, 90)
        bpycv.set_cam_pose(cam_radius=cam_radius, cam_deg=cam_deg)

        instn = random.choice(cfg.OBJ_NUM_DIST)
        fence = bpy.data.objects["fence"]
        fence["is_artifact"] = True
        for _ in range(instn - 1):
            with bpycv.activate_obj(fence):
                obj = bpycv.duplicate(fence, True)
                obj["is_duplicate"] = True

        objs = [obj for obj in bpy.data.objects if obj.get("is_artifact")]

        for idx, obj in enumerate(objs):
            obj["inst_id"] = idx + 1000
            ENV_SIZE = 1.2
            location = (
                random.uniform(-ENV_SIZE, ENV_SIZE),
                random.uniform(-ENV_SIZE, ENV_SIZE),
                0.04 + 0.1 * idx,
            )
            rotation = (
                0,
                0,
                random.random() * 2 * 3.1415,
            )
            obj.location = location
            obj.rotation_euler = rotation
        for i in range(120):
            bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)
        result = bpycv.render_data()

        def qualify_result(result):
            return True

        if qualify_result(result):
            result.save(dirr, index, save_blend=False)
        else:
            self.generate_one(dirr, index, meta_seed=meta_seed + 1)


def get_cfg():
    cfg = get_default_cfg()
    cfg.OBJ_NUM_DIST = [2, 2, 3, 3, 3, 4]
    return cfg.clone()


if __name__ == "__main__":
    args = get_arguments()
    cfg = get_cfg()
    cfg.merge_from_list_or_str(args.opts)
    fence_gen = FenceGenerator(cfg)
    fence_gen.generate_all()
