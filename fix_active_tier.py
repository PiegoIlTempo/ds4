import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: set active_tier to emb_tier before embed in streaming path
old = '''    fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor\\n");
    if (ok) {
        ok = ds4_gpu_embed_token_hc_tensor(metal_graph_cur_hc(g),'''

new = '''    fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor\\n");
    if (ok) {
        /* SSD streaming + multi-tier: ensure active_tier is set to emb_tier */
        if (g->placement && g->active_tier < 0) {
            g->active_tier = g->emb_tier;
        }
        ok = ds4_gpu_embed_token_hc_tensor(metal_graph_cur_hc(g),'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: set active_tier before embed')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
