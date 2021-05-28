#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Feb 22 22:14:51 2020
"""
# TODO
# - [x] support RLE encode
# - [ ] support panoptic segmentation


import boxx
from boxx import *
from boxx import pathjoin, listdir, filename, imread, basename
from boxx import np, os

import cv2
import argparse
import pycocotools.mask


def mask2poly(
    mask,
    category_id=0,
    img_name=None,
    save_segmentation=True,
    shrank_stride=1,
    mask_encoding="rle",
    approx_poly_epsilon=1,
):

    ground_truth_binary_mask = np.uint8(mask)
    fortran_ground_truth_binary_mask = np.asfortranarray(ground_truth_binary_mask)
    encoded_ground_truth = pycocotools.mask.encode(fortran_ground_truth_binary_mask)
    ground_truth_area = pycocotools.mask.area(encoded_ground_truth)
    ground_truth_bounding_box = pycocotools.mask.toBbox(encoded_ground_truth)

    annotation = {
        "segmentation": [[1, 1, 1, 2, 2, 2]],
        "area": ground_truth_area.tolist(),
        "iscrowd": 0,
        "image_id": 0,
        "bbox": ground_truth_bounding_box.tolist(),
        "category_id": int(category_id),
        "id": 1,
        "img_name": img_name,
    }
    if save_segmentation:
        assert mask_encoding in ["rle", "poly"]
        if mask_encoding == "rle":
            encoded_ground_truth["counts"] = encoded_ground_truth["counts"].decode(
                "ascii"
            )
            annotation["segmentation"] = encoded_ground_truth
        else:
            contours, hierarchy = cv2.findContours(
                (ground_truth_binary_mask).astype(np.uint8),
                cv2.RETR_TREE,
                cv2.CHAIN_APPROX_SIMPLE,
            )[-2:]
            contours = [
                cv2.approxPolyDP(cnt, approx_poly_epsilon, True) for cnt in contours
            ]
            annotation["segmentation"] = []
            for contour in contours:
                contour = np.flip(contour, axis=1).round().astype(int)
                segmentation = contour.ravel().tolist()
                if shrank_stride > 1 and len(segmentation) > shrank_stride * 2 * 10:
                    segmentation = (
                        np.array(segmentation)
                        .reshape(-1, 2)[::shrank_stride]
                        .round()
                        .astype(int)
                        .ravel()
                        .tolist()
                    )
                # fix TypeError: Argument 'bb' has incorrect type (expected numpy.ndarray, got list)
                while len(segmentation) <= 4:
                    segmentation += segmentation[-2:]
                annotation["segmentation"].append(segmentation)

    return annotation


class InstMapDataProvider:
    def __init__(self, dirr, phase=None):
        self.dirr = dirr
        self.imgdir = pathjoin(self.dirr, "image")
        self.instdir = pathjoin(self.dirr, "instance_map")

        img_bnames = listdir(self.imgdir)
        inst_bnames = listdir(self.instdir)

        self.fnames = sorted(set(map(filename, img_bnames)))
        self.idx2fname = dict(enumerate(self.fnames))

        fname2img_bname = {filename(p): p for p in img_bnames}
        fname2inst_bname = {filename(p): p for p in inst_bnames}

        self.idx2img_bname = {
            idx: fname2img_bname[fname] for idx, fname in self.idx2fname.items()
        }
        self.idx2inst_bname = {
            idx: fname2inst_bname[fname] for idx, fname in self.idx2fname.items()
        }

    def __len__(self):
        return len(self.fnames)

    def __getitem__(self, idx):
        fname = self.idx2fname[idx]
        imgp = pathjoin(self.imgdir, self.idx2img_bname[idx])
        instp = pathjoin(self.instdir, self.idx2inst_bname[idx])
        d = dict(
            index=idx, fname=fname, img=imread(imgp), inst=imread(instp), imgp=imgp
        )
        return d


if __name__ == "__main__":
    dirr = "/home/dl/dataset/blender_syn_hanger"

    parser = argparse.ArgumentParser(
        """
    python -m boxx.script 'p/mapmt(lambda i:os.system(f"rlaunch --cpu=10 --memory=30000 -- python ../build_synthetic_ishape/tool/instance_map_to_coco.py --dirr {i} --mask_encoding poly ") , glob("*/*"), pool=16)'
    """
    )
    parser.add_argument("--dirr", default=dirr)
    parser.add_argument("--mask_encoding", default="rle")
    args = parser.parse_args()
    dirr = args.dirr

    provider = InstMapDataProvider(dirr)

    coco_dic = {}
    category_ids = set()
    anns = coco_dic["annotations"] = []
    imgds = coco_dic["images"] = []
    ann_id = 1
    for idx in range(len(provider)):
        img_id = idx + 1
        d = provider[idx]
        inst = d["inst"]
        h, w = inst.shape
        imgd = dict(id=img_id, file_name=basename(d["imgp"]), height=h, width=w)
        imgds.append(imgd)
        for inst_id in np.unique(inst):
            if inst_id >= 1000:
                mask = inst == inst_id
                ann = mask2poly(mask, inst_id // 1000, mask_encoding=args.mask_encoding)
                ann["id"] = ann_id
                ann["image_id"] = img_id
                ann_id += 1
                anns.append(ann)

        if boxx.timegap(10, "to json"):
            print(f"{idx}/{len(provider)} = {idx/len(provider)}")
    coco_dic["categories"] = [
        {"id": cat, "name": "cat" + str(cat), "supercategory": "supercat" + str(cat),}
        for cat in sorted(set([d["category_id"] for d in anns]))
    ]
    js_name = f"coco_format-mask_encoding={args.mask_encoding}-instances_2017.json"
    coco_jsp = pathjoin(dirr, js_name)
    boxx.savejson(coco_dic, coco_jsp)

    coco_format_dir = pathjoin(dirr, "coco_format")
    boxx.makedirs(coco_format_dir)
    img_dir_ln = pathjoin(coco_format_dir, "train2017")
    if os.path.exists(img_dir_ln):
        os.remove(img_dir_ln)
    os.system(f"ln -sf ../image {img_dir_ln}")
    os.system(
        f"ln -sf ../{js_name} {pathjoin(coco_format_dir,'instances_train2017.json')}"
    )
