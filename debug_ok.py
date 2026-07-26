import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug before the final ok check
old = '''    const bool ok = state_init_ok && layer_cache_ok && class_p_ok &&'''

new = '''    fprintf(stderr, "ds4: DEBUG ok check: state_init_ok=%d layer_cache_ok=%d class_p_ok=%d\\n",
            state_init_ok, layer_cache_ok, class_p_ok);
    const bool ok = state_init_ok && layer_cache_ok && class_p_ok &&'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: ok check debug')
else:
    print('NOT FOUND: ok check')

# Add debug for metal_graph_output_pre etc
old2 = '''                    metal_graph_output_pre(g) && metal_graph_output_weights(g) &&'''
new2 = '''                    fprintf(stderr, "ds4: DEBUG calling metal_graph_output_pre\\n"),
                    metal_graph_output_pre(g) && metal_graph_output_weights(g) &&'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: output_pre debug')
else:
    print('NOT FOUND: output_pre')

# Add debug for metal_graph_logits
old3 = '''                    metal_graph_logits(g) && output_tp_ok &&'''
new3 = '''                    fprintf(stderr, "ds4: DEBUG calling metal_graph_logits\\n"),
                    metal_graph_logits(g) && output_tp_ok &&'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('FIXED: logits debug')
else:
    print('NOT FOUND: logits')

# Add debug for metal_graph_prefill_tokens
old4 = '''                    metal_graph_prefill_tokens(g) &&'''
new4 = '''                    fprintf(stderr, "ds4: DEBUG calling metal_graph_prefill_tokens\\n"),
                    metal_graph_prefill_tokens(g) &&'''

if old4 in content:
    content = content.replace(old4, new4, 1)
    print('FIXED: prefill_tokens debug')
else:
    print('NOT FOUND: prefill_tokens')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
