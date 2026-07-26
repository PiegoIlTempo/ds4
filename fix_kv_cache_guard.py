import sys

with open('ds4.c', 'r') as f:
    content = f.read()

# Fix: remove ssd_streaming guard from KV cache allocation for CPU-spilled layers
old = '        /* SSD streaming: allocate KV cache for CPU-spilled layers on head_tier */\n        if (g->ssd_streaming && placement && placement[il + 1] == DS4_LAYER_PACK_CPU) {'
new = '        /* Allocate KV cache for CPU-spilled layers on head_tier */\n        if (placement && placement[il + 1] == DS4_LAYER_PACK_CPU) {'

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: KV cache CPU-spill allocation no longer requires ssd_streaming')
else:
    print('NOT FOUND')

with open('ds4.c', 'w') as f:
    f.write(content)
print('DONE')
