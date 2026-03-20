from openc3.tools.test_runner.test import Test, SkipTestCase
load_utility("DTNFSW-1/procedures/build_tests/custody_nominal.py")
load_utility("DTNFSW-1/procedures/build_tests/custody_errors.py")

# Test case for Bundle Creation

class DTN_FSW_BD_0641_Custody_Transfer(Test):
    def setup(self):
        print("Setup")
        # Use this function for any setup specific to this test case (delete if not used)

    def test_1_nominal(self):
        print(
            f"Running {Test.current_test_suite()}:{Test.current_test()}:{Test.current_test_case()}"
        )
        
        custody_nominal(self)
        
        raise SkipTestCase

    def test_2_errors(self):
        print(
            f"Running {Test.current_test_suite()}:{Test.current_test()}:{Test.current_test_case()}"
        )
        
        custody_errors(self)
        
        raise SkipTestCase

    def teardown(self):
        print("Teardown")
        # Use this function for any teardown specific to this test case (delete if not used)
