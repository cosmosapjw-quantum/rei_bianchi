#!/usr/bin/env python3
"""Read-only launcher tests: no scientific Popen, no output mutation."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("ax08_min_launcher",HERE/"launcher.py")
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class LauncherPreparation(unittest.TestCase):
    def test_reject_shell_and_rg_false_positive(self):
        for argv in (["/bin/bash","-c","rg axbi_ /some/path"],
                     ["rg","--files","research/axbi_goal_20261014"],
                     ["python3","-c","print('axbi_reionization')"]):
            self.assertFalse(m.is_science({"argv":argv}))
            self.assertFalse(m.is_owner({"argv":argv}))
        self.assertTrue(m.is_science({"argv":["/target/axbi_signed_resource_continuation","--binding","x"]}))
        self.assertTrue(m.is_owner({"argv":["python3",str(m.AX/"driver/full/post_plus_epoch_dispatch.py")],"cwd":str(m.ROOT)}))
        self.assertFalse(m.is_owner({"argv":["python3","/other_project/launcher.py"],"cwd":str(m.ROOT)}))

    def test_current_prerequisites_are_real_and_read_only(self):
        result=m.preflight()
        self.assertEqual(result["status"],"PRELAUNCH_SCOPED_LOCAL_PASS")
        self.assertEqual(result["active_science_count"],0)
        self.assertEqual(result["half_plus_classification"]["last_accepted"],312237)

    def test_immutable_binding_fails_closed(self):
        original=m.load
        def tamper(path):
            data=original(path)
            if path==m.CONTRACT:
                data["binding"]["sha256"]="0"*64
            return data
        with patch.object(m,"load",side_effect=tamper):
            with self.assertRaisesRegex(RuntimeError,"FROZEN_IDENTITY_MISMATCH:binding"):
                m.preflight()

    def test_no_controller_release_means_no_science(self):
        with tempfile.TemporaryDirectory(prefix="ax08-minus-synthetic-") as tmp:
            p=Path(tmp)/"release.json"
            p.write_text(json.dumps({"status":"PREPARATION_ONLY","case":"SHEAR_MINUS"}))
            with self.assertRaisesRegex(RuntimeError,"MISSING_RELEASE"):
                m.launch(p)
        self.assertFalse((m.OWN/"RESERVATION.json").exists())
        self.assertFalse((m.OWN/"PROCESS_ACK.json").exists())

if __name__=="__main__":
    unittest.main(verbosity=2)
