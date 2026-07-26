import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: always reset active_tier to emb_tier before embed, not just when < 0
old = '''        /* SSD streaming + multi-tier: ensure active_tier is set to emb_tier */
        if (g->placement && g->active_tier < 0) g->active_tier = g->emb_tier;
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor active_tier=%d\\n", g->active_tier);'''

new = '''        /* SSD streaming + multi-tier: reset active_tier to emb_tier before embed */
        if (g->placement) g->active_tier = g->emb_tier;
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor active_tier=%d\\n", g->active_tier);'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: always reset active_tier to emb_tier before embed')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
