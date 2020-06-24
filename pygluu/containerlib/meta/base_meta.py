class BaseMeta:
    def get_containers(self, label):
        """Get list of containers based on label.

        Subclass __MUST__ implement this method.
        """

    def get_container_ip(self, container):
        """Get container's IP address.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def get_container_name(self, container):
        """Get container's name.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def copy_to_container(self, container, path):
        """Copy path to container.

        Subclass __MUST__ implement this method.
        """
        raise NotImplementedError

    def exec_cmd(self, container, cmd):
        raise NotImplementedError
