import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug to output head allocations
old = '    g->output_pre_by_tier[g->head_tier] =\n        ds4_gpu_tensor_alloc_ptr_on(g->head_tier, (uint64_t)DS4_N_HC * sizeof(float));'
new = '    fprintf(stderr, "ds4: DEBUG output_pre_by_tier head_tier=%d\\n", g->head_tier);\n    g->output_pre_by_tier[g->head_tier] =\n        ds4_gpu_tensor_alloc_ptr_on(g->head_tier, (uint64_t)DS4_N_HC * sizeof(float));'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added output_pre debug')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
