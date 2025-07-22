import os
import sys

# Edge case 2: Very long lines that might break parsing
def extremely_long_function_name_that_goes_on_and_on_and_on_and_should_not_break_the_parser_but_might_cause_issues_with_very_long_identifiers_and_function_names(parameter_with_extremely_long_name_that_should_be_tested, another_parameter_with_ridiculously_long_name_for_testing_purposes, third_parameter_also_with_very_long_name):
    os.system("echo 'This is a command injection with a very long function name'")

# Edge case 3: Unicode and special characters
def функция_с_unicode_именем():
    система = "rm -rf /"  # Command injection with unicode
    os.system(система)

# Edge case 4: Nested strings and complex formatting
def complex_string_formatting(user_input):
    command = f"""
    echo "This is a complex command with nested quotes and 'single quotes' and {user_input}"
    """
    os.system(command)

# Edge case 5: Multiple vulnerabilities in single line
def multiple_issues_single_line(user_input): 
    os.system(f"rm {user_input}"); exec("dangerous_code"); eval("more_danger")

# Edge case 6: Comments with potential false positives
# This is not a real vulnerability: os.system("fake")
# Neither is this: eval("not_real")
def legitimate_function():
    print("This function is safe")

# Edge case 7: Very long string literals
VERY_LONG_SECRET = "sk-live-" + "a" * 100 + "very_long_secret_key_for_testing_scanner_robustness"