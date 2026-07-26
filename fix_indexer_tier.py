import sys

with open('ds4.c', 'r') as f:
    content = f.read()

# Fix: replace layer_tier with alloc_tier in indexer state allocation block
# The block starts with layer_index_comp_cache and ends with the index_state_score fill
old = '''                g->layer_index_comp_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                        managed_kv_cache,
                        layer_tier,
                        (uint64_t)g->layer_comp_cap[il] * DS4_N_INDEXER_HEAD_DIM * sizeof(float));
                g->layer_index_state_kv[il] = ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));
                g->layer_index_state_score[il] = ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));
                if (enable_frontier_snapshot) {
                    g->spec_index_state_kv[il] =
                        ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));
                    g->spec_index_state_score[il] =
                        ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));
                    if (enable_prefix1_snapshot) {
                        g->spec_prefix1_index_state_kv[il] =
                            ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));
                        g->spec_prefix1_index_state_score[il] =
                            ds4_gpu_tensor_alloc_ptr_on(layer_tier, index_width * index_rows * sizeof(float));
                    }
                }'''

new = '''                g->layer_index_comp_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                        managed_kv_cache,
                        alloc_tier,
                        (uint64_t)g->layer_comp_cap[il] * DS4_N_INDEXER_HEAD_DIM * sizeof(float));
                g->layer_index_state_kv[il] = ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));
                g->layer_index_state_score[il] = ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));
                if (enable_frontier_snapshot) {
                    g->spec_index_state_kv[il] =
                        ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));
                    g->spec_index_state_score[il] =
                        ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));
                    if (enable_prefix1_snapshot) {
                        g->spec_prefix1_index_state_kv[il] =
                            ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));
                        g->spec_prefix1_index_state_score[il] =
                            ds4_gpu_tensor_alloc_ptr_on(alloc_tier, index_width * index_rows * sizeof(float));
                    }
                }'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: indexer state allocation now uses alloc_tier instead of layer_tier')
else:
    print('NOT FOUND: indexer state allocation block')

with open('ds4.c', 'w') as f:
    f.write(content)
print('DONE')
