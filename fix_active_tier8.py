import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: use ds4_gpu_set_current_device (g_gpu is C++ static, not accessible from ds4.c)
old = '''        if (g->placement) {
            g->active_tier = g->emb_tier;
            cudaSetDevice(g_gpu[g->emb_tier].device_id);
        }'''

new = '''        if (g->placement) {
            g->active_tier = g->emb_tier;
            ds4_gpu_set_current_device(g->emb_tier);
        }'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: use ds4_gpu_set_current_device instead of cudaSetDevice')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
