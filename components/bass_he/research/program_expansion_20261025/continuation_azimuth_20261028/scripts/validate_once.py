"""Run exactly the new unittest suite once and save all plot data in that run."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]


class RecordedResult(unittest.TextTestResult):
    def startTest(self,test):
        self._cpu=time.process_time()
        self._wall=time.perf_counter()
        super().startTest(test)

    def stopTest(self,test):
        TESTS.SAVED["benchmarks"].append({"test":test.id(),"cpu_s":time.process_time()-self._cpu,"wall_s":time.perf_counter()-self._wall})
        super().stopTest(test)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--saved-json",required=True)
    parser.add_argument("--report-json",required=True)
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location("azimuth09_tests",ROOT/"tests/test_azimuth.py")
    TESTS=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=TESTS
    spec.loader.exec_module(TESTS)
    cpu,wall=time.process_time(),time.perf_counter()
    result=unittest.TextTestRunner(verbosity=2,resultclass=RecordedResult).run(unittest.defaultTestLoader.loadTestsFromModule(TESTS))
    report={"tests_run":result.testsRun,"failures":[[test.id(),trace] for test,trace in result.failures],"errors":[[test.id(),trace] for test,trace in result.errors],"success":result.wasSuccessful(),"suite_cpu_s":time.process_time()-cpu,"suite_wall_s":time.perf_counter()-wall,"scientific_suite_runs":1,"saved_payload_created_in_same_process":True}
    TESTS.SAVED["validation"]=report
    TESTS.SAVED["scope"]={"declared_scalar_only":True,"density":"explicit manufactured Bernstein coefficients; not empirical DCS","thermal_ports":None,"birth_pool":"UNASSIGNED","rest_binding_owner":"population_rest_energy_witness","L4_ready":False,"production_status":"NOT_APPROVED"}
    for path,value in [(args.saved_json,TESTS.SAVED),(args.report_json,report)]:
        destination=Path(path)
        temporary=destination.with_name(destination.name+".tmp")
        with temporary.open("x",encoding="utf-8") as handle:
            json.dump(value,handle,indent=2,sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary,destination)
        temporary.unlink()
        descriptor=os.open(destination.parent,os.O_RDONLY)
        try:os.fsync(descriptor)
        finally:os.close(descriptor)
    sys.exit(0 if result.wasSuccessful() else 1)
