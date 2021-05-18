from batou.lib.cron import CronJob
from batou.lib.supervisor import Supervisor


class Supervisor(Supervisor):
    """Deploy supervisor with a reboot cron job"""
    def configure(self):
        super(Supervisor, self).configure()
        self += CronJob(
            self.map("bin/supervisord"),
            timing="@reboot",
            logger="recensio")
