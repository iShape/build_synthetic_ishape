#!/usr/bin/env python3
import os
import sys
import argparse
from zcs import argument, ints
from zcs.config import CfgNode as CN


from bpycv.dataset_utils.cfg_utils import *

cfg.SOURCE_ASSET = os.path.abspath(os.path.join(__file__, "../../source_asset"))


if __name__ == "__main__":
    from boxx import tree

    args = get_arguments()
    cfg = get_default_cfg()
    cfg.merge_from_list_or_str(args.opts)
    tree - cfg
    pass
