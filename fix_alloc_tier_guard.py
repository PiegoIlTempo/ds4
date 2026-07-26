import sys

with open('ds4.c', 'r') as f:
    content = f.read()

# Fix: remove ssd_streaming guard from alloc_tier
old = '        const int alloc_tier = (g->ssd_streaming && layer_tier == DS4_LAYER_PACK_CPU) ? g->head_tier : layer_tier;'
new = '        const int alloc_tier = (layer_tier == DS4_LAYER_PACK_CPU) ? g->head_tier : layer_tier;'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: alloc_tier no longer requires ssd_streaming')
else:
    print('NOT FOUND')

with open('ds4.c', 'w') as f:
    f.write(content)
print('DONE')
