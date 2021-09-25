from typing import NamedTuple, Callable

from pw32n.units import Secs

Callback = Callable[[Secs], int]


class TimedStep(NamedTuple):
    delay: Secs
    callback: Callback


class TimedWorkflow:

    """See TimedWorkflowExample in timed_workflow_test.py."""

    def __init__(self, name: str, steps: list[TimedStep]) -> None:
        self.name = name
        self.steps = steps
        self.initial_countdown = self.countdown = Secs(0.0)
        self._set_next_countdown()

    def on_update(self, delta_time: float) -> None:
        if not len(self.steps):
            raise ValueError(
                f"You forgot to cleanup your workflow; you should do that in your last step: {self}"
            )
        self.countdown -= delta_time
        if self.countdown <= 0.0:
            step = self.steps.pop(0)
            step.callback(-self.countdown)
            self._set_next_countdown()

    def _set_next_countdown(self) -> None:
        if len(self.steps):
            self.initial_countdown = self.countdown = self.steps[0].delay

    @property
    def completion_ratio_for_current_step(self) -> float:
        return (
            self.initial_countdown - max(0.0, self.countdown)
        ) / self.initial_countdown
