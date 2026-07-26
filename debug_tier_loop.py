import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug to per-tier scratch loop to find which tier causes the error
old = '    for (int t = 0; t < DS4_MAX_GPUS; t++) {\n        if (!used_tier[t]) continue;\n        g->cur_hc_by_tier[t] = ds4_gpu_tensor_alloc_ptr_on(t, hc_dim * sizeof(float));'
new = '    for (int t = 0; t < DS4_MAX_GPUS; t++) {\n        if (!used_tier[t]) continue;\n        fprintf(stderr, "ds4: DEBUG per-tier scratch loop t=%d\\n", t);\n        g->cur_hc_by_tier[t] = ds4_gpu_tensor_alloc_ptr_on(t, hc_dim * sizeof(float));'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added per-tier debug')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
