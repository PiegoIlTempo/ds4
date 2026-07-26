import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

changes = 0

# PATCH 1: Allocate KV cache for CPU-spilled layers on head_tier
old = '''    bool layer_cache_ok = true;
    for (uint32_t il = 0; layer_cache_ok && il < DS4_N_LAYER; il++) {
        /* SSD streaming: skip cache check for CPU-spilled layers */
        if (g->ssd_streaming && placement && placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        layer_cache_ok = g->layer_raw_cache[il] != NULL;'''

new = '''    bool layer_cache_ok = true;
    for (uint32_t il = 0; layer_cache_ok && il < DS4_N_LAYER; il++) {
        /* SSD streaming: allocate KV cache for CPU-spilled layers on head_tier */
        if (g->ssd_streaming && placement && placement[il + 1] == DS4_LAYER_PACK_CPU) {
            g->layer_raw_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                    managed_kv_cache, g->head_tier,
                    (uint64_t)raw_cap * DS4_N_HEAD_DIM * sizeof(float));
            if (!g->layer_raw_cache[il]) { layer_cache_ok = false; break; }
            continue;
        }
        layer_cache_ok = g->layer_raw_cache[il] != NULL;'''

if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print('P1: Allocate KV cache for CPU-spilled layers on head_tier')

# PATCH 2: Handle CPU-spill tier in encode_decode_layer_phase
old = '''    if (g->placement) {
        const int this_tier = g->placement[il + 1];
        if (!metal_graph_set_active_tier_decode(g, this_tier)) return false;
    }'''

new = '''    if (g->placement) {
        const int this_tier = g->placement[il + 1];
        /* SSD streaming: CPU-spilled layers execute on the current tier */
        if (g->ssd_streaming && this_tier == DS4_LAYER_PACK_CPU) {
            /* Keep current active_tier */
        } else if (!metal_graph_set_active_tier_decode(g, this_tier)) {
            return false;
        }
    }'''

if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print('P2: Handle CPU-spill tier in encode_decode_layer_phase')

# PATCH 3: Remove the skip in decode loop - now we have KV cache for CPU-spilled layers
old = '''        /* SSD streaming: skip CPU-spilled layers */
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        ok = metal_graph_encode_decode_layer(g,'''

new = '''        /* SSD streaming: map CPU-spilled layer weights from host memory */
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) {
            if (!metal_graph_stream_map_layer_decode(model, weights, il)) {
                ok = false;
                break;
            }
        }
        ok = metal_graph_encode_decode_layer(g,'''

if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print('P3: Map CPU-spilled layers from SSD in decode loop')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print(f'DONE: {changes} patches applied')
