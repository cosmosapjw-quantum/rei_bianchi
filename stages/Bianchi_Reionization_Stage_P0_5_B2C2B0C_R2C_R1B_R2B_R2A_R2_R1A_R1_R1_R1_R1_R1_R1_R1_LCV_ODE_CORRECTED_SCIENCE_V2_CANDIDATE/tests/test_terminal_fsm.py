from __future__ import annotations

from pathlib import Path
import sys
import unittest


ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
sys.path.insert(0, str(ANALYSIS))

try:
    import terminal_fsm as fsm
except ModuleNotFoundError:
    fsm = None


EXPECTED_ACTIONS = {
    "START",
    "RECOVER",
    "ACCEPT",
    "BISECT",
    "EVENT_RESTART",
    "PAUSE_ACCEPT_LIMIT",
    "PAUSE_ATTEMPT_LIMIT",
    "RESUME",
    "COMPLETE",
    "BLOCK",
    "ABORT",
    "INSPECT",
}


class TerminalStateMachineTests(unittest.TestCase):
    def require_module(self):
        self.assertIsNotNone(fsm, "terminal_fsm.py is not implemented")
        return fsm

    def test_transition_function_is_total_for_all_typed_pairs(self) -> None:
        module = self.require_module()
        self.assertEqual({item.name for item in module.Action}, EXPECTED_ACTIONS)
        states = (
            module.RunState(module.RunPhase.READY),
            module.RunState(module.RunPhase.RUNNING),
            module.RunState(
                module.RunPhase.PAUSED,
                pause_reason=module.PauseReason.ACCEPT_LIMIT,
            ),
            module.RunState(
                module.RunPhase.TERMINAL,
                terminal_outcome=module.TerminalOutcome.BLOCKED_EVENT,
            ),
        )
        for state in states:
            for action in module.Action:
                with self.subTest(phase=state.phase.name, action=action.name):
                    result = module.transition(state, action)
                    self.assertIsInstance(result, module.TransitionResult)
                    self.assertIsInstance(result.state, module.RunState)

    def test_every_terminal_action_is_the_same_byte_no_write_self_loop(self) -> None:
        module = self.require_module()
        actions = tuple(module.Action) + ("UNKNOWN_ACTION", object())
        for outcome in module.TerminalOutcome:
            state = module.RunState(
                module.RunPhase.TERMINAL,
                terminal_outcome=outcome,
                transition_number=17,
                generation_number=5,
                regime_epoch=2,
                cursor_complete=outcome
                is module.TerminalOutcome.COMPLETE_CANDIDATE_UNSEALED,
            )
            before = module.canonical_state_bytes(state)
            for action in actions:
                with self.subTest(outcome=outcome.name, action=repr(action)):
                    result = module.transition(state, action)
                    self.assertIs(result.state, state)
                    self.assertFalse(result.write_required)
                    self.assertEqual(result.code, module.TransitionCode.TERMINAL_NO_WRITE)
                    self.assertEqual(module.canonical_state_bytes(result.state), before)

    def test_resume_is_legal_only_from_pause(self) -> None:
        module = self.require_module()
        paused = module.RunState(
            module.RunPhase.PAUSED,
            pause_reason=module.PauseReason.ATTEMPT_LIMIT,
        )
        resumed = module.transition(paused, module.Action.RESUME)
        self.assertEqual(resumed.state.phase, module.RunPhase.RUNNING)
        self.assertIsNone(resumed.state.pause_reason)
        self.assertTrue(resumed.write_required)

        for phase in (module.RunPhase.READY, module.RunPhase.RUNNING):
            with self.subTest(phase=phase.name):
                illegal = module.transition(module.RunState(phase), module.Action.RESUME)
                self.assertEqual(illegal.state.phase, module.RunPhase.TERMINAL)
                self.assertEqual(
                    illegal.state.terminal_outcome,
                    module.TerminalOutcome.BLOCKED_PROTOCOL,
                )

    def test_unknown_and_illegal_actions_fail_closed(self) -> None:
        module = self.require_module()
        ready = module.RunState(module.RunPhase.READY)
        unknown = module.transition(ready, "DO_WHATEVER")
        self.assertEqual(unknown.code, module.TransitionCode.FAIL_CLOSED_UNKNOWN)
        self.assertEqual(
            unknown.state.terminal_outcome,
            module.TerminalOutcome.BLOCKED_PROTOCOL,
        )

        illegal = module.transition(ready, module.Action.ACCEPT)
        self.assertEqual(illegal.code, module.TransitionCode.FAIL_CLOSED_ILLEGAL)
        self.assertEqual(
            illegal.state.terminal_outcome,
            module.TerminalOutcome.BLOCKED_PROTOCOL,
        )

    def test_complete_requires_cursor_and_closeout(self) -> None:
        module = self.require_module()
        incomplete = module.RunState(module.RunPhase.RUNNING, cursor_complete=False)
        denied = module.transition(
            incomplete,
            module.Action.COMPLETE,
            closeout_passed=True,
        )
        self.assertEqual(
            denied.state.terminal_outcome,
            module.TerminalOutcome.BLOCKED_PROTOCOL,
        )

        finished = module.RunState(module.RunPhase.RUNNING, cursor_complete=True)
        no_closeout = module.transition(finished, module.Action.COMPLETE)
        self.assertEqual(
            no_closeout.state.terminal_outcome,
            module.TerminalOutcome.BLOCKED_PROTOCOL,
        )

        completed = module.transition(
            finished,
            module.Action.COMPLETE,
            closeout_passed=True,
        )
        self.assertEqual(completed.state.phase, module.RunPhase.TERMINAL)
        self.assertEqual(
            completed.state.terminal_outcome,
            module.TerminalOutcome.COMPLETE_CANDIDATE_UNSEALED,
        )

    def test_valid_progress_and_pause_transitions_are_explicit(self) -> None:
        module = self.require_module()
        ready = module.RunState(module.RunPhase.READY)
        running = module.transition(ready, module.Action.START).state
        self.assertEqual(running.phase, module.RunPhase.RUNNING)

        accepted = module.transition(
            running,
            module.Action.ACCEPT,
            next_cursor_complete=True,
        ).state
        self.assertEqual(accepted.generation_number, 1)
        self.assertTrue(accepted.cursor_complete)

        paused = module.transition(
            accepted,
            module.Action.PAUSE_ATTEMPT_LIMIT,
        ).state
        self.assertEqual(paused.phase, module.RunPhase.PAUSED)
        self.assertEqual(paused.pause_reason, module.PauseReason.ATTEMPT_LIMIT)


if __name__ == "__main__":
    unittest.main()
