import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add progressive debug markers after the per-tier scratch loop
# Find the section after "per-tier scratch loop done"
old = '''    fprintf(stderr, "ds4: DEBUG per-tier scratch loop done\\n");
    /* Class H — head_tier captured from placement[DS4_N_LAYER + 1]'''

new = '''    fprintf(stderr, "ds4: DEBUG per-tier scratch loop done\\n");
    fprintf(stderr, "ds4: DEBUG step H (head_tier)\\n");
    /* Class H — head_tier captured from placement[DS4_N_LAYER + 1]'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: step H debug')
else:
    print('NOT FOUND: step H')

# Add debug before output_pre_by_tier
old2 = '''    g->output_pre_by_tier[g->head_tier] =
        ds4_gpu_tensor_alloc_ptr_on(g->head_tier, (uint64_t)DS4_N_HC * sizeof(float));'''

new2 = '''    fprintf(stderr, "ds4: DEBUG step output_pre head_tier=%d\\n", g->head_tier);
    g->output_pre_by_tier[g->head_tier] =
        ds4_gpu_tensor_alloc_ptr_on(g->head_tier, (uint64_t)DS4_N_HC * sizeof(float));'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: output_pre debug')
else:
    print('NOT FOUND: output_pre')

# Add debug before emb_tier
old3 = '''    /* Class E — emb_tier captured from placement[0] (or 0 in
     * single-tier / diagnostic paths). _ptr_on(0, ...) short-circuits to the
     * legacy ds4_gpu_tensor_alloc when g_n_gpus <= 1 — byte-equivalent. */
    g->emb_tier = placement ? placement[0] : 0;'''

new3 = '''    fprintf(stderr, "ds4: DEBUG step E (emb_tier)\\n");
    /* Class E — emb_tier captured from placement[0] (or 0 in
     * single-tier / diagnostic paths). _ptr_on(0, ...) short-circuits to the
     * legacy ds4_gpu_tensor_alloc when g_n_gpus <= 1 — byte-equivalent. */
    g->emb_tier = placement ? placement[0] : 0;'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('FIXED: emb_tier debug')
else:
    print('NOT FOUND: emb_tier')

# Add debug before per-layer loop
old4 = '''    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        /* per-layer Class L allocations land on the layer's
         * home tier. placement is NULL on single-tier / diagnostic paths
         * (all-tier-0); non-NULL on the engine path that opted into
         * multi-tier. layer_tier == 0 in single-tier mode is the
         * byte-equivalent path through metal_graph_alloc_kv_cache_tensor_on
         * and ds4_gpu_tensor_alloc_ptr_on. */
        const int layer_tier = placement ? placement[il + 1] : 0;
        /* SSD streaming: skip per-layer allocations for CPU-spilled layers */
        if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) continue;'''

new4 = '''    fprintf(stderr, "ds4: DEBUG step L (per-layer loop start)\\n");
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        /* per-layer Class L allocations land on the layer's
         * home tier. placement is NULL on single-tier / diagnostic paths
         * (all-tier-0); non-NULL on the engine path that opted into
         * multi-tier. layer_tier == 0 in single-tier mode is the
         * byte-equivalent path through metal_graph_alloc_kv_cache_tensor_on
         * and ds4_gpu_tensor_alloc_ptr_on. */
        const int layer_tier = placement ? placement[il + 1] : 0;
        /* SSD streaming: skip per-layer allocations for CPU-spilled layers */
        if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) continue;'''

if old4 in content:
    content = content.replace(old4, new4, 1)
    print('FIXED: per-layer loop debug')
else:
    print('NOT FOUND: per-layer loop')

# Add debug after per-layer loop
old5 = '''    bool state_init_ok = true;
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {'''

new5 = '''    fprintf(stderr, "ds4: DEBUG step L done, state_init\\n");
    bool state_init_ok = true;
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {'''

if old5 in content:
    content = content.replace(old5, new5, 1)
    print('FIXED: state_init debug')
else:
    print('NOT FOUND: state_init')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
