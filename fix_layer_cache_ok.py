import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix layer_cache_ok to skip CPU-spilled layers when SSD streaming
old = '''    bool layer_cache_ok = true;
    for (uint32_t il = 0; layer_cache_ok && il < DS4_N_LAYER; il++) {
        layer_cache_ok = g->layer_raw_cache[il] != NULL;'''

new = '''    bool layer_cache_ok = true;
    for (uint32_t il = 0; layer_cache_ok && il < DS4_N_LAYER; il++) {
        /* SSD streaming: skip cache check for CPU-spilled layers */
        if (g->ssd_streaming && placement && placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        layer_cache_ok = g->layer_raw_cache[il] != NULL;'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: layer_cache_ok skip CPU-spill')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
