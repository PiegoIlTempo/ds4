import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix metal_graph_build_prefill_stages to skip CPU-spilled layers
old = '''    uint32_t ns = 0;
    int prev_tier = -1;
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        const int tier = g->placement[il + 1];
        if (tier < 0 || tier >= DS4_MAX_GPUS) return false;'''

new = '''    uint32_t ns = 0;
    int prev_tier = -1;
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        const int tier = g->placement[il + 1];
        /* SSD streaming: skip CPU-spilled layers (demand-loaded from SSD) */
        if (g->ssd_streaming && tier == DS4_LAYER_PACK_CPU) continue;
        if (tier < 0 || tier >= DS4_MAX_GPUS) return false;'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: build_prefill_stages skip CPU-spill')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
