from threading import Thread
from typing import Callable

import schedule

from .app import AppJob


class Runner:
    def __init__(self, jobs: list[AppJob]):
        if len(jobs) > 0:
            for job in jobs:
                schedule.every(job.interval_seconds).seconds.do(
                    self.__run_threaded, job.job
                )

            print("JOBS running...")

    @staticmethod
    def __run_threaded(job: Callable[[], None]):
        job_thread = Thread(target=job)
        job_thread.start()

    @staticmethod
    def run_pending():
        schedule.run_pending()
