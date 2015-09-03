# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import multiprocessing

from helpers import unittest
import mock
import json

import luigi
import luigi.date_interval
import luigi.notifications
from luigi.worker import TaskException, TaskProcess
from luigi.scheduler import DONE, FAILED

luigi.notifications.DEBUG = True


class MyTask(luigi.Task):
    # Test overriding the constructor without calling the superconstructor
    # This is a simple mistake but caused an error that was very hard to understand

    def __init__(self):
        pass


class SuccessTask(luigi.Task):

    def on_success(self):
        return "test success expl"


class FailTask(luigi.Task):

    def run(self):
        raise BaseException("Uh oh.")

    def on_failure(self, exception):
        return "test failure expl"


class WorkerTaskTest(unittest.TestCase):

    def test_constructor(self):
        def f():
            luigi.build([MyTask()], local_scheduler=True)
        self.assertRaises(TaskException, f)

    def test_run_none(self):
        def f():
            luigi.build([None], local_scheduler=True)
        self.assertRaises(TaskException, f)


class TaskProcessTest(unittest.TestCase):

    def test_update_result_queue_on_success(self):
        task = SuccessTask()
        result_queue = multiprocessing.Queue()
        task_process = TaskProcess(task, 1, result_queue)

        with mock.patch.object(result_queue, 'put') as mock_put:
            task_process.run()
            mock_put.assert_called_once_with((task.task_id, DONE, json.dumps("test success expl"), [], None))

    def test_update_result_queue_on_failure(self):
        task = FailTask()
        result_queue = multiprocessing.Queue()
        task_process = TaskProcess(task, 1, result_queue)

        with mock.patch.object(result_queue, 'put') as mock_put:
            task_process.run()
            mock_put.assert_called_once_with((task.task_id, FAILED, json.dumps("test failure expl"), [], []))


if __name__ == '__main__':
    unittest.main()
