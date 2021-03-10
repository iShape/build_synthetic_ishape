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
from dataset_gen_utils import MetaDatasetGenerator, uniform_by_mean
from cfg_utils import get_arguments, get_defaults_cfg


class HangerGenerator(MetaDatasetGenerator):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.hdri_manager = bpycv.HdriManager(
            hdri_dir=os.path.join(cfg.SOURCE_ASSET, "shared/hdri/all")
        )

    def generate_one(self, dirr, index, meta_seed=0):
        cfg = self.cfg
        random.seed(f"{cfg.DIR},{meta_seed},{index}")
        bpy.context.scene.frame_set(0)
        bpycv.remove_useless_data()
        bpycv.clear_all()

        hdri_path = self.hdri_manager.sample()
        bpycv.load_hdri_world(hdri_path)

        cam_radius = random.choice([5, 8, 10, 15, 20])
        cam_deg = random.uniform(0, 90)
        bpycv.set_cam_pose(cam_radius=cam_radius, cam_deg=cam_deg)

        if "Plane" not in bpy.data.objects:
            bpy.ops.mesh.primitive_plane_add(size=100)
            obj = bpy.data.objects["Plane"]
            with bpycv.activate_obj(obj):
                bpy.ops.rigidbody.object_add()
                bpy.context.object.rigid_body.type = "PASSIVE"
                obj.hide_render = True

        obj_num = random.choice(cfg.OBJ_NUM_DIST)
        for inst_id, idx in enumerate(range(obj_num), cfg.MAX_INST):
            inst_id
            bpy.ops.mesh.primitive_cylinder_add(
                radius=uniform_by_mean(mean=0.25, rate=0.4),
                depth=uniform_by_mean(12, 0.01),
            )
            obj = bpy.context.active_object
            obj["is_artifact"] = True
            bpy.ops.object.shade_smooth()
            obj["inst_id"] = inst_id
            area_scale = 4
            location = (
                random.uniform(-1, 1) * area_scale,
                0,
                random.uniform(0, 1) * area_scale,
            )
            obj.location = location
            obj.rotation_euler.x = boxx.pi / 2
            with bpycv.activate_obj(obj):
                bpy.ops.rigidbody.object_add()
                obj.rigid_body.type = "ACTIVE"

            texture_path = random.choice(self.texture_paths)
            material = bpycv.build_tex(texture_path)
            obj.data.materials.clear()
            obj.data.materials.append(material)

        for i in range(120):
            bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)

        result = bpycv.render_data()

        def qualify_result(result):
            return len(np.unique(result["inst"])) > 5

        if qualify_result(result):
            result.save(dirr, index, save_blend=True)
        else:
            self.generate_one(dirr, index, meta_seed=meta_seed + 1)


def get_cfg():
    cfg = get_defaults_cfg()
    cfg.OBJ_NUM_DIST = [70, 80, 90]
    return cfg.clone()


if __name__ == "__main__":
    args = get_arguments()
    cfg = get_cfg()
    cfg.merge_from_list_or_str(args.opts)
    hanger_gen = HangerGenerator(cfg)
    hanger_gen.generate_all()
