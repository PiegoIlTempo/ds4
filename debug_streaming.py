import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug in metal_graph_eval_token_raw_swa_streaming
old = '''    bool ok = true;
    if (static_decode_map) {
        if (!static_map_state_cache || !g->streaming_static_decode_map_current) {
            ok = metal_graph_stream_map_decode_static_all(model, weights);
            if (ok) g->streaming_static_decode_map_current = static_map_state_cache;
        }
    } else {
        g->streaming_static_decode_map_current = false;
        ok = metal_graph_stream_map_token(model, weights);
    }
    if (ok && !static_decode_map && DS4_N_LAYER > 0) {
        metal_graph_stream_readahead_layer_decode(model, weights, 0);
    }
    if (ok) ok = ds4_gpu_begin_commands() != 0;
    if (ok) {
        ok = ds4_gpu_embed_token_hc_tensor(metal_graph_cur_hc(g),
                                           model->map,
                                           model->size,
                                           weights->token_embd->abs_offset,
                                           (uint32_t)weights->token_embd->dim[1],
                                           (uint32_t)token,
                                           DS4_N_EMBD,
                                           DS4_N_HC) != 0;
    }'''

new = '''    bool ok = true;
    if (static_decode_map) {
        if (!static_map_state_cache || !g->streaming_static_decode_map_current) {
            fprintf(stderr, "ds4: DEBUG streaming: calling stream_map_decode_static_all\\n");
            ok = metal_graph_stream_map_decode_static_all(model, weights);
            if (ok) g->streaming_static_decode_map_current = static_map_state_cache;
        }
    } else {
        g->streaming_static_decode_map_current = false;
        fprintf(stderr, "ds4: DEBUG streaming: calling stream_map_token\\n");
        ok = metal_graph_stream_map_token(model, weights);
    }
    fprintf(stderr, "ds4: DEBUG streaming: after map, ok=%d\\n", ok);
    if (ok && !static_decode_map && DS4_N_LAYER > 0) {
        fprintf(stderr, "ds4: DEBUG streaming: calling readahead_layer_decode(0)\\n");
        metal_graph_stream_readahead_layer_decode(model, weights, 0);
    }
    fprintf(stderr, "ds4: DEBUG streaming: calling begin_commands\\n");
    if (ok) ok = ds4_gpu_begin_commands() != 0;
    fprintf(stderr, "ds4: DEBUG streaming: begin_commands ok=%d\\n", ok);
    if (ok) {
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor\\n");
        ok = ds4_gpu_embed_token_hc_tensor(metal_graph_cur_hc(g),
                                           model->map,
                                           model->size,
                                           weights->token_embd->abs_offset,
                                           (uint32_t)weights->token_embd->dim[1],
                                           (uint32_t)token,
                                           DS4_N_EMBD,
                                           DS4_N_HC) != 0;
    }
    fprintf(stderr, "ds4: DEBUG streaming: embed ok=%d\\n", ok);'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added streaming debug')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
