import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: set active_tier AND call cudaSetDevice directly before embed
old = '''    if (ok) {
        /* SSD streaming + multi-tier: reset CUDA device to emb_tier before embed.
         * Do NOT set g->active_tier here — metal_graph_set_active_tier_decode
         * uses active_tier to detect device changes and would skip cudaSetDevice
         * if active_tier already matches the target tier. */
        if (g->placement) {
            ds4_gpu_set_current_device(g->emb_tier);
        }
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor active_tier=%d\\n", g->active_tier);
        ok = ds4_gpu_embed_token_hc_tensor(metal_graph_cur_hc(g),'''

new = '''    if (ok) {
        /* SSD streaming + multi-tier: set active_tier to emb_tier and switch
         * CUDA device before embed. metal_graph_cur_hc() uses active_tier to
         * index cur_hc_by_tier[], so it must be valid. Call cudaSetDevice
         * directly to force the device switch regardless of active_tier. */
        if (g->placement) {
            g->active_tier = g->emb_tier;
            cudaSetDevice(g_gpu[g->emb_tier].device_id);
        }
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor active_tier=%d\\n", g->active_tier);
        ok = ds4_gpu_embed_token_hc_tensor(metal_graph_cur_hc(g),'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: set active_tier + cudaSetDevice before embed')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
