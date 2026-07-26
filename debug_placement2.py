import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug print to see used_tier and placement
old = '    bool used_tier[DS4_MAX_GPUS] = {0};\n    used_tier[0] = true; /* single-tier baseline always uses tier 0 */\n    if (placement) {'
new = '    bool used_tier[DS4_MAX_GPUS] = {0};\n    used_tier[0] = true; /* single-tier baseline always uses tier 0 */\n    if (placement) {\n        fprintf(stderr, "ds4: DEBUG placement[0..5] = %d %d %d %d %d %d\\n",\n                placement[0], placement[1], placement[2], placement[3], placement[4], placement[5]);\n        fprintf(stderr, "ds4: DEBUG placement[DS4_N_LAYER] = %d, placement[DS4_N_LAYER+1] = %d\\n",\n                placement[DS4_N_LAYER], placement[DS4_N_LAYER+1]);'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added debug prints')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
