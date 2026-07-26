import sys

with open(sys.argv[1], 'r') as f:
    lines = f.readlines()

# Find the 4 return false statements in metal_graph_alloc_raw_cap
# We need to find the function start
func_start = None
for i, line in enumerate(lines):
    if 'static bool metal_graph_alloc_raw_cap(' in line:
        func_start = i
        break

if func_start is None:
    print('Function not found')
    sys.exit(1)

# Find function end by brace counting
brace_count = 0
func_end = func_start
for i in range(func_start, len(lines)):
    brace_count += lines[i].count('{') - lines[i].count('}')
    if brace_count == 0 and i > func_start:
        func_end = i
        break

print(f'Function from line {func_start+1} to {func_end+1}')

# Find all return false in the function
labels = ['#1 (CUDA TP tiers)', '#2 (CUDA TP EP)', '#3 (CUDA TP output head tier)', '#4 (end of function)']
label_idx = 0
modifications = 0
for i in range(func_start, func_end + 1):
    stripped = lines[i].strip()
    if stripped == 'return false;' or stripped == 'return false':
        # Check if already instrumented
        if 'DEBUG return false' in lines[i-1] if i > 0 else False:
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
