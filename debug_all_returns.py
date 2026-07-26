import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug to every return false in metal_graph_alloc_raw_cap
# Find all "return false;" in the function
import re

# Find the function start
func_start = content.find('static bool metal_graph_alloc_raw_cap(')
if func_start < 0:
    print('Function not found')
    sys.exit(1)

# Find the function end (next function at same level)
# Count braces
brace_count = 0
func_end = func_start
in_func = False
for i in range(func_start, len(content)):
    if content[i] == '{':
        brace_count += 1
        in_func = True
    elif content[i] == '}':
        brace_count -= 1
        if in_func and brace_count == 0:
            func_end = i + 1
            break

print(f'Function from {func_start} to {func_end}')

# Find all return false in the function body
func_body = content[func_start:func_end]
lines = func_body.split('\n')
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == 'return false;' or stripped == 'return false':
        # Add a debug print before this return
        old = line
        indent = line[:len(line) - len(stripped)]
        new = indent + 'fprintf(stderr, "ds4: DEBUG metal_graph_alloc_raw_cap returning false at line %d\\n", __LINE__);\n' + line
        if old in content:
            content = content.replace(old, new, 1)
            print(f'FIXED: added debug at line {i+1}')
        else:
            print(f'NOT FOUND at line {i+1}: {stripped[:50]}')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
