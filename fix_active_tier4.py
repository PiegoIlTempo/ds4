import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: also call ds4_gpu_set_current_device to reset CUDA device to emb_tier
old = '''        /* SSD streaming + multi-tier: reset active_tier to emb_tier before embed */
        if (g->placement) g->active_tier = g->emb_tier;
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor active_tier=%d\\n", g->active_tier);'''

new = '''        /* SSD streaming + multi-tier: reset active_tier and CUDA device to emb_tier before embed */
        if (g->placement) {
            g->active_tier = g->emb_tier;
            ds4_gpu_set_current_device(g->emb_tier);
        }
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor active_tier=%d\\n", g->active_tier);'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: also call ds4_gpu_set_current_device before embed')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
