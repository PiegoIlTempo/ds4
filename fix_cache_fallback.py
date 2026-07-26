import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: add fallback to cuda_model_range_ptr when cache miss
old = '''    fprintf(stderr,
        "ds4: selective-cache miss for offset=%llu bytes=%llu on "
        "logical_tier=%d (physical_device=%d, current_device=%d, "
        "label=%s); this is a placement/cache-install bug\\n",
        (unsigned long long)offset, (unsigned long long)bytes,
        logical_tier, physical_device, cur_dev, label ? label : "?");
    return NULL;'''

new = '''    /* Multi-GPU SSD streaming: fall back to host-mapped range when the
     * selective cache doesn't have this tensor (e.g. CPU-spilled output
     * head tensors that were never cached on any GPU). */
    return cuda_model_range_ptr(model_map, offset, bytes, label);'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added fallback to cuda_model_range_ptr on cache miss')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
