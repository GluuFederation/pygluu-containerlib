import logging
import os
import sys
import tarfile
from tempfile import TemporaryFile

from kubernetes import (
    client,
    config,
)
from kubernetes.stream import stream

from .base_meta import BaseMeta  # noqa: F401

logger = logging.getLogger(__name__)


class KubernetesMeta(BaseMeta):
    def __init__(self):
        config_loaded = False

        try:
            config.load_incluster_config()
            config_loaded = True
        except config.config_exception.ConfigException:
            logger.warn("Unable to load in-cluster configuration; trying to load from Kube config file")
            try:
                config.load_kube_config()
                config_loaded = True
            except (IOError, config.config_exception.ConfigException) as exc:
                logger.warn("Unable to load Kube config; reason={}".format(exc))

        if not config_loaded:
            logger.error("Unable to load in-cluster or Kube config")
            sys.exit(1)

        cli = client.CoreV1Api()
        cli.api_client.configuration.assert_hostname = False
        self.client = cli

    def get_containers(self, label):
        return self.client.list_pod_for_all_namespaces(label_selector=label).items

    def get_container_ip(self, container):
        return container.status.pod_ip

    def get_container_name(self, container):
        return container.metadata.name

    def copy_to_container(self, container, path):
        # make sure parent directory is created first
        self.exec_cmd(
            container,
            ["mkdir -p {}".format(os.path.dirname(path))],
        )

        # copy file implementation
        resp = stream(
            self.client.connect_get_namespaced_pod_exec,
            container.metadata.name,
            container.metadata.namespace,
            command=["tar", "xvf", "-", "-C", "/"],
            stderr=True,
            stdin=True,
            stdout=True,
            tty=False,
            _preload_content=False,
        )

        with TemporaryFile() as tar_buffer:
            with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
                tar.add(path)

            tar_buffer.seek(0)
            commands = []
            commands.append(tar_buffer.read())

            while resp.is_open():
                resp.update(timeout=1)
                if resp.peek_stdout():
                    # logger.info("STDOUT: %s" % resp.read_stdout())
                    pass
                if resp.peek_stderr():
                    # logger.info("STDERR: %s" % resp.read_stderr())
                    pass
                if commands:
                    c = commands.pop(0)
                    try:
                        resp.write_stdin(c.decode())
                    except UnicodeDecodeError:
                        # likely bytes from a binary
                        resp.write_stdin(c.decode("ISO-8859-1"))
                else:
                    break
            resp.close()

    def exec_cmd(self, container, cmd):
        return stream(
            self.client.connect_get_namespaced_pod_exec,
            container.metadata.name,
            container.metadata.namespace,
            command=[cmd],
            stderr=True,
            stdin=True,
            stdout=True,
            tty=False,
        )
