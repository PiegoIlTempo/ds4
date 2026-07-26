import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

old = '''    if (has_cpu_spill) {
        if (e->ssd_streaming) {
            fprintf(stderr,
                    "ds4: SSD streaming active: %d CPU-spilled entries "
                    "will be demand-loaded from SSD\\n",
                    has_cpu_spill);
        } else {'''

new = '''    if (has_cpu_spill) {
        if (e->ssd_streaming) {
            /* SSD streaming: remap CPU-spilled entries to GPU0.
             * The per-device cache is skipped when SSD streaming is active,
             * so this won't trigger a large VRAM allocation. */
            fprintf(stderr,
                    "ds4: SSD streaming active: remapping %d CPU-spilled "
                    "entries to GPU0 for graph scaffold\\n",
                    has_cpu_spill);
            for (int i = 0; i < e->n_placement_entries; i++) {
                if (e->placement[i] == DS4_LAYER_PACK_CPU) {
                    e->placement[i] = 0;
                }
            }
        } else {'''

if old in content:
    content = content.replace(old, new, 1)
    with open(sys.argv[1], 'w') as f:
        f.write(content)
    print('OK')
else:
    print('NOT FOUND')
    sys.exit(1)
