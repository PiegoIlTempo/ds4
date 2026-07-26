import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: don't set used_tier for CPU-spilled entries (DS4_LAYER_PACK_CPU = -1)
old = '            if (p >= 0 && p < DS4_MAX_GPUS) used_tier[p] = true;'
new = '            if (p >= 0 && p < DS4_MAX_GPUS) used_tier[p] = true; else if (g->ssd_streaming) continue;'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: used_tier skips CPU-spilled entries when SSD streaming')
else:
    print('NOT FOUND: used_tier check')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
