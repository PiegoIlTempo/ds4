import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add SSD streaming skip for per-layer allocations
old = '''    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        /* per-layer Class L allocations land on the layer's
         * home tier. placement is NULL on single-tier / diagnostic paths
         * (all-tier-0); non-NULL on the engine path that opted into
         * multi-tier. layer_tier == 0 in single-tier mode is the
         * byte-equivalent path through metal_graph_alloc_kv_cache_tensor_on
         * and ds4_gpu_tensor_alloc_ptr_on. */
        const int layer_tier = placement ? placement[il + 1] : 0;'''

new = '''    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        /* per-layer Class L allocations land on the layer's
         * home tier. placement is NULL on single-tier / diagnostic paths
         * (all-tier-0); non-NULL on the engine path that opted into
         * multi-tier. layer_tier == 0 in single-tier mode is the
         * byte-equivalent path through metal_graph_alloc_kv_cache_tensor_on
         * and ds4_gpu_tensor_alloc_ptr_on. */
        const int layer_tier = placement ? placement[il + 1] : 0;
        /* SSD streaming: skip per-layer allocations for CPU-spilled layers */
        if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) continue;'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added SSD streaming skip for per-layer allocations')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
