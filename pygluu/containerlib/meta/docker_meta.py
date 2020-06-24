import contextlib
import os
import tarfile

import docker

from .base_meta import BaseMeta  # noqa: F401


class DockerMeta(BaseMeta):
    def __init__(self, base_url="unix://var/run/docker.sock"):
        self.client = docker.DockerClient(base_url=base_url)

    def get_containers(self, label):
        return self.client.containers.list(filters={'label': label})

    def get_container_ip(self, container):
        for _, network in container.attrs["NetworkSettings"]["Networks"].items():
            return network["IPAddress"]

    def get_container_name(self, container):
        return container.name

    def copy_to_container(self, container, path):
        src = os.path.basename(path)
        dirname = os.path.dirname(path)

        os.chdir(dirname)

        with tarfile.open(src + ".tar", "w:gz") as tar:
            tar.add(src)

        with open(src + ".tar", "rb") as f:
            payload = f.read()

            # create directory first
            self.exec_cmd(container, "mkdir -p {}".format(dirname))

            # copy file
            container.put_archive(os.path.dirname(path), payload)

        with contextlib.suppress(FileNotFoundError):
            os.unlink(src + ".tar")

    def exec_cmd(self, container, cmd):
        return container.exec_run(cmd)
