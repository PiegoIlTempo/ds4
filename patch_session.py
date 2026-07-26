import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Find the point after GLM block and before metal_graph_alloc_raw_cap
# Insert a check: if coordinator, skip graph allocation
old = '    s->prefill_cap = metal_graph_prefill_cap_for_prompt(ctx_size,\n                                                        e->prefill_chunk);\n    const uint32_t raw_cap = metal_graph_raw_cap_for_context(ctx_size, s->prefill_cap);\n    const ds4_layer_weights *shape_layer = weights_first_bound_layer(&e->weights);'

new = '    if (e->distributed.role == DS4_DISTRIBUTED_COORDINATOR) {\n        /* Coordinator: skip full graph allocation, only create distributed session */\n        s->logits = xmalloc((size_t)DS4_N_VOCAB * sizeof(s->logits[0]));\n        s->sample_probs = xmalloc((size_t)DS4_N_VOCAB * sizeof(s->sample_probs[0]));\n        char err[256];\n        if (ds4_dist_session_create(&s->distributed,\n                                    e,\n                                    &e->distributed,\n                                    s,\n                                    ctx_size,\n                                    err,\n                                    sizeof(err)) != 0) {\n            fprintf(stderr,\n                    "ds4: failed to create distributed coordinator session: %s\\n",\n                    err[0] ? err : "unknown error");\n            free(s->logits);\n            free(s->sample_probs);\n            free(s);\n            return 1;\n        }\n        if (!ds4_session_tp_register(s)) {\n            ds4_session_free(s);\n            return 1;\n        }\n        *out = s;\n        return 0;\n    }\n    s->prefill_cap = metal_graph_prefill_cap_for_prompt(ctx_size,\n                                                        e->prefill_chunk);\n    const uint32_t raw_cap = metal_graph_raw_cap_for_context(ctx_size, s->prefill_cap);\n    const ds4_layer_weights *shape_layer = weights_first_bound_layer(&e->weights);'

if old in content:
    content = content.replace(old, new, 1)
    with open(sys.argv[1], 'w') as f:
        f.write(content)
    print('OK')
else:
    print('NOT FOUND')
    sys.exit(1)
