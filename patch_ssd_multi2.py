import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Replace the spill check: when ssd_streaming, just warn and continue (don't remap, don't refuse)
old = '''        if (spilled > 0) {
            if (e->ssd_streaming) {
                /* SSD streaming: remap CPU-spilled entries to GPU0.
                 * The SSD streaming path will load expert weights on demand,
                 * so we only need the graph scaffold on one device. */
                fprintf(stderr,
                        "ds4: SSD streaming active: remapping %d CPU-spilled "
                        "entries (%.2f GiB) to GPU0 for graph scaffold\\n",
                        spilled,
                        (double)spilled_bytes / (1024.0 * 1024.0 * 1024.0));
                for (int i = 0; i < e->n_placement_entries; i++) {
                    if (e->placement[i] == DS4_LAYER_PACK_CPU) {
                        e->placement[i] = 0;
                    }
                }
            } else {
                size_t total_budget = 0;
                for (int d = 0; d < e->gpu_cfg.n_gpus; d++) {
                    total_budget += e->gpu_cfg.vram_bytes[d];
                }
                if (have_entry_bytes) {
                    ds4_layer_pack_print(stderr,
                                         e->placement,
                                         e->n_placement_entries,
                                         DS4_N_LAYER,
                                         entry_bytes_buf,
                                         used_bytes,
                                         budget_bytes,
                                         e->gpu_cfg.n_gpus);
                }
                fprintf(stderr,
                        "ds4: per-tier graph scratch reserved on each GPU: "
                        "%.2f GiB (pre-subtracted from each --gpu-vram budget "
                        "before packing).\\n",
                        (double)engine_per_tier_graph_overhead_bytes(e) /
                            (1024.0 * 1024.0 * 1024.0));
                fprintf(stderr,
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
                return 1;
            }
        }'''

new = '''        if (spilled > 0) {
            if (e->ssd_streaming) {
                /* SSD streaming: CPU-spilled entries are expected.
                 * The SSD streaming path loads expert weights on demand,
                 * so we don't need full VRAM residency. */
                fprintf(stderr,
                        "ds4: SSD streaming active: %d entries (%.2f GiB) "
                        "will be demand-loaded from SSD\\n",
                        spilled,
                        (double)spilled_bytes / (1024.0 * 1024.0 * 1024.0));
            } else {
                size_t total_budget = 0;
                for (int d = 0; d < e->gpu_cfg.n_gpus; d++) {
                    total_budget += e->gpu_cfg.vram_bytes[d];
                }
                if (have_entry_bytes) {
                    ds4_layer_pack_print(stderr,
                                         e->placement,
                                         e->n_placement_entries,
                                         DS4_N_LAYER,
                                         entry_bytes_buf,
                                         used_bytes,
                                         budget_bytes,
                                         e->gpu_cfg.n_gpus);
                }
                fprintf(stderr,
                        "ds4: per-tier graph scratch reserved on each GPU: "
                        "%.2f GiB (pre-subtracted from each --gpu-vram budget "
                        "before packing).\\n",
                        (double)engine_per_tier_graph_overhead_bytes(e) /
                            (1024.0 * 1024.0 * 1024.0));
                fprintf(stderr,
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
                return 1;
            }
        }'''

if old in content:
    content = content.replace(old, new, 1)
    print('PATCH: updated spill check for ssd+multi (no remap, no refuse)')
else:
    print('PATCH: OLD STRING NOT FOUND')
    # Try to find what's actually there
    import re
    m = re.search(r'if \(spilled > 0\) \{.*?ds4_engine_close\(e\);\s+\*out = NULL;\s+return 1;\s+\}', content, re.DOTALL)
    if m:
        print(f'Found spill block at offset {m.start()}')
        print(repr(m.group()[:200]))
    sys.exit(1)

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
