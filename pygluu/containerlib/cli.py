# -*- coding: utf-8 -*-
import argparse
import logging
import urllib3
from collections import OrderedDict

from .manager import get_manager
from .wait import wait_for


def setup_logger():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    fmt = logging.Formatter("%(levelname)s - %(name)s - %(asctime)s - %(message)s")
    ch.setFormatter(fmt)
    logger.addHandler(ch)


def wait_for_cli():
    setup_logger()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conn-only",
        help="dependencies to check for their connection only",
        default="",
    )
    required_group = parser.add_argument_group("required arguments")
    required_group.add_argument(
        "--deps",
        help="dependencies to wait for",
        required=True,
    )
    args = parser.parse_args()

    deps = filter(
        None,
        [dep.strip() for dep in args.deps.split(",") if dep]
    )
    deps = list(OrderedDict.fromkeys(deps))

    conn_only = filter(
        None,
        [conn.strip() for conn in args.conn_only.split(",") if conn]
    )
    conn_only = list(OrderedDict.fromkeys(conn_only))

    manager = get_manager()
    wait_for(manager, deps, conn_only)
