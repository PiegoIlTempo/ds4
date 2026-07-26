import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: allocate KV cache for CPU-spilled layers on head_tier when SSD streaming
old = '''        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        g->layer_raw_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                managed_kv_cache, g->head_tier,
                (uint64_t)raw_cap * DS4_N_HEAD_DIM * sizeof(float));'''

new = '''        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) {
            /* SSD streaming: allocate KV cache for CPU-spilled layers on head_tier */
            g->layer_raw_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                    managed_kv_cache, g->head_tier,
                    (uint64_t)raw_cap * DS4_N_HEAD_DIM * sizeof(float));
            continue;
        }
        g->layer_raw_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                managed_kv_cache, g->head_tier,
                (uint64_t)raw_cap * DS4_N_HEAD_DIM * sizeof(float));'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: allocate KV cache for CPU-spilled layers on head_tier')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
