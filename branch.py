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

from addon_utils import check, enable

addon = "add_curve_sapling"
is_enabled, is_loaded = check(addon)
if not is_enabled:
    enable(addon)


class BranchGenerator(MetaDatasetGenerator):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.hdri_manager = bpycv.HdriManager(
            hdri_dir=os.path.join(cfg.SOURCE_ASSET, "shared/hdri/all"),
            category="nature",
        )

    def generate_one(self, dirr, index, meta_seed=0):
        bpycv.clear_all()
        cfg = self.cfg
        seed = f"{cfg.DIR},{meta_seed},{index}"
        random.seed(seed)
        bpy.context.scene.frame_set(0)
        bpycv.remove_useless_data()

        hdri_path = self.hdri_manager.sample()
        bpycv.load_hdri_world(hdri_path)

        cam_radius = random.choice([6, 7, 8,])
        cam_deg = random.uniform(0, 45)
        cam = bpycv.set_cam_pose(cam_radius=cam_radius, cam_deg=cam_deg)
        TREE_HEIGHT = 5
        cam.location.z += TREE_HEIGHT / 3
        for i in range(len(cam.rotation_euler)):
            cam.rotation_euler[i] += random.uniform(-pi / 18 / 2, pi / 18 / 2)

        instn = random.choice(cfg.OBJ_NUM_DIST)

        for idx in range(instn):
            bpy.ops.curve.tree_add(
                do_update=True,
                chooseSet="1",
                bevel=True,
                prune=False,
                showLeaves=False,
                useArm=False,
                seed=meta_seed * 10086 + idx,
                handleType="0",
                levels=2,
                length=(0.8, 0.6, 0.5, 0.1),
                lengthV=(0, 0.1, 0, 0),
                taperCrown=0.5,
                branches=(0, 0, 10, 1),
                curveRes=(8, 5, 3, 1),
                curve=(0, -15, 0, 0),
                curveV=(20, 50, 75, 0),
                curveBack=(0, 0, 0, 0),
                baseSplits=2,
                segSplits=(0.2, 0, 0.2, 0),
                splitByLen=True,
                rMode="rotate",
                splitAngle=(44.79, 15.24, 22, 0),
                splitAngleV=(-0.0999999, 5, 5, 0),
                scale=TREE_HEIGHT,
                scaleV=0.26,
                attractUp=(3.5, -1.89984, 0, 0),
                attractOut=(0, 0.8, 0, 0),
                shape="8",
                shapeS="10",
                customShape=(0.01, 0.01, 0.01, 0.01),
                branchDist=0.72,
                nrings=0,
                baseSize=0,
                baseSize_s=0,
                splitHeight=0,
                splitBias=0,
                ratio=0.01,
                minRadius=0.0015,
                closeTip=True,
                rootFlare=1.75,
                autoTaper=True,
                taper=(0, 0.0100001, 0, 0),
                radiusTweak=(1, 1, 1, 1),
                ratioPower=1.2,
                downAngle=(0, 26.21, 52.56, 30),
                downAngleV=(0, 10, 10, 10),
                useOldDownAngle=True,
                useParentAngle=True,
                rotate=(0, 0, 137.5, 137.5),
                rotateV=(15, 0, 0, 0),
                scale0=1,
                scaleV0=0.1,
                pruneWidth=0.34,
                pruneBase=0.12,
                pruneWidthPeak=0.5,
                prunePowerHigh=0.5,
                prunePowerLow=0.001,
                pruneRatio=0.75,
                leaves=150,
                leafDownAngle=30,
                leafDownAngleV=-10,
                leafRotate=137.5,
                leafRotateV=15,
                leafScale=0.4,
                leafScaleX=0.2,
                leafScaleT=0.1,
                leafScaleV=0.15,
                leafShape="hex",
                leafangle=-12,
                horzLeaves=True,
                leafDist="6",
                bevelRes=32,
                resU=20,
                armAnim=False,
                previewArm=False,
                leafAnim=False,
                frameRate=1,
                loopFrames=0,
                wind=1,
                gust=1,
                gustF=0.075,
                af1=1,
                af2=1,
                af3=4,
                makeMesh=False,
                armLevels=2,
                boneStep=(1, 1, 1, 1),
            )
        objs = [obj for obj in bpy.data.objects if obj.name.startswith("tree")]

        area_radius = TREE_HEIGHT * 0.6
        min_gap = TREE_HEIGHT * 0.05
        location_xyzs = list(
            np.mgrid[
                -area_radius:area_radius:min_gap, -area_radius:area_radius:min_gap, 0:1
            ].T.reshape(
                -1, 3,
            )
        )

        for inst_id, obj in enumerate(objs, 1000):
            obj["is_artifact"] = True
            obj["inst_id"] = inst_id
            location = location_xyzs.pop(random.choice(range(len(location_xyzs))))
            obj.location = location

            material_name = "auto.plastic_mat." + obj.name
            material = bpy.data.materials.new(material_name)
            material["is_auto"] = True
            material.use_nodes = True
            material.node_tree.nodes.clear()
            with bpycv.activate_node_tree(material.node_tree):
                bsdf = bpycv.Node("ShaderNodeBsdfPrincipled")
                bsdf.set_input(
                    {
                        "Base Color": (0.2, 0.1, 0, 1),
                        "Subsurface": 0.1,
                        "Subsurface Radius": (0.1, 0.1, 0.1),
                        "Subsurface Color": (0.75, 0.75, 0.75, 1),
                        "Metallic": 0.0,
                        "Specular": 0.0,
                        "Roughness": 1.0,
                        "Clearcoat": 0.0,
                        "Clearcoat Roughness": 1.0,
                    }
                )
                hsv = (
                    random.uniform(0.07, 0.133),
                    random.uniform(0.2, 1),
                    random.uniform(0.3, 0.95),
                )
                import skimage.color

                base_color = skimage.color.hsv2rgb(npa - [[hsv]]).squeeze()
                bsdf["Base Color"] = list(base_color) + [1]
                bsdf["Roughness"] = random.uniform(0, 1)
                bpycv.Node("ShaderNodeOutputMaterial").Surface = bsdf.BSDF

            obj.data.materials.clear()
            obj.data.materials.append(material)

        result = bpycv.render_data()

        def qualify_result(result):
            return True

        if qualify_result(result):
            result.save(dirr, index, save_blend=False)
        else:
            self.generate_one(dirr, index, meta_seed=meta_seed + 1)


def get_cfg():
    cfg = get_default_cfg()
    cfg.OBJ_NUM_DIST = [10]
    return cfg.clone()


if __name__ == "__main__":
    args = get_arguments()
    cfg = get_cfg()
    cfg.merge_from_list_or_str(args.opts)
    branch_gen = BranchGenerator(cfg)
    branch_gen.generate_all()
