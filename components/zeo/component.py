from batou.component import Attribute
from batou.component import Component
from batou.lib.buildout import Buildout
from batou.lib.file import Directory
from batou.lib.git import Clone
from batou.lib.supervisor import Program
from batou.utils import Address
import batou_ext.nix


class Zeo(Component):
    address = Attribute(Address, "{{host.fqdn}}:9000")
    profile = "base"
    branch = "master"
    manage_buildout_clone = Attribute("literal", True)

    def configure(self):
        self.provide("zeo:server", self.address)

        self += batou_ext.nix.UserEnv(
            "zope",
            packages=[
                "abiword",
                "aespipe",
                "cron",
                "cyrus_sasl",
                "enchant",
                "gcc",
                "gettext",
                "ghostscript",
                "gnumake",
                "graphicsmagick",
                "html-tidy",
                "libedit",
                "libffi",
                "libjpeg",
                "libxslt",
                "libyaml",
                "pdf2svg",
                "pdftk",
                "perl",
                "perlPackages.LWPProtocolHttps",
                "perlPackages.LWPUserAgent",
                "perlPackages.MonitoringPlugin",
                "poppler_utils",
                "tmpwatch",
                "wkhtmltopdf",
                "wv",
                "yarn",
                "zlib",
            ],
            channel="https://releases.nixos.org/nixos/19.03/nixos-19.03.173575.0e0ee084d6d/nixexprs.tar.xz",
        )

        self += Clone(
            "https://github.com/syslabcom/recensio.buildout.git",
            branch=self.branch,
            vcs_update=self.manage_buildout_clone,
        )
        self += Directory("downloads")
        self += Buildout(
            python="2.7", setuptools="38.5.1", version="2.11.4", additional_config=[]
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
