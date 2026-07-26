import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug to ds4_session_create to find exact failure point
old = '    if (!metal_graph_alloc_raw_cap(&s->graph, &e->weights, shape_layer,\n                                   raw_cap, (uint32_t)ctx_size, s->prefill_cap,\n                                   need_spec_verifier,\n                                   placement,\n                                   e->cuda_tensor_parallel,\n                                   shared_prefill_workspace))\n    {\n        free(s);\n        return 1;\n    }'
new = '    fprintf(stderr, "ds4: DEBUG calling metal_graph_alloc_raw_cap with placement=%p multi_tier=%d\\n", (void*)placement, e->multi_tier);\n    if (!metal_graph_alloc_raw_cap(&s->graph, &e->weights, shape_layer,\n                                   raw_cap, (uint32_t)ctx_size, s->prefill_cap,\n                                   need_spec_verifier,\n                                   placement,\n                                   e->cuda_tensor_parallel,\n                                   shared_prefill_workspace))\n    {\n        fprintf(stderr, "ds4: DEBUG metal_graph_alloc_raw_cap returned false\\n");\n        free(s);\n        return 1;\n    }\n    fprintf(stderr, "ds4: DEBUG metal_graph_alloc_raw_cap succeeded\\n");'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added debug to ds4_session_create')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
