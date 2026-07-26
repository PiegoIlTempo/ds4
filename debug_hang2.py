import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug at start of metal_graph_alloc_raw_cap - right after memset restore
old = '    g->ssd_streaming = saved_ssd_streaming;\n    g->owns_prefill_workspace = shared_prefill_workspace == NULL;'
new = '    g->ssd_streaming = saved_ssd_streaming;\n    fprintf(stderr, "ds4: DEBUG metal_graph_alloc_raw_cap start\\n");\n    g->owns_prefill_workspace = shared_prefill_workspace == NULL;'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added start debug')
else:
    print('NOT FOUND')

# Add debug before per-tier scratch loop
old2 = '    /* Class B — per-tier scratch buffers */\n    for (int t = 0; t < DS4_MAX_GPUS; t++) {\n        if (!used_tier[t]) continue;'
new2 = '    /* Class B — per-tier scratch buffers */\n    fprintf(stderr, "ds4: DEBUG per-tier scratch loop start\\n");\n    for (int t = 0; t < DS4_MAX_GPUS; t++) {\n        if (!used_tier[t]) continue;'

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: added per-tier loop debug')
else:
    print('NOT FOUND')

# Add debug after per-tier scratch loop, before head_tier
old3 = '    /* Class H — head_tier captured from placement[DS4_N_LAYER + 1]'
new3 = '    fprintf(stderr, "ds4: DEBUG per-tier scratch loop done\\n");\n    /* Class H — head_tier captured from placement[DS4_N_LAYER + 1]'

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('FIXED: added post-loop debug')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
