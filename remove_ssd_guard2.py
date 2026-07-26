import sys

with open(sys.argv[1], 'r') as f:
    lines = f.readlines()

# Find the guard block: "if (e->ssd_streaming && e->multi_tier) {"
# followed by the error message, ds4_engine_close, *out = NULL, return 1, }
# We need to find the exact lines and remove them

guard_start = None
for i, line in enumerate(lines):
    if 'if (e->ssd_streaming && e->multi_tier)' in line:
        guard_start = i
        break

if guard_start is None:
    print('Guard not found')
    sys.exit(1)

print(f'Guard found at line {guard_start+1}: {lines[guard_start].strip()}')

# The guard block is:
# line: if (e->ssd_streaming && e->multi_tier) {
# line+1: fprintf(stderr,
# line+2: "ds4: --ssd-streaming is not compatible with multi-GPU placement\n");
# line+3: ds4_engine_close(e);
# line+4: *out = NULL;
# line+5: return 1;
# line+6: }

# Verify
for j in range(guard_start, guard_start + 7):
    print(f'  Line {j+1}: {lines[j].strip()}')

# Remove lines guard_start through guard_start+6
del lines[guard_start:guard_start + 7]

with open(sys.argv[1], 'w') as f:
    f.writelines(lines)
print(f'Removed {7} lines, guard eliminated')
