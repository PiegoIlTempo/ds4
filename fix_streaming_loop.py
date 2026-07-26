import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix the streaming decode loop in metal_graph_eval_token_raw_swa_streaming
old = '''    for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
        const double tl0 = profile ? now_sec() : 0.0;
        if (!static_decode_map && !metal_graph_stream_map_layer_decode(model, weights, il)) {'''

new = '''    for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
        /* SSD streaming: skip CPU-spilled layers */
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        const double tl0 = profile ? now_sec() : 0.0;
        if (!static_decode_map && !metal_graph_stream_map_layer_decode(model, weights, il)) {'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: streaming decode loop skip CPU-spill')
else:
    print('NOT FOUND')

# Also fix the batch_static_decode loop
old2 = '''        for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
            ok = metal_graph_encode_decode_layer(g,
                                                 model,
                                                 &weights->layer[il],
                                                 il,
                                                 pos,
                                                 g->layer_raw_cache[il],
                                                 g->raw_cap,
                                                 raw_row,
                                                 n_raw,
                                                 token);'''

new2 = '''        for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
            /* SSD streaming: skip CPU-spilled layers */
            if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
            ok = metal_graph_encode_decode_layer(g,
                                                 model,
                                                 &weights->layer[il],
                                                 il,
                                                 pos,
                                                 g->layer_raw_cache[il],
                                                 g->raw_cap,
                                                 raw_row,
                                                 n_raw,
                                                 token);'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: batch_static_decode loop skip CPU-spill')
else:
    print('NOT FOUND: batch_static_decode')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
