import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: when SSD streaming is active, map CPU-spilled emb_tier and head_tier to GPU0
old = '    g->emb_tier = placement ? placement[0] : 0;'
new = '    g->emb_tier = placement ? placement[0] : 0;\n    if (g->ssd_streaming && g->emb_tier == DS4_LAYER_PACK_CPU) g->emb_tier = 0;'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: emb_tier mapped to GPU0 when SSD streaming')
else:
    print('NOT FOUND: emb_tier')

old2 = '    g->head_tier = placement ? placement[DS4_N_LAYER + 1] : 0;'
new2 = '    g->head_tier = placement ? placement[DS4_N_LAYER + 1] : 0;\n    if (g->ssd_streaming && g->head_tier == DS4_LAYER_PACK_CPU) g->head_tier = 0;'

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: head_tier mapped to GPU0 when SSD streaming')
else:
    print('NOT FOUND: head_tier')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
