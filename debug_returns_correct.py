import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Find the function
func_marker = 'static bool metal_graph_alloc_raw_cap('
func_start = content.find(func_marker)
if func_start < 0:
    print('Function not found')
    sys.exit(1)

# Find opening brace
brace_start = content.find('{', func_start)
if brace_start < 0:
    print('Opening brace not found')
    sys.exit(1)

# Get the function body
func_body = content[brace_start:]

# Find all "return false;" in the function body
# We need to track brace depth to stay within the function
depth = 0
pos = 0
returns_found = []
while pos < len(func_body):
    c = func_body[pos]
    if c == '{':
        depth += 1
    elif c == '}':
        depth -= 1
        if depth < 0:
            break  # end of function
    elif c == 'r' and depth >= 0:
        # Check for "return false;"
        if func_body[pos:pos+14] == 'return false;\n' or func_body[pos:pos+13] == 'return false\n':
            # Check it's not already instrumented
            before = func_body[max(0,pos-100):pos]
            if 'DEBUG metal_graph_alloc_raw_cap returning false' not in before:
                returns_found.append(pos)
                pos += 13
                continue
            else:
                pos += 13
                continue
        elif func_body[pos:pos+14] == 'return false;\r' or func_body[pos:pos+13] == 'return false\r':
            returns_found.append(pos)
            pos += 13
            continue
    pos += 1

print(f'Found {len(returns_found)} uninstrumented return false statements')

# Add debug prints before each one (in reverse order to preserve positions)
for rpos in reversed(returns_found):
    # Find the start of the line
    line_start = func_body.rfind('\n', 0, rpos) + 1
    indent = func_body[line_start:rpos]
    # Count leading whitespace
    ws = ''
    for c in indent:
        if c in ' \t':
            ws += c
        else:
            break
    debug_line = ws + 'fprintf(stderr, "ds4: DEBUG metal_graph_alloc_raw_cap returning false at line %d\\n", __LINE__);\n'
    func_body = func_body[:rpos] + debug_line + func_body[rpos:]

# Replace the function body
content = content[:brace_start] + func_body

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
