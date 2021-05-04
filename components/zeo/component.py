from batou.component import Attribute
from batou.component import Component
from batou.lib.buildout import Buildout
from batou.lib.cron import CronJob
from batou.lib.file import Directory
from batou.lib.file import File
from batou.lib.git import Clone
from batou.lib.supervisor import Program
from batou.utils import Address


class Zeo(Component):
    address = Attribute(Address, "{{host.fqdn}}:9000")
    profile = "base"
    branch = "master"
    manage_buildout_clone = Attribute("literal", True)

    def configure(self):
        self.provide("zeo:server", self.address)

        self += Clone(
            "https://github.com/syslabcom/recensio.buildout.git",
            branch=self.branch,
            vcs_update=self.manage_buildout_clone,
        )
        self += Directory("downloads")
        self += Buildout(
            python="2.7", setuptools="42.0.2", version="2.13.3", additional_config=[]
        )
        if self.profile == "dev":
            config_file = "parts/zeo/etc/zeo.conf"
        else:
            config_file = "parts/zeo/zeo.conf"
        self += Program(
            "zeo",
            options=dict(startsecs=30),
            command=self.map("bin/runzeo"),
            args=self.expand("-C {{component.workdir}}/" + config_file),
        )

        self += File('bin/pack', source='pack', mode=0750)
        self += CronJob(self.map('bin/pack'),
                        timing='@weekly', logger='zeopack')
