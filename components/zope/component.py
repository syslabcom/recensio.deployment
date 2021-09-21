from batou import UpdateNeeded
from batou.component import Attribute
from batou.component import Component
from batou.lib.cron import CronJob
from batou.lib.file import Directory
from batou.lib.git import Clone
from batou.lib.buildout import Buildout
from batou.lib.logrotate import RotatedLogfile
from batou.lib.supervisor import Eventlistener
from batou.lib.supervisor import Program
from batou.utils import Address
import os.path


class DevelopAwareBuildout(Buildout):

    def verify(self):
        super(DevelopAwareBuildout, self).verify()
        if os.path.exists('bin/develop'):
            raise UpdateNeeded


class Zope(Component):
    """Deploys the zope instance with all dependencies.
    """
    instance_address = Attribute(Address, '{{host.fqdn}}:8080')
    instance1_address = Attribute(Address, '{{host.fqdn}}:8081')
    instance2_address = Attribute(Address, '{{host.fqdn}}:8082')
    instance3_address = Attribute(Address, '{{host.fqdn}}:8083')
    instance4_address = Attribute(Address, '{{host.fqdn}}:8084')
    instancebots_address = Attribute(Address, '{{host.fqdn}}:8089')
    worker_address = Attribute(Address, '{{host.fqdn}}:8099')
    solr_address = Attribute(Address, '{{host.fqdn}}:8983')
    profile = 'base'
    branch = 'master'
    adminpw = None
    portals = Attribute('literal', [])
    sentry_dsn = Attribute(str, '')
    manage_buildout_clone = Attribute('literal', True)
    eggserver = ''

    features = ('instance', 'worker', 'instancebots', )
    numbered_instances = Attribute(int, 0)
    run_exports_on = None
    run_imports_on = None

    def configure(self):
        # self.provide('zope:http', self.instance_address)
        self.zeo = self.require_one('zeo:server')
        self.solr = self.require_one('solr:server')

        self.extra_parts = []
        if 'instance' in self.features:
            for num in range(1, self.numbered_instances + 1):
                self.extra_parts.append('instance{0}'.format(num))
        if 'instancebots' in self.features:
            self.extra_parts.append('instancebots')
        if 'worker' in self.features:
            self.extra_parts.append('worker')
        if 'solr' in self.features:
            self.extra_parts.extend(['solr-download', 'solr-instance'])

        self += Directory('downloads')
        buildout = DevelopAwareBuildout(python='2.7',
                                        setuptools='42.0.2',
                                        version='2.13.3',
                                        additional_config=[])
        self += buildout
        buildout += Clone('https://github.com/syslabcom/recensio.buildout.git',
                          branch=self.branch,
                          vcs_update=self.manage_buildout_clone)

        if 'instance' in self.features:
            for num in range(1, self.numbered_instances + 1):
                instance_id = 'instance{0}'.format(num)
                self += Program(
                    instance_id,
                    options=dict(startsecs=20, stopsignal='INT', stopwaitsecs=5),
                    command=self.map('bin/{0} console'.format(instance_id)))

                self += Eventlistener(
                    'memmon{0}'.format(num),
                    command='bin/memmon',
                    args='-p instance{0}=2GB -m admin@syslab.com'.format(num))

            postrotate = self.expand(
                "for i in {{component.workdir}}/var/*.pid; do kill -USR2 `cat $i`; done"
            )
            self += RotatedLogfile("var/log/*.log", postrotate=postrotate)

        if 'instancebots' in self.features:
            self += Program(
                'instancebots',
                options=dict(startsecs=20, stopsignal='INT', stopwaitsecs=5),
                command=self.map('bin/instancebots console'))

            self += Eventlistener(
                'memmonbots',
                command='bin/memmon',
                args='-p instancebots=2GB')

        if 'worker' in self.features:
            self += Program(
                'worker',
                options=dict(startsecs=20, stopsignal='INT', stopwaitsecs=5),
                command=self.map('bin/worker console'))

            self += Eventlistener(
                'memmonworker',
                command='bin/memmon',
                args='-p worker=2GB -m admin@syslab.com')

        if 'solr' in self.features:
            self += Program('solr3',
                            command='/usr/bin/env java',
                            args='-Xms512m -Xmx2048m -jar start.jar',
                            directory=self.map('parts/solr-instance'))

        if self.host.name == self.run_exports_on:
            self += CronJob(
                self.map("bin/metadata-export"),
                timing="20 22 * * sun",
                logger="recensio")
            self += CronJob(
                self.map("bin/metadata-export-regio"),
                timing="00 23 * * sun",
                logger="recensio")
            self += CronJob(
                self.map("bin/metadata-export-altertum"),
                timing="30 23 * * sun",
                logger="recensio")
            self += CronJob(
                self.map("bin/metadata-export-artium"),
                timing="55 23 * * sun",
                logger="recensio")
            self += CronJob(
                self.map("bin/chronicon-export"),
                timing="27 2 1 * *",
                logger="recensio")
            self += CronJob(
                self.map("bin/chronicon-export-regio"),
                timing="57 2 1 * *",
                logger="recensio")
            self += CronJob(
                self.map("bin/chronicon-export-altertum"),
                timing="27 3 1 * *",
                logger="recensio")
            # chronicon artium skipped on purpose
            self += CronJob(
                self.map("bin/newsletter"),
                timing="0 12 20 * *",
                logger="recensio")
            self += CronJob(
                "wget --output-file=/dev/null --output-document=/dev/null http://www.recensio.net/RSS-feeds/mail_uncommented_presentations",
                timing="0 12 * * *",
                logger="recensio")
        if self.host.name == self.run_imports_on:
            self += CronJob(
                self.map("bin/sehepunkte-import"),
                timing="00 22 * * sun",
                logger="recensio")
            self += CronJob(
                self.map("bin/sehepunkte-import-artium"),
                timing="30 23 * * sun",
                logger="recensio")
            self += CronJob(
                "/home/recensio/dehydrated/certs.sh",
                timing="3 23 * * *",
                logger="recensio")
