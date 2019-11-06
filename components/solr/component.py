from batou.component import Component, Attribute
from batou.lib.buildout import Buildout
from batou.lib.file import Directory
from batou.lib.supervisor import Program
from batou.utils import Address
import batou_ext.nix


class Solr4(Component):

    address = Attribute(Address, '{{host.fqdn}}:8984')
    test_address = Attribute(Address, '{{host.fqdn}}:9984')

    profile = 'base'

    def configure(self):
        self.solr_version = '4.9.1'
        self.major_version = self.solr_version[0]
        self.solr_src = (
            'http://archive.apache.org/dist/lucene/solr/'
            '{0}/solr-{0}.zip'.format(
                self.solr_version
            )
        )
        self.md5sum = '2b8db289ce238c665363017f62e54708'

        self += Buildout(
            python='2.7',
            setuptools='38.5.1',
            version='2.11.4',
            additional_config=[Directory('profiles', source='profiles')])


class Solr5(Component):

    address = Attribute(Address, '{{host.fqdn}}:8985')
    test_address = Attribute(Address, '{{host.fqdn}}:9985')

    profile = 'solr5'

    def configure(self):
        self.provide('solr:server', self)
        self.solr_version = '5.5.5'
        self.major_version = self.solr_version[0]
        self.solr_src = (
            'http://archive.apache.org/dist/lucene/solr/'
            '{0}/solr-{0}.zip'.format(
                self.solr_version
            )
        )
        self.md5sum = 'b15105d42936f33de3e5d241c6e6cf71'

        self += batou_ext.nix.UserEnv(
            "solr",
            packages=[
                "jre8",
            ],
            channel="https://releases.nixos.org/nixos/19.03/nixos-19.03.173575.0e0ee084d6d/nixexprs.tar.xz"
        )
        self += Buildout(
            python='2.7',
            setuptools='38.5.1',
            version='2.11.4',
            additional_config=[
                Directory('profiles', source='profiles'),
                Directory('templates', source='templates'),
            ],
        )

        self += Program('solr',
                        command='/usr/bin/env java',
                        args=self.expand('-Xms512m -Xmx2048m -jar start.jar --module=http jetty.host={{component.address.connect.host}} jetty.port={{component.address.connect.port}}'),
                        directory=self.map('parts/instance'))
