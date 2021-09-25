from typing import NamedTuple, Callable

Secs = float
Callback = Callable[[Secs], int]


class TimedStep(NamedTuple):
    delay: Secs
    callback: Callback


class TimedWorkflow:

    """See TimedWorkflowExample in timed_workflow_test.py."""

    def __init__(self, steps: list[TimedStep]) -> None:
        self._steps = steps
        self._countdown = Secs(0.0)
        self._set_next_countdown()

    def on_update(self, delta_time: float) -> None:
        if not len(self._steps):
            raise ValueError(
                f"You forgot to cleanup your workflow; you should do that in your last step: {self}"
            )
        self._countdown -= delta_time
        if self._countdown <= 0.0:
            step = self._steps.pop(0)
            step.callback(-self._countdown)
            self._set_next_countdown()

    def _set_next_countdown(self) -> None:
        if len(self._steps):
            self._countdown = self._steps[0].delay
