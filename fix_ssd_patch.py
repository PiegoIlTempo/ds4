import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix the SSD streaming skip block in metal_graph_alloc_raw_cap
# Remove references to non-existent fields (layer_attn_state_kv_comp, etc.)
old = '''        if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) {
            /* SSD streaming: skip per-layer scratch allocation for
             * CPU-spilled layers. Weights will be loaded on demand. */
            g->layer_raw_cache[il] = NULL;
            g->layer_raw_cache_tp[il] = NULL;
            g->layer_attn_comp_cache[il] = NULL;
            g->layer_attn_comp_cache_tp[il] = NULL;
            g->layer_attn_state_kv[il] = NULL;
            g->layer_attn_state_score[il] = NULL;
            g->layer_attn_state_kv_comp[il] = NULL;
            g->layer_attn_state_score_comp[il] = NULL;
            g->layer_attn_state_kv_comp_tp[il] = NULL;
            g->layer_attn_state_score_comp_tp[il] = NULL;
            g->layer_attn_state_kv_comp_scratch[il] = NULL;
            g->layer_attn_state_score_comp_scratch[il] = NULL;
            g->layer_attn_state_kv_comp_scratch_tp[il] = NULL;
            g->layer_attn_state_score_comp_scratch_tp[il] = NULL;
            g->layer_attn_state_kv_comp_scratch_2[il] = NULL;
            g->layer_attn_state_score_comp_scratch_2[il] = NULL;
            g->layer_attn_state_kv_comp_scratch_2_tp[il] = NULL;
            g->layer_attn_state_score_comp_scratch_2_tp[il] = NULL;
            g->layer_attn_state_kv_comp_scratch_3[il] = NULL;
            g->layer_attn_state_score_comp_scratch_3[il] = NULL;
            g->layer_attn_state_kv_comp_scratch_3_tp[il] = NULL;
            g->layer_attn_state_score_comp_scratch_3_tp[il] = NULL;
            g->layer_attn_state_kv_comp_scratch_4[il] = NULL;
            g->layer_attn_state_score_comp_scratch_4[il] = NULL;
            g->layer_attn_state_kv_comp_scratch_4_tp[il] = NULL;
            g->layer_attn_state_score_comp_scratch_4_tp[il] = NULL;
            continue;
        }'''

new = '''        if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) {
            /* SSD streaming: skip per-layer scratch allocation for
             * CPU-spilled layers. Weights will be loaded on demand. */
            g->layer_raw_cache[il] = NULL;
            g->layer_raw_cache_tp[il] = NULL;
            g->layer_attn_comp_cache[il] = NULL;
            g->layer_attn_comp_cache_tp[il] = NULL;
            g->layer_attn_state_kv[il] = NULL;
            g->layer_attn_state_score[il] = NULL;
            g->layer_index_comp_cache[il] = NULL;
            g->layer_index_state_kv[il] = NULL;
            g->layer_index_state_score[il] = NULL;
            g->spec_attn_state_kv[il] = NULL;
            g->spec_attn_state_score[il] = NULL;
            g->spec_index_state_kv[il] = NULL;
            g->spec_index_state_score[il] = NULL;
            g->spec_prefix1_attn_state_kv[il] = NULL;
            g->spec_prefix1_attn_state_score[il] = NULL;
            g->spec_prefix1_index_state_kv[il] = NULL;
            g->spec_prefix1_index_state_score[il] = NULL;
            continue;
        }'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: removed non-existent fields from SSD streaming skip block')
else:
    print('NOT FOUND: trying alternate match...')
    # Try to find the block with the non-existent fields
    idx = content.find('g->layer_attn_state_kv_comp[il] = NULL;')
    if idx >= 0:
        # Find the start of the block
        start = content.rfind('if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU)', 0, idx)
        if start >= 0:
            end = content.find('continue;', idx) + len('continue;')
            end = content.find('\n', end) + 1
            print(f'Found block at {start}-{end}')
            # Replace everything from start to end
            content = content[:start] + new + content[end:]
            print('FIXED: replaced block')
        else:
            print('Could not find block start')
    else:
        print('Non-existent fields not found in file')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
