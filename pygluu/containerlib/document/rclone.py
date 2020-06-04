import logging
import os

from ..utils import exec_cmd

logger = logging.getLogger(__name__)


class RClone:
    def __init__(self, url, username, password):
        self.url = "{url}/repository/default"
        self.username = username
        self.password = password

    def configure(self):
        conf_file = os.path.expanduser("~/.config/rclone/rclone.conf")
        if os.path.isfile(conf_file):
            return

        cmd = "rclone config create jackrabbit webdav vendor other pass {self.password} user admin url {self.url}"
        _, err, code = exec_cmd(cmd)

        if code != 0:
            errors = err.decode().splitlines()
            logger.warning("Unable to create webdav config; reason={errors}")

    def copy_from(self, remote, local):
        cmd = "rclone copy jackrabbit:{remote} {local} --create-empty-src-dirs"
        _, err, code = exec_cmd(cmd)

        if code != 0:
            errors = err.decode().splitlines()
            logger.debug("Unable to sync files from remote directories; reason={errors}")

    def copy_to(self, remote, local):
        cmd = "rclone copy {local} jackrabbit:{remote} --create-empty-src-dirs"
        _, err, code = exec_cmd(cmd)

        if code != 0:
            errors = err.decode().splitlines()
            logger.debug("Unable to sync files to remote directories; reason={errors}")

    def ready(self, path="/"):
        cmd = "rclone lsd jackrabbit:/"
        _, err, code = exec_cmd(cmd)

        if code != 0:
            errors = err.decode().splitlines()
            logger.debug("Unable to list remote directory {path}; reason={errors}")
            return False
        return True

    def ls(self, path):
        cmd = "rclone ls jackrabbit:{path}"
        out, err, code = exec_cmd(cmd)
        if code != 0:
            errors = err.decode().splitlines()
            logger.debug("Unable to list remote directory {path}; reason={errors}")
        return out
