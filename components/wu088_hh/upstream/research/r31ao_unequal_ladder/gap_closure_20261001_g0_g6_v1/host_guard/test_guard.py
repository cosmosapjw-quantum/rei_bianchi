import sys
import tempfile
import time
from pathlib import Path
import unittest
from host_guard.run_guarded import run_guarded


class GuardTests(unittest.TestCase):
    def test_completed_synthetic_process(self):
        r=run_guarded([sys.executable,'-B','-c','print(3*7)'],wall_seconds=2,memory_mib=128)
        self.assertEqual(r['status'],'PROCESS_COMPLETED')
        self.assertEqual(r['returncode'],0)
        self.assertEqual(r['stdout'],'21\n')

    def test_child_allocation_is_rejected(self):
        code='try:\n x=bytearray(256*1024*1024)\nexcept MemoryError:\n print("ADDRESS_SPACE_LIMIT_OBSERVED")\n raise SystemExit(37)'
        r=run_guarded([sys.executable,'-B','-c',code],wall_seconds=2,memory_mib=128)
        self.assertEqual(r['status'],'PROCESS_NONZERO_EXIT')
        self.assertEqual(r['returncode'],37)
        self.assertIn('ADDRESS_SPACE_LIMIT_OBSERVED',r['stdout'])

    def test_wall_timeout(self):
        r=run_guarded([sys.executable,'-B','-c','import time;time.sleep(2)'],wall_seconds=0.1,memory_mib=128)
        self.assertEqual(r['status'],'CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT')
        self.assertEqual(r['reason'],'PROCESS_GROUP_WALL_TIMEOUT')
        self.assertLess(r['wall_seconds'],1.5)

    def test_invalid_caps_and_argv(self):
        for args in ([],['']):
            with self.assertRaises(ValueError):run_guarded(args,wall_seconds=1,memory_mib=128)
        for wall,mem in ((False,128),(0,128),(float('nan'),128),(1,True),(1,0)):
            with self.assertRaises(ValueError):run_guarded([sys.executable],wall_seconds=wall,memory_mib=mem)

    def test_descendant_cannot_outlive_successful_leader(self):
        with tempfile.TemporaryDirectory() as folder:
            marker=Path(folder)/'escaped.txt'
            child='import time;from pathlib import Path;time.sleep(.4);Path('+repr(str(marker))+').write_text("bad")'
            leader='import subprocess,sys;subprocess.Popen([sys.executable,"-B","-c",'+repr(child)+'])'
            r=run_guarded([sys.executable,'-B','-c',leader],wall_seconds=1,memory_mib=128)
            self.assertEqual(r['status'],'PROCESS_CONTRACT_VIOLATION')
            self.assertEqual(r['reason'],'DESCENDANTS_SURVIVE_LEADER')
            time.sleep(.5)
            self.assertFalse(marker.exists())


if __name__=='__main__':unittest.main()
