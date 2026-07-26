import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# 1. Add ds4_gpu_set_ssd_streaming in the multi-tier path
old1 = '''            e->metal_ready = true;
            ds4_gpu_set_quality(e->quality);
            (void)ds4_gpu_set_model_fd(e->model.fd);

            if (engine_install_gpu_placement(e) != 0) {'''

new1 = '''            e->metal_ready = true;
            ds4_gpu_set_quality(e->quality);
            (void)ds4_gpu_set_model_fd(e->model.fd);
            ds4_gpu_set_ssd_streaming(e->ssd_streaming);

            if (engine_install_gpu_placement(e) != 0) {'''

if old1 in content:
    content = content.replace(old1, new1, 1)
    print('PATCH 1: added ds4_gpu_set_ssd_streaming in multi-tier path')
else:
    print('PATCH 1: NOT FOUND')

# 2. In engine_install_gpu_placement, don't remap CPU-spilled entries, just warn
old2 = '''    if (has_cpu_spill) {
        if (e->ssd_streaming) {
            /* SSD streaming: remap CPU-spilled entries to GPU0.
             * The per-device cache is skipped when SSD streaming is active,
             * so this won't trigger a large VRAM allocation. */
            fprintf(stderr,
                    "ds4: SSD streaming active: remapping %d CPU-spilled "
                    "entries to GPU0 for graph scaffold\\n",
                    has_cpu_spill);
            for (int i = 0; i < e->n_placement_entries; i++) {
                if (e->placement[i] == DS4_LAYER_PACK_CPU) {
                    e->placement[i] = 0;
                }
            }
        } else {'''

new2 = '''    if (has_cpu_spill) {
        if (e->ssd_streaming) {
            /* SSD streaming: keep CPU-spilled entries as-is.
             * The graph allocator will skip per-layer scratch allocation
             * for these layers, and weights will be loaded on demand. */
            fprintf(stderr,
                    "ds4: SSD streaming active: %d CPU-spilled entries "
                    "will be demand-loaded from SSD\\n",
                    has_cpu_spill);
        } else {'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('PATCH 2: no longer remap CPU-spilled entries in engine_install_gpu_placement')
else:
    print('PATCH 2: NOT FOUND')

# 3. In metal_graph_alloc_raw_cap, skip per-layer allocations for CPU-spilled layers when SSD streaming
old3 = '''        const int layer_tier = placement ? placement[il + 1] : 0;
        g->layer_raw_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                managed_kv_cache,
                layer_tier,
                (uint64_t)raw_cap * DS4_N_HEAD_DIM * sizeof(float));
        const int layer_tp_partner = g->cuda_tp_attn_cache_dup
            ? metal_graph_cuda_tp_partner_tier(layer_tier) : -1;
        if (layer_tp_partner >= 0) {
            g->layer_raw_cache_tp[il] = metal_graph_alloc_kv_cache_tensor_on(
                    managed_kv_cache,
                    layer_tp_partner,
                    (uint64_t)raw_cap * DS4_N_HEAD_DIM * sizeof(float));
        }
        const uint32_t ratio = ds4_layer_compress_ratio(il);
        if (ratio != 0) {
            const uint32_t coff = ratio == 4 ? 2u : 1u;
            const uint64_t attn_width = (uint64_t)coff * DS4_N_HEAD_DIM;
            const uint64_t attn_rows = (uint64_t)coff * ratio;
            g->layer_attn_comp_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                    managed_kv_cache,
                    layer_tier,
                    (uint64_t)g->layer_comp_cap[il] * DS4_N_HEAD_DIM *
                    (DS4_GPU_ATTN_COMP_CACHE_F16 ? sizeof(uint16_t) : sizeof(float)));
            if (layer_tp_partner >= 0) {
                g->layer_attn_comp_cache_tp[il] = metal_graph_alloc_kv_cache_tensor_on(
                        managed_kv_cache,
                        layer_tp_partner,
                        (uint64_t)g->layer_comp_cap[il] * DS4_N_HEAD_DIM *
                        (DS4_GPU_ATTN_COMP_CACHE_F16 ? sizeof(uint16_t) : sizeof(float)));
            }
            g->layer_attn_state_kv[il] = ds4_gpu_tensor_alloc_ptr_on(layer_tier, attn_width * attn_rows * sizeof(float));
            g->layer_attn_state_score[il] = ds4_gpu_tensor_alloc_ptr_on(layer_tier, attn_width * attn_rows * sizeof(float));
            if (enable_frontier_snapshot) {'''

new3 = '''        const int layer_tier = placement ? placement[il + 1] : 0;
        if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) {
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
        }
        g->layer_raw_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                managed_kv_cache,
                layer_tier,
                (uint64_t)raw_cap * DS4_N_HEAD_DIM * sizeof(float));
        const int layer_tp_partner = g->cuda_tp_attn_cache_dup
            ? metal_graph_cuda_tp_partner_tier(layer_tier) : -1;
        if (layer_tp_partner >= 0) {
            g->layer_raw_cache_tp[il] = metal_graph_alloc_kv_cache_tensor_on(
                    managed_kv_cache,
                    layer_tp_partner,
                    (uint64_t)raw_cap * DS4_N_HEAD_DIM * sizeof(float));
        }
        const uint32_t ratio = ds4_layer_compress_ratio(il);
        if (ratio != 0) {
            const uint32_t coff = ratio == 4 ? 2u : 1u;
            const uint64_t attn_width = (uint64_t)coff * DS4_N_HEAD_DIM;
            const uint64_t attn_rows = (uint64_t)coff * ratio;
            g->layer_attn_comp_cache[il] = metal_graph_alloc_kv_cache_tensor_on(
                    managed_kv_cache,
                    layer_tier,
                    (uint64_t)g->layer_comp_cap[il] * DS4_N_HEAD_DIM *
                    (DS4_GPU_ATTN_COMP_CACHE_F16 ? sizeof(uint16_t) : sizeof(float)));
            if (layer_tp_partner >= 0) {
                g->layer_attn_comp_cache_tp[il] = metal_graph_alloc_kv_cache_tensor_on(
                        managed_kv_cache,
                        layer_tp_partner,
                        (uint64_t)g->layer_comp_cap[il] * DS4_N_HEAD_DIM *
                        (DS4_GPU_ATTN_COMP_CACHE_F16 ? sizeof(uint16_t) : sizeof(float)));
            }
            g->layer_attn_state_kv[il] = ds4_gpu_tensor_alloc_ptr_on(layer_tier, attn_width * attn_rows * sizeof(float));
            g->layer_attn_state_score[il] = ds4_gpu_tensor_alloc_ptr_on(layer_tier, attn_width * attn_rows * sizeof(float));
            if (enable_frontier_snapshot) {'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('PATCH 3: skip per-layer allocations for CPU-spilled layers in metal_graph_alloc_raw_cap')
else:
    print('PATCH 3: NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
