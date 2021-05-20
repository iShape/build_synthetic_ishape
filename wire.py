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


class WireGenerator(MetaDatasetGenerator):
    def __init__(self, cfg):
        bpy.ops.wm.open_mainfile(
            filepath=os.path.join(cfg.SOURCE_ASSET, "wire/wire.blend")
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

        sphere = bpy.data.objects["Sphere"]
        sphere.location = -1.2, 0, 0
        sphere2 = bpy.data.objects["Sphere2"]
        sphere2.location = 0.1, -1.7, 0

        cam_radius = random.uniform(1.8, 2)
        cam_deg = random.uniform(67, 90)
        bpycv.set_cam_pose(cam_radius=cam_radius, cam_deg=cam_deg)

        instn = random.choice(cfg.OBJ_NUM_DIST)
        wire = bpy.data.objects["wire"]
        wire["is_artifact"] = True
        for _ in range(instn - 1):
            with bpycv.activate_obj(wire):
                obj = bpycv.duplicate(wire, True)
                obj["is_duplicate"] = True

        wires = [obj for obj in bpy.data.objects if obj.get("is_artifact")]

        colors = np.array(boxx.getDefaultColorList(random.choice(range(7, 30)))) * 0.7

        color = random.choice([(0.5, 0.0, 0.0), (0.0, 0.5, 0.0), (0.0, 0.0, 0.5),])
        ENV_SIZE = 0.5
        for inst_id, obj in enumerate(wires, 1000):
            obj["inst_id"] = inst_id
            location = (
                random.uniform(-ENV_SIZE, ENV_SIZE),
                random.uniform(-ENV_SIZE, ENV_SIZE),
                random.uniform(0.5, 1),
            )
            rotation = (
                random.random() * 2 * pi,
                # random.random() * pi / 4 - pi / 8,
                random.random() * pi / 2 - pi / 4,
                random.random() * 2 * pi,
            )
            obj.location = location
            obj.rotation_euler = rotation

            material_name = "auto.plastic_mat." + obj.name
            material = bpy.data.materials.new(material_name)
            material["is_auto"] = True
            material.use_nodes = True
            material.node_tree.nodes.clear()
            with bpycv.activate_node_tree(material.node_tree):
                bsdf = bpycv.Node("ShaderNodeBsdfPrincipled")
                _color = random.choice(colors) if random.random() < 1 / 8 else color
                bsdf["Base Color"] = tuple(_color) + (1.0,)
                bsdf["Specular"] = 0.2
                bsdf["Roughness"] = 0.2
                bpycv.Node("ShaderNodeOutputMaterial").Surface = bsdf.BSDF
            obj.data.materials.clear()
            obj.data.materials.append(material)
        if "computing simulation":
            print("Start computing simulation, and will takes a while")
            for i in range(30):
                bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)

            for i in range(30):
                bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)
                bpy.ops.wm.redraw_timer(type="DRAW", iterations=1)
                bpy.context.view_layer.update()
                sphere.location.x += 1 / 30 * 1.5
                sphere2.location.y += 1 / 30 * 1.8
                bpy.context.view_layer.update()
                bpy.ops.wm.redraw_timer(type="DRAW", iterations=1)
            for i in range(10):
                bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)

        bpy.data.objects["Plane"].material_slots[0].material.node_tree.nodes[
            "Principled BSDF"
        ].inputs["Base Color"].default_value = tuple(random.choice(colors)) + (1.0,)
        sphere.location = -1, 0, -10
        sphere2.location = -1, 0, -10
        result = bpycv.render_data()

        def qualify_result(result):
            return True

        if qualify_result(result):
            result.save(dirr, index, save_blend=True)
        else:
            self.generate_one(dirr, index, meta_seed=meta_seed + 1)


def get_cfg():
    cfg = get_default_cfg()
    cfg.OBJ_NUM_DIST = [
        5,
        6,
        7,
    ]
    return cfg.clone()


if __name__ == "__main__":
    args = get_arguments()
    cfg = get_cfg()
    cfg.merge_from_list_or_str(args.opts)
    wire_gen = WireGenerator(cfg)
    wire_gen.generate_all()
