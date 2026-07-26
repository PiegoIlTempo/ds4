import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: allocate ALL per-layer tensors for CPU-spilled layers on head_tier
old = '''        const int layer_tier = placement ? placement[il + 1] : 0;
        /* SSD streaming: skip per-layer allocations for CPU-spilled layers */
        if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) continue;
        /* SSD streaming: skip per-layer allocations for CPU-spilled layers */
        if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) continue;
        g->layer_raw_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                managed_kv_cache,
                layer_tier,
                (uint64_t)raw_cap * DS4_N_HEAD_DIM * sizeof(float));'''

new = '''        const int layer_tier = placement ? placement[il + 1] : 0;
        /* SSD streaming: allocate per-layer tensors for CPU-spilled layers on head_tier */
        const int alloc_tier = (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) ? g->head_tier : layer_tier;
        g->layer_raw_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                managed_kv_cache,
                alloc_tier,
                (uint64_t)raw_cap * DS4_N_HEAD_DIM * sizeof(float));'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: allocate all per-layer tensors for CPU-spilled layers on head_tier')
else:
    print('NOT FOUND')

# Also fix the layer_tier references below to use alloc_tier
old2 = '''        const int layer_tp_partner = g->cuda_tp_attn_cache_dup
            ? metal_graph_cuda_tp_partner_tier(layer_tier) : -1;'''

new2 = '''        const int layer_tp_partner = g->cuda_tp_attn_cache_dup
            ? metal_graph_cuda_tp_partner_tier(alloc_tier) : -1;'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: layer_tp_partner uses alloc_tier')
else:
    print('NOT FOUND: layer_tp_partner')

# Fix all layer_tier references in the per-layer allocation loop to use alloc_tier
# Find all occurrences of layer_tier in the allocation block
old3 = '''            g->layer_attn_comp_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                    managed_kv_cache,
                    layer_tier,''' 

new3 = '''            g->layer_attn_comp_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                    managed_kv_cache,
                    alloc_tier,''' 

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('FIXED: layer_attn_comp_cache uses alloc_tier')
else:
    print('NOT FOUND: layer_attn_comp_cache')

old4 = '''            g->layer_attn_state_kv[il] = ds4_gpu_tensor_alloc_ptr_on(layer_tier, attn_width * attn_rows * sizeof(float));
            g->layer_attn_state_score[il] = ds4_gpu_tensor_alloc_ptr_on(layer_tier, attn_width * attn_rows * sizeof(float));'''

new4 = '''            g->layer_attn_state_kv[il] = ds4_gpu_tensor_alloc_ptr_on(alloc_tier, attn_width * attn_rows * sizeof(float));
            g->layer_attn_state_score[il] = ds4_gpu_tensor_alloc_ptr_on(alloc_tier, attn_width * attn_rows * sizeof(float));'''

if old4 in content:
    content = content.replace(old4, new4, 1)
    print('FIXED: layer_attn_state uses alloc_tier')
else:
    print('NOT FOUND: layer_attn_state')

old5 = '''                g->spec_attn_state_kv[il] =
                    ds4_gpu_tensor_alloc_ptr_on(layer_tier, attn_width * attn_rows * sizeof(float));
                g->spec_attn_state_score[il] =
                    ds4_gpu_tensor_alloc_ptr_on(layer_tier, attn_width * attn_rows * sizeof(float));'''

new5 = '''                g->spec_attn_state_kv[il] =
                    ds4_gpu_tensor_alloc_ptr_on(alloc_tier, attn_width * attn_rows * sizeof(float));
                g->spec_attn_state_score[il] =
                    ds4_gpu_tensor_alloc_ptr_on(alloc_tier, attn_width * attn_rows * sizeof(float));'''

if old5 in content:
    content = content.replace(old5, new5, 1)
    print('FIXED: spec_attn_state uses alloc_tier')
else:
    print('NOT FOUND: spec_attn_state')

old6 = '''                    g->spec_prefix1_attn_state_kv[il] =
                        ds4_gpu_tensor_alloc_ptr_on(layer_tier, attn_width * attn_rows * sizeof(float));
                    g->spec_prefix1_attn_state_score[il] =
                        ds4_gpu_tensor_alloc_ptr_on(layer_tier, attn_width * attn_rows * sizeof(float));'''

new6 = '''                    g->spec_prefix1_attn_state_kv[il] =
                        ds4_gpu_tensor_alloc_ptr_on(alloc_tier, attn_width * attn_rows * sizeof(float));
                    g->spec_prefix1_attn_state_score[il] =
                        ds4_gpu_tensor_alloc_ptr_on(alloc_tier, attn_width * attn_rows * sizeof(float));'''

if old6 in content:
    content = content.replace(old6, new6, 1)
    print('FIXED: spec_prefix1_attn_state uses alloc_tier')
else:
    print('NOT FOUND: spec_prefix1_attn_state')

# Fix index cache allocations
old7 = '''            g->layer_index_comp_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                    managed_kv_cache,
                    layer_tier,''' 

new7 = '''            g->layer_index_comp_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                    managed_kv_cache,
                    alloc_tier,''' 

if old7 in content:
    content = content.replace(old7, new7, 1)
    print('FIXED: layer_index_comp_cache uses alloc_tier')
else:
    print('NOT FOUND: layer_index_comp_cache')

old8 = '''            g->layer_index_state_kv[il] = ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));
            g->layer_index_state_score[il] = ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));'''

new8 = '''            g->layer_index_state_kv[il] = ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));
            g->layer_index_state_score[il] = ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));'''

if old8 in content:
    content = content.replace(old8, new8, 1)
    print('FIXED: layer_index_state uses alloc_tier')
else:
    print('NOT FOUND: layer_index_state')

old9 = '''                g->spec_index_state_kv[il] =
                    ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));
                g->spec_index_state_score[il] =
                    ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));'''

new9 = '''                g->spec_index_state_kv[il] =
                    ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));
                g->spec_index_state_score[il] =
                    ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));'''

if old9 in content:
    content = content.replace(old9, new9, 1)
    print('FIXED: spec_index_state uses alloc_tier')
else:
    print('NOT FOUND: spec_index_state')

old10 = '''                    g->spec_prefix1_index_state_kv[il] =
                        ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));
                    g->spec_prefix1_index_state_score[il] =
                        ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));'''

new10 = '''                    g->spec_prefix1_index_state_kv[il] =
                        ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));
                    g->spec_prefix1_index_state_score[il] =
                        ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));'''

if old10 in content:
    content = content.replace(old10, new10, 1)
    print('FIXED: spec_prefix1_index_state uses alloc_tier')
else:
    print('NOT FOUND: spec_prefix1_index_state')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
