import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug before shared_prefill_workspace check
old = '''    /* Class P chunked-prefill batch scratch — replicated across
     * every used tier. The cur/next pair (batch_cur_hc / batch_next_hc) is
     * ping-ponged per layer step on each tier; tier transitions copy via
     * ds4_gpu_tensor_copy_xdev (handled in B6). batch_ffn_out is lazily
     * allocated by metal_graph_ensure_batch_ffn_out (per-tier on first touch)
     * and included in the CUDA scratch estimate because TP prefill can use it
     * as the combined routed+shared FFN buffer. */
    if (shared_prefill_workspace) {'''

new = '''    fprintf(stderr, "ds4: DEBUG step shared_prefill_workspace check\\n");
    /* Class P chunked-prefill batch scratch — replicated across
     * every used tier. The cur/next pair (batch_cur_hc / batch_next_hc) is
     * ping-ponged per layer step on each tier; tier transitions copy via
     * ds4_gpu_tensor_copy_xdev (handled in B6). batch_ffn_out is lazily
     * allocated by metal_graph_ensure_batch_ffn_out (per-tier on first touch)
     * and included in the CUDA scratch estimate because TP prefill can use it
     * as the combined routed+shared FFN buffer. */
    if (shared_prefill_workspace) {'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: shared_prefill debug')
else:
    print('NOT FOUND: shared_prefill')

# Add debug before the batch scratch loop
old2 = '''    } else {
        g->prefill_tokens_by_tier[g->emb_tier] =
            ds4_gpu_tensor_alloc_ptr_on(g->emb_tier, pc * sizeof(int32_t));
        for (int t = 0; t < DS4_MAX_GPUS; t++) {
            if (!used_tier[t]) continue;'''

new2 = '''    } else {
        fprintf(stderr, "ds4: DEBUG step batch scratch alloc\\n");
        g->prefill_tokens_by_tier[g->emb_tier] =
            ds4_gpu_tensor_alloc_ptr_on(g->emb_tier, pc * sizeof(int32_t));
        for (int t = 0; t < DS4_MAX_GPUS; t++) {
            if (!used_tier[t]) continue;'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: batch scratch debug')
else:
    print('NOT FOUND: batch scratch')

# Add debug before return true
old3 = '''    g->ssd_streaming_cold = false;
    return true;'''

new3 = '''    g->ssd_streaming_cold = false;
    fprintf(stderr, "ds4: DEBUG metal_graph_alloc_raw_cap returning true\\n");
    return true;'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('FIXED: return true debug')
else:
    print('NOT FOUND: return true')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
