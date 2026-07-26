import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: instead of failing when stream_selected_cache doesn't match, fall through to non-cached path
old = '''    if (g_ssd_streaming_mode && allow_streaming &&
        !use_stream_selected_cache) {
        fprintf(stderr,
                "ds4: CUDA streaming selected experts are unavailable for layer %u\\n",
                layer_index);
        return 0;
    }'''

new = '''    /* Multi-GPU SSD streaming: if the per-tier cache doesn't match, fall through
     * to the non-cached cuda_resolve_weight_ptr path instead of failing. */
    if (g_ssd_streaming_mode && allow_streaming &&
        !use_stream_selected_cache) {
        /* Fall through to non-cached path below */
    }'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: stream_selected_cache guard -> fall through to non-cached')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
