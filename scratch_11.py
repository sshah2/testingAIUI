import re

# Test line from the COBOL code
test_line = "RB0714 PERFORM 4011-Obsolete-Type-License-TBL"

# Further updated regular expression pattern to find PERFORM statements
# This pattern should correctly handle multiple hyphenated segments in the function name
pattern = r'PERFORM\s+([A-Z0-9-]+(?:-[A-Z0-9]+)*)'
match = re.search(pattern, test_line, re.IGNORECASE)

# Check the match
if match:
    called_function = match.group(1)
    print("Called Function:", called_function)
else:
    print("No match found")
