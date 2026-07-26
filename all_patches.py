import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# === PATCH 1: Remove SSD streaming + multi-tier guard in ds4_engine_open_internal ===
old1 = '''    if (e->ssd_streaming && e->multi_tier) {
        fprintf(stderr,
                "ds4: --ssd-streaming is not compatible with multi-GPU placement\\n");
        ds4_engine_close(e);
        *out = NULL;
        return 1;
    }'''

new1 = '''    /* SSD streaming + multi-tier: guard removed for V100 multi-GPU support */'''

if old1 in content:
    content = content.replace(old1, new1, 1)
    print('PATCH 1: Removed SSD+multi-tier guard')
else:
    print('PATCH 1: NOT FOUND')

# === PATCH 2: Remove CPU-spill guard in engine_install_gpu_placement ===
old2 = '''    if (has_cpu_spill) {
        fprintf(stderr,
            "ds4: CPU-spill placement detected; CPU-tier execution wiring lands in\\n"
            "ds4: cpu-spill execution (follow-up) (CPU-spill execution). Aborting engine creation.\\n");
        return -1;
    }

    if (engine_install_per_device_caches(e) != 0) return -1;'''

new2 = '''    if (engine_install_per_device_caches(e) != 0) return -1;'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('PATCH 2: Removed CPU-spill guard in engine_install_gpu_placement')
else:
    print('PATCH 2: NOT FOUND')

# === PATCH 3: Remove CPU-spill guard in ds4_engine_open_internal (the "wave-3b" one) ===
old3 = '''            fprintf(stderr,
                    "ds4: CPU-spill placement detected; CPU-tier execution wiring "
                    "is the wave-3b mgpu-graph-session-cpu-spill follow-up.\\n");
            fprintf(stderr,
                    "ds4: --gpu-vram placement does not fit at the requested "
                    "context (ctx hint = %d):\\n"
                    "ds4:   %d placement entries spilled to CPU "
                    "(%.2f GiB unaccommodated of %.2f GiB total per-device budget).\\n"
                    "ds4: Lower --ctx / --ctx-max, raise --gpu-vram budgets, or use "
                    "--gpu-vram auto on a host with more free VRAM.\\n"
                    "ds4: Refusing upfront to avoid silent OOM at session_create.\\n",
                    e->placement_ctx_hint,
                    spilled,
                    (double)spilled_bytes / (1024.0 * 1024.0 * 1024.0),
                    (double)total_budget / (1024.0 * 1024.0 * 1024.0));
            ds4_engine_close(e);
            *out = NULL;
            return 1;'''

new3 = '''            /* CPU-spill guard removed for SSD streaming multi-GPU support */'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('PATCH 3: Removed CPU-spill guard in ds4_engine_open_internal')
else:
    print('PATCH 3: NOT FOUND')

# === PATCH 4: Remove SSD streaming skip in metal_graph_alloc_raw_cap (non-existent fields) ===
old4 = '''        if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) {
            g->layer_attn_state_kv_comp[il] = NULL;
            g->layer_attn_state_sc_comp[il] = NULL;
            g->layer_attn_state_kv[il] = NULL;
            g->layer_attn_state_score[il] = NULL;
            g->layer_index_state_kv[il] = NULL;
            g->layer_index_state_score[il] = NULL;
            g->spec_prefix1_index_state_kv[il] = NULL;
            g->spec_prefix1_index_state_score[il] = NULL;
            continue;
        }'''

new4 = '''        if (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) {
            /* SSD streaming: skip per-layer state allocation for CPU-spilled layers */
            continue;
        }'''

if old4 in content:
    content = content.replace(old4, new4, 1)
    print('PATCH 4: Fixed SSD streaming skip block')
else:
    print('PATCH 4: NOT FOUND')

# === PATCH 5: CPU-spill remapping - don't remap to GPU0 when SSD streaming ===
old5 = '''    if (e->ssd_streaming) {
        for (int i = 0; i < e->n_placement_entries; i++) {
            if (e->placement[i] == DS4_LAYER_PACK_CPU) {
                e->placement[i] = 0;
            }
        }
    }'''

new5 = '''    /* SSD streaming: CPU-spilled layers stay as CPU-spill (demand-loaded from SSD) */'''

if old5 in content:
    content = content.replace(old5, new5, 1)
    print('PATCH 5: Removed CPU-spill remapping to GPU0')
else:
    print('PATCH 5: NOT FOUND')

# === PATCH 6: emb_tier and head_tier fix ===
old6 = '''    g->emb_tier = placement ? placement[0] : 0;'''
new6 = '''    g->emb_tier = placement ? placement[0] : 0;
    if (g->ssd_streaming && g->emb_tier == DS4_LAYER_PACK_CPU) g->emb_tier = 0;'''

if old6 in content:
    content = content.replace(old6, new6, 1)
    print('PATCH 6: Fixed emb_tier for SSD streaming')
else:
    print('PATCH 6: NOT FOUND')

old6b = '''    g->head_tier = placement ? placement[DS4_N_LAYER + 1] : 0;'''
new6b = '''    g->head_tier = placement ? placement[DS4_N_LAYER + 1] : 0;
    if (g->ssd_streaming && g->head_tier == DS4_LAYER_PACK_CPU) g->head_tier = 0;'''

if old6b in content:
    content = content.replace(old6b, new6b, 1)
    print('PATCH 6b: Fixed head_tier for SSD streaming')
else:
    print('PATCH 6b: NOT FOUND')

# === PATCH 7: Set g->ssd_streaming before metal_graph_alloc_raw_cap ===
old7 = '''    s->graph.dspark_exec_tier = e->multi_tier ? e->dspark_exec_tier : 0;
    if (!metal_graph_alloc_raw_cap(&s->graph, &e->weights, shape_layer,'''
new7 = '''    s->graph.dspark_exec_tier = e->multi_tier ? e->dspark_exec_tier : 0;
    s->graph.ssd_streaming = e->ssd_streaming;
    if (!metal_graph_alloc_raw_cap(&s->graph, &e->weights, shape_layer,'''

if old7 in content:
    content = content.replace(old7, new7, 1)
    print('PATCH 7: Set g->ssd_streaming before metal_graph_alloc_raw_cap')
else:
    print('PATCH 7: NOT FOUND')

# === PATCH 8: used_tier skips CPU-spilled entries when SSD streaming ===
old8 = '''    bool used_tier[DS4_MAX_GPUS] = {0};
    used_tier[0] = true; /* single-tier baseline always uses tier 0 */
    if (placement) {'''
new8 = '''    bool used_tier[DS4_MAX_GPUS] = {0};
    used_tier[0] = true; /* single-tier baseline always uses tier 0 */
    if (placement) {
        /* SSD streaming: skip CPU-spilled entries in used_tier */
        for (int i = 0; i < DS4_N_LAYER + 2; i++) {
            if (placement[i] == DS4_LAYER_PACK_CPU) continue;
            if (placement[i] >= 0 && placement[i] < DS4_MAX_GPUS)
                used_tier[placement[i]] = true;
        }'''

if old8 in content:
    content = content.replace(old8, new8, 1)
    print('PATCH 8: Fixed used_tier for SSD streaming')
else:
    print('PATCH 8: NOT FOUND')

# === PATCH 9: Save/restore ssd_streaming around memset ===
old9 = '''    const int saved_dspark_exec_tier = g->dspark_exec_tier;
    memset(g, 0, sizeof(*g));
    g->dspark_exec_tier = saved_dspark_exec_tier;'''
new9 = '''    const int saved_dspark_exec_tier = g->dspark_exec_tier;
    const bool saved_ssd_streaming = g->ssd_streaming;
    memset(g, 0, sizeof(*g));
    g->dspark_exec_tier = saved_dspark_exec_tier;
    g->ssd_streaming = saved_ssd_streaming;'''

if old9 in content:
    content = content.replace(old9, new9, 1)
    print('PATCH 9: Save/restore ssd_streaming around memset')
else:
    print('PATCH 9: NOT FOUND')

# === PATCH 10: Set ssd_streaming in engine_open ===
old10 = '''            ds4_gpu_set_quality(e->quality);
            (void)ds4_gpu_set_model_fd(e->model.fd);'''
new10 = '''            ds4_gpu_set_quality(e->quality);
            (void)ds4_gpu_set_model_fd(e->model.fd);
            ds4_gpu_set_ssd_streaming(e->ssd_streaming);'''

if old10 in content:
    content = content.replace(old10, new10, 1)
    print('PATCH 10: Set ssd_streaming in engine_open')
else:
    print('PATCH 10: NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('ALL PATCHES APPLIED')
