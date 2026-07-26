import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: save and restore g->ssd_streaming around memset in metal_graph_alloc_raw_cap
old = '    const int saved_dspark_exec_tier = g->dspark_exec_tier;\n    memset(g, 0, sizeof(*g));\n    g->dspark_exec_tier = saved_dspark_exec_tier;'
new = '    const int saved_dspark_exec_tier = g->dspark_exec_tier;\n    const bool saved_ssd_streaming = g->ssd_streaming;\n    memset(g, 0, sizeof(*g));\n    g->dspark_exec_tier = saved_dspark_exec_tier;\n    g->ssd_streaming = saved_ssd_streaming;'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: saved and restored g->ssd_streaming around memset')
else:
    print('NOT FOUND: memset in metal_graph_alloc_raw_cap')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
