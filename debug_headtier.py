import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug print before head_tier fix
old = '    g->head_tier = placement ? placement[DS4_N_LAYER + 1] : 0;\n    if (g->ssd_streaming && g->head_tier == DS4_LAYER_PACK_CPU) g->head_tier = 0;'
new = '    g->head_tier = placement ? placement[DS4_N_LAYER + 1] : 0;\n    fprintf(stderr, "ds4: DEBUG head_tier=%d ssd_streaming=%d placement=%p\\n", g->head_tier, g->ssd_streaming, (void*)placement);\n    if (g->ssd_streaming && g->head_tier == DS4_LAYER_PACK_CPU) g->head_tier = 0;'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added head_tier debug')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
