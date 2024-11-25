from proto.ups_test_pb2 import TestType


class TestManager:
    def __init__(self):
        """Initialize the TestManager with predefined test descriptions."""
        self.test_descriptions = self.load_test_descriptions()

    def load_test_descriptions(self):
        """Load test descriptions and map them to TestType."""
        return {
            TestType.LIGHT_LOAD_AND_FUNCTION_TEST: (
                "UPS runs in normal mode with light load and performs a function test to verify basic operation. "
                "Ensure all functionality operates correctly under light load conditions."
            ),
            TestType.NO_LOAD_TEST: (
                "With the UPS operating in battery mode of operation at no load, measure the r.m.s. output voltage."
            ),
            TestType.FULL_LOAD_TEST: (
                "UPS runs in normal mode, applying 100% reference test load to the UPS output. Measure the output voltage "
                "to ensure it meets the required specifications under full load conditions."
            ),
            TestType.AC_INPUT_FAILURE: (
                "Test the UPS's response to a sudden AC input failure while running in normal mode with load applied. "
                "Verify seamless transfer to battery mode and proper alarms during the failure."
            ),
            TestType.AC_INPUT_RETURN: (
                "1. UPS runs in normal mode, applying 100% linear load. Then cut off input, UPS transfers to battery. "
                "A few seconds later, return AC input, UPS transfers to normal again.\n"
                "2. UPS runs in normal mode, applying 100% linear load. Then cut off input, UPS transfers to battery.\n"
                "3. A few seconds later, return AC input with improper phase rotation. UPS can't transfer to normal and "
                "alarms 'Rectifier Phase'.\n"
                "4. Then cut off input, and return AC input with proper phase rotation. UPS transfers to normal again."
            ),
            TestType.INPUT_POWER_FACTOR: (
                "Measure the input power factor of the UPS under varying load conditions (25%, 50%, 75%, 100%) to "
                "ensure compliance with power factor specifications."
            ),
            TestType.CHANGE_OPERATION_MODE: (
                "Test the UPS's ability to switch between different operational modes (e.g., normal, eco, and battery) "
                "without interrupting the output load. Verify functionality and timing during the mode transitions."
            ),
            TestType.STORED_ENERGY_TIME: (
                "Measure the duration for which the UPS can sustain the load in battery mode after the input power is cut off. "
                "Ensure it meets the expected battery backup duration."
            ),
            TestType.SwitchTest: (
                "Test the UPS's ability to switch seamlessly between normal mode and battery mode during input disruptions. "
                "Verify the smoothness of transition and ensure no load interruption."
            ),
            TestType.BackupTest: (
                "Simulate a power outage and ensure the UPS transitions to battery backup mode. Measure the duration "
                "for which it can support the load and verify alarms and indicators."
            ),
            TestType.EfficiencyTest: (
                "Measure the efficiency of the UPS under varying load conditions (25%, 50%, 75%, 100%) to ensure it meets "
                "the specified efficiency standards."
            ),
            TestType.SteadyState_InputVoltage_Test: (
                "With the UPS operating in steady-state mode, measure and verify the input voltage under varying load "
                "conditions. Ensure it falls within acceptable limits."
            ),
            TestType.WaveformTest: (
                "Examine the output waveform of the UPS under different load conditions to verify that it remains clean and "
                "within the specified total harmonic distortion (THD) levels."
            ),
            TestType.EFFICIENCY_NORMAL_MODE: (
                "UPS runs in normal mode with charging off. Measure the UPS efficiency at 25%, 50%, 75%, and 100% reference load."
            ),
            TestType.EFFICIENCY_STORAGE_MODE: (
                "UPS operates in storage mode. Measure and verify the efficiency across varying load conditions to ensure it meets "
                "specified standards."
            ),
            TestType.OVERLOAD_NORMAL_MODE: (
                "Simulate an overload condition with the UPS running in normal mode. Verify the UPS's response, including alarms, "
                "load shedding, or shutdown as applicable."
            ),
            TestType.OVERLOAD_STORAGE_MODE: (
                "Simulate an overload condition with the UPS running in storage mode. Verify the UPS's response, ensuring proper "
                "alarms and protection mechanisms are triggered."
            ),
        }

    def get_test_description(self, test_type: TestType) -> str:
        """Retrieve the description for a given TestType."""
        return self.test_descriptions.get(test_type, "Description not found.")


# Example Usage
if __name__ == "__main__":
    manager = TestManager()

    # Retrieve and print specific descriptions
    print("AC_INPUT_RETURN Description:")
    print(manager.get_test_description(TestType.AC_INPUT_RETURN))

    print("\nEFFICIENCY_NORMAL_MODE Description:")
    print(manager.get_test_description(TestType.EFFICIENCY_NORMAL_MODE))

    print("\nFULL_LOAD_TEST Description:")
    print(manager.get_test_description(TestType.FULL_LOAD_TEST))
