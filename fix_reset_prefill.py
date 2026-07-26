import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix metal_graph_reset_prefill_state to skip CPU-spilled layers
old = '''static bool metal_graph_reset_prefill_state(ds4_gpu_graph *g) {
    memset(g->layer_n_comp, 0, sizeof(g->layer_n_comp));
    memset(g->layer_n_index_comp, 0, sizeof(g->layer_n_index_comp));
    g->mtp_n_raw = 0;
    metal_graph_dspark_cache_reset(g);
    metal_graph_dspark_capture_invalidate(g);
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        const uint32_t ratio = ds4_layer_compress_ratio(il);
        if (ratio == 0) continue;'''

new = '''static bool metal_graph_reset_prefill_state(ds4_gpu_graph *g) {
    memset(g->layer_n_comp, 0, sizeof(g->layer_n_comp));
    memset(g->layer_n_index_comp, 0, sizeof(g->layer_n_index_comp));
    g->mtp_n_raw = 0;
    metal_graph_dspark_cache_reset(g);
    metal_graph_dspark_capture_invalidate(g);
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        /* SSD streaming: skip state reset for CPU-spilled layers */
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        const uint32_t ratio = ds4_layer_compress_ratio(il);
        if (ratio == 0) continue;'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: reset_prefill_state skip CPU-spill')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
