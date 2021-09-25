from typing import NamedTuple, Union
import unittest

from pw32n.timed_workflow import TimedWorkflow, TimedStep
from pw32n.units import Secs

# Heh, algebraic types :)
class State0(NamedTuple):
    pass


class State1(NamedTuple):
    pass


class State2(NamedTuple):
    pass


ExampleState = Union[State0, State1, State2]


class TimedWorkflowExample:
    MAIN_WORKFLOW = "MAIN_WORKFLOW"

    def __init__(self) -> None:
        self.state: ExampleState = State0()
        self.last_late_by: Secs = None
        self.main_workflow = TimedWorkflow(
            name=self.MAIN_WORKFLOW,
            steps=[
                TimedStep(Secs(1000.0), self.enter_state_1),
                TimedStep(Secs(1000.0), self.enter_state_2),
            ],
        )
        self.running_workflows: set[TimedWorkflow] = set((self.main_workflow,))

    def on_update(self, delta_time: float) -> None:
        # The call to list() is important because during cleanup, we'll be removing a workflow
        # from the set while still iterating.
        for w in list(self.running_workflows):
            w.on_update(delta_time)

    def enter_state_1(self, late_by: Secs) -> None:
        assert self.main_workflow.completion_ratio_for_current_step == 1.0
        self.state = State1()
        self.last_late_by = late_by

    def enter_state_2(self, late_by: Secs) -> None:
        self.state = State2()
        self.last_late_by = late_by

        # Remember to clean up. You might want to set self.main_workflow to None as well. I can't
        # do that here because I need it in the test.
        self.running_workflows.remove(self.main_workflow)


class TimedWorkflowTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.example = TimedWorkflowExample()

    def test_entire_workflow(self) -> None:
        self.assertIsInstance(self.example.state, State0)
        self.assertIsNone(self.example.last_late_by)

        self.example.on_update(Secs(1.0))
        self.assertEqual(self.example.main_workflow.initial_countdown, 1000.0)
        self.assertEqual(self.example.main_workflow.countdown, 1000.0 - 1.0)
        self.assertEqual(
            self.example.main_workflow.completion_ratio_for_current_step, 1.0 / 1000.0
        )
        self.assertIsInstance(self.example.state, State0)

        self.example.on_update(Secs(1000.0))
        self.assertIsInstance(self.example.state, State1)
        self.assertEqual(self.example.last_late_by, Secs(1.0))

        self.example.on_update(Secs(1.0))
        self.assertIsInstance(self.example.state, State1)

        self.example.on_update(Secs(1000.0))
        self.assertIsInstance(self.example.state, State2)
        self.assertEqual(self.example.last_late_by, Secs(1.0))

        self.assertEqual(len(self.example.running_workflows), 0)

        # Things should be clean at this stage, but if you insist on calling on_update again, you
        # should get an exception.
        with self.assertRaises(ValueError) as ctx:
            self.example.running_workflows.add(self.example.main_workflow)
            self.example.on_update(Secs(1.0))
        self.assertEqual(
            ctx.exception.args[0],
            f"You forgot to cleanup your workflow; you should do that in your last step: {self.example.main_workflow}",
        )

    def test_avoid_dividing_by_zero(self) -> None:
        main_workflow = self.example.main_workflow
        main_workflow.initial_countdown = 0.0
        main_workflow.countdown = 0.0
        self.assertEqual(main_workflow.completion_ratio_for_current_step, 1.0)
