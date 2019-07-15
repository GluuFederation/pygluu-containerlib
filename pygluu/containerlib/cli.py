# -*- coding: utf-8 -*-
import argparse
import logging
from collections import OrderedDict

from .manager import get_manager
from .wait import wait_for


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    fmt = logging.Formatter("%(levelname)s - %(name)s - %(asctime)s - %(message)s")
    ch.setFormatter(fmt)
    logger.addHandler(ch)


def wait_for_cli():
    setup_logger()

    parser = argparse.ArgumentParser()
    required_group = parser.add_argument_group("required arguments")
    required_group.add_argument(
        "--deps",
        help="comma-separated dependencies to wait for",
        required=True,
    )
    args = parser.parse_args()

    deps = filter(
        None,
        [dep.strip() for dep in args.deps.split(",") if dep]
    )
    deps = list(OrderedDict.fromkeys(deps))

    kwargs = {}
    manager = get_manager()
    wait_for(manager, deps, **kwargs)
