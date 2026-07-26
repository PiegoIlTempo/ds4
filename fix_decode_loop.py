import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: skip CPU-spilled layers in metal_graph_encode_token_raw_swa decode loop
old = '''    for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
        ok = metal_graph_encode_decode_layer(g,
                                             model,
                                             &weights->layer[il],
                                             il,
                                             pos,
                                             g->layer_raw_cache[il],'''

new = '''    for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
        /* SSD streaming: skip CPU-spilled layers */
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        ok = metal_graph_encode_decode_layer(g,
                                             model,
                                             &weights->layer[il],
                                             il,
                                             pos,
                                             g->layer_raw_cache[il],'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: encode_token_raw_swa decode loop skip CPU-spill')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
