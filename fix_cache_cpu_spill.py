import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: cache CPU-spilled tensors on head_tier when SSD streaming is active
old = '''        int logical_tier = e->placement[entry];
        if (logical_tier == DS4_LAYER_PACK_CPU) continue;        /* CPU spill: skip here. */'''

new = '''        int logical_tier = e->placement[entry];
        if (logical_tier == DS4_LAYER_PACK_CPU) {
            /* SSD streaming: cache CPU-spilled tensors on the head tier
             * so the output head pipeline can access them. */
            if (e->ssd_streaming) {
                logical_tier = e->placement[e->n_placement_entries - 1];
                if (logical_tier < 0 || logical_tier >= e->gpu_cfg.n_gpus)
                    logical_tier = 0;
            } else {
                continue;
            }
        }'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: cache CPU-spilled tensors on head_tier for SSD streaming')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
