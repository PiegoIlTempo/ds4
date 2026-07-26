import sys

with open(sys.argv[1], 'r') as f:
    lines = f.readlines()

# Find the function start
func_start = None
for i, line in enumerate(lines):
    if 'static bool metal_graph_alloc_raw_cap(' in line:
        func_start = i
        break

if func_start is None:
    print('Function not found')
    sys.exit(1)

# Find opening brace - scan from func_start
brace_line = None
for i in range(func_start, len(lines)):
    if '{' in lines[i]:
        brace_line = i
        break

if brace_line is None:
    print('Opening brace not found')
    sys.exit(1)

# Count braces from brace_line to find function end
brace_count = 0
func_end = brace_line
for i in range(brace_line, len(lines)):
    brace_count += lines[i].count('{') - lines[i].count('}')
    if brace_count == 0:
        func_end = i
        break

print(f'Function from line {func_start+1} to {func_end+1} (brace at line {brace_line+1})')

# Find all return false in the function
labels = ['#1 (CUDA TP tiers)', '#2 (CUDA TP EP)', '#3 (CUDA TP output head tier)', '#4 (end of function)']
label_idx = 0
modifications = 0
for i in range(brace_line, func_end + 1):
    stripped = lines[i].strip()
    if stripped == 'return false;' or stripped == 'return false':
        # Check if already instrumented
        already_done = False
        for j in range(max(0, i-3), i):
            if 'DEBUG return false' in lines[j]:
                already_done = True
                break
        if already_done:
            print(f'  Line {i+1}: already instrumented, skipping')
            continue
        indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
        label = labels[label_idx] if label_idx < len(labels) else f'#{label_idx+1}'
        lines[i] = indent + f'fprintf(stderr, "ds4: DEBUG return false {label}\\n");\n' + lines[i]
        print(f'  Line {i+1}: instrumented {label}')
        label_idx += 1
        modifications += 1

print(f'Total: {modifications} modifications')

with open(sys.argv[1], 'w') as f:
    f.writelines(lines)
print('DONE')
