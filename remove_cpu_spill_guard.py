import sys

with open(sys.argv[1], 'r') as f:
    lines = f.readlines()

# Find the CPU-spill guard block that starts with:
# "ds4: CPU-spill placement detected; CPU-tier execution wiring "
# and ends with "return 1;"
# We need to find the exact lines

# Find the "CPU-spill placement detected" message
guard_start = None
for i, line in enumerate(lines):
    if 'CPU-spill placement detected' in line and 'wave-3b' in line:
        guard_start = i
        break

if guard_start is None:
    print('Guard not found')
    sys.exit(1)

print(f'Guard starts at line {guard_start+1}: {lines[guard_start].strip()}')

# The block structure (from the output):
# line: fprintf(stderr, "ds4: CPU-spill placement detected...");
# line+1: fprintf(stderr, "ds4: --gpu-vram placement does not fit...");
# line+2: "ds4:   %d placement entries spilled to CPU..."
# line+3: "ds4: Lower --ctx / --ctx-max..."
# line+4: "ds4: Refusing upfront..."
# line+5: ds4_engine_close(e);
# line+6: *out = NULL;
# line+7: return 1;
# line+8: }

# But the actual lines may vary. Let's find the closing brace.
# We need to find the matching } after the return 1;
for j in range(guard_start, min(guard_start + 20, len(lines))):
    print(f'  Line {j+1}: {lines[j].strip()}')

# Find the closing brace
closing_brace = None
for j in range(guard_start, min(guard_start + 20, len(lines))):
    if lines[j].strip() == '}':
        # Check that the next line is not a continuation
        if j + 1 < len(lines) and 'if (opt->mtp_path' in lines[j+1]:
            closing_brace = j
            break

if closing_brace is None:
    print('Could not find closing brace')
    sys.exit(1)

print(f'Closing brace at line {closing_brace+1}')

# Remove from guard_start to closing_brace inclusive
del lines[guard_start:closing_brace + 1]

with open(sys.argv[1], 'w') as f:
    f.writelines(lines)
print(f'Removed {closing_brace - guard_start + 1} lines')
