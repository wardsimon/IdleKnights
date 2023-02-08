__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from collections import deque


class TaskBase:

    def __init__(self):
        self.objective = None
        self.priority = 0





class TaskList:

    def __init__(self):
        self._tasks = deque([])
        self._current_task = None

    @property
    def current_task(self):
        return self._current_task

    def add_task(self, task: TaskBase):
        self._tasks.append(task)

    def add_new_task(self, task: TaskBase):
        self._tasks.appendleft(task)

    def start_task(self):
        self._current_task = self._tasks.popleft()
