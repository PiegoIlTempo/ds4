import sys

with open('ds4.c', 'r') as f:
    content = f.read()

# Fix: remove ssd_streaming guard from head_tier and emb_tier fallback
old = '''    g->head_tier = placement ? placement[DS4_N_LAYER + 1] : 0;
    if (g->ssd_streaming && g->head_tier == DS4_LAYER_PACK_CPU) g->head_tier = 0;
    if (g->ssd_streaming && g->head_tier == DS4_LAYER_PACK_CPU) g->head_tier = 0;'''

new = '''    g->head_tier = placement ? placement[DS4_N_LAYER + 1] : 0;
    if (g->head_tier == DS4_LAYER_PACK_CPU) g->head_tier = 0;'''

old2 = '''    g->emb_tier = placement ? placement[0] : 0;
    if (g->ssd_streaming && g->emb_tier == DS4_LAYER_PACK_CPU) g->emb_tier = 0;
    if (g->ssd_streaming && g->emb_tier == DS4_LAYER_PACK_CPU) g->emb_tier = 0;'''

new2 = '''    g->emb_tier = placement ? placement[0] : 0;
    if (g->emb_tier == DS4_LAYER_PACK_CPU) g->emb_tier = 0;'''

count = 0
if old in content:
    content = content.replace(old, new, 1)
    count += 1
    print('FIXED: head_tier fallback no longer requires ssd_streaming')
else:
    print('NOT FOUND: head_tier block')

if old2 in content:
    content = content.replace(old2, new2, 1)
    count += 1
    print('FIXED: emb_tier fallback no longer requires ssd_streaming')
else:
    print('NOT FOUND: emb_tier block')

with open('ds4.c', 'w') as f:
    f.write(content)
print(f'DONE: {count} patches applied')
