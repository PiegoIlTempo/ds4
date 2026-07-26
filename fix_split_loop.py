import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix the split_commands loop in metal_graph_prefill_layer_major
old = '''    for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
        double layer_elapsed = 0.0;
        if (layer_prepare &&
            !metal_graph_stream_prepare_join_layer(g,
                                                   model,
                                                   weights,
                                                   il,
                                                   n_tokens,
                                                   layer_madvise,
                                                   layer_pread,
                                                   layer_readahead,
                                                   batch_selected_addr,
                                                   layer_prepare_slots,
                                                   layer_prepare_ahead)) {
            ok = false;
            break;
        }'''

new = '''    for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
        /* SSD streaming: skip CPU-spilled layers (demand-loaded from SSD) */
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        double layer_elapsed = 0.0;
        if (layer_prepare &&
            !metal_graph_stream_prepare_join_layer(g,
                                                   model,
                                                   weights,
                                                   il,
                                                   n_tokens,
                                                   layer_madvise,
                                                   layer_pread,
                                                   layer_readahead,
                                                   batch_selected_addr,
                                                   layer_prepare_slots,
                                                   layer_prepare_ahead)) {
            ok = false;
            break;
        }'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: split_commands loop skip CPU-spill')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
