import unittest

from pw32n.timed_workflow import MS, TimedWorkflow, TimedStep


class TimedWorkflowExample:
    STATE_0 = "STATE_0"
    STATE_1 = "STATE_1"
    STATE_2 = "STATE_2"

    def __init__(self) -> None:
        self.state = self.STATE_0
        self.last_late_by: MS = None
        self.main_workflow = TimedWorkflow(
            [
                TimedStep(MS(1000.0), self.enter_state_1),
                TimedStep(MS(1000.0), self.enter_state_2),
            ]
        )
        self.running_workflows: set[TimedWorkflow] = set((self.main_workflow,))

    def on_update(self, delta_time: float) -> None:
        # The call to list() is important because during cleanup, we'll be removing a workflow
        # from the set while still iterating.
        for w in list(self.running_workflows):
            w.on_update(delta_time)

    def enter_state_1(self, late_by: MS) -> None:
        self.state = self.STATE_1
        self.last_late_by = late_by

    def enter_state_2(self, late_by: MS) -> None:
        self.state = self.STATE_2
        self.last_late_by = late_by

        # Remember to clean up.
        self.running_workflows.remove(self.main_workflow)


class TimedWorkflowTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.example = TimedWorkflowExample()

    def test_entire_workflow(self) -> None:
        self.assertEqual(self.example.state, TimedWorkflowExample.STATE_0)
        self.assertIsNone(self.example.last_late_by)

        self.example.on_update(MS(1.0))
        self.assertEqual(self.example.state, TimedWorkflowExample.STATE_0)

        self.example.on_update(MS(1000.0))
        self.assertEqual(self.example.state, TimedWorkflowExample.STATE_1)
        self.assertEqual(self.example.last_late_by, MS(1.0))

        self.example.on_update(MS(1.0))
        self.assertEqual(self.example.state, TimedWorkflowExample.STATE_1)

        self.example.on_update(MS(1000.0))
        self.assertEqual(self.example.state, TimedWorkflowExample.STATE_2)
        self.assertEqual(self.example.last_late_by, MS(1.0))

        self.assertEqual(len(self.example.running_workflows), 0)

        # Things should be clean at this stage, but if you insist on calling on_update again, you
        # should get an exception.
        with self.assertRaises(ValueError) as ctx:
            self.example.running_workflows.add(self.example.main_workflow)
            self.example.on_update(MS(1.0))
        self.assertEqual(
            ctx.exception.args[0],
            f"You forgot to cleanup your workflow; you should do that in your last step: {self.example.main_workflow}",
        )
