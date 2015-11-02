from ftw.upgrade import UpgradeStep


class RemoveSkinsDirectory(UpgradeStep):
    """Remove skins directory.
    """

    def __call__(self):
        self.install_upgrade_profile()
