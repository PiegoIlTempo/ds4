import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: set g->ssd_streaming before metal_graph_alloc_raw_cap in session creation
old = '    s->graph.dspark_exec_tier = e->multi_tier ? e->dspark_exec_tier : 0;\n    if (!metal_graph_alloc_raw_cap(&s->graph, &e->weights, shape_layer,'
new = '    s->graph.dspark_exec_tier = e->multi_tier ? e->dspark_exec_tier : 0;\n    s->graph.ssd_streaming = e->ssd_streaming;\n    if (!metal_graph_alloc_raw_cap(&s->graph, &e->weights, shape_layer,'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: set g->ssd_streaming before metal_graph_alloc_raw_cap in session creation')
else:
    print('NOT FOUND: session creation path')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
