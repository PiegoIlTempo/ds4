import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

old = '''        if (spilled > 0) {
            if (e->ssd_streaming) {
                /* SSD streaming: CPU-spilled entries are expected.
                 * The SSD streaming path loads expert weights on demand,
                 * so we don't need full VRAM residency. */
                fprintf(stderr,
                        "ds4: SSD streaming active: %d entries (%.2f GiB) "
                        "will be demand-loaded from SSD\\n",
                        spilled,
                        (double)spilled_bytes / (1024.0 * 1024.0 * 1024.0));
            } else {'''

new = '''        if (spilled > 0) {
            if (e->ssd_streaming) {
                /* SSD streaming: remap CPU-spilled entries to GPU0.
                 * The per-device cache is skipped when SSD streaming is active,
                 * so this won't trigger a large VRAM allocation. */
                fprintf(stderr,
                        "ds4: SSD streaming active: remapping %d CPU-spilled "
                        "entries (%.2f GiB) to GPU0 for graph scaffold\\n",
                        spilled,
                        (double)spilled_bytes / (1024.0 * 1024.0 * 1024.0));
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
