import sys

with open('ds4.c', 'r') as f:
    content = f.read()

# Fix 1: batch_static_decode path - replace skip with execute
old1 = '''            /* SSD streaming: skip CPU-spilled layers */
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
                                                 token);
            if (ok) {
                ds4_gpu_tensor *tmp = metal_graph_cur_hc(g);
                g->cur_hc_by_tier[g->active_tier] = metal_graph_after_ffn_hc(g);
                g->after_ffn_hc_by_tier[g->active_tier] = tmp;
                ok = metal_graph_dspark_capture_decode_layer(g, il);
            }'''

new1 = '''            /* SSD streaming: execute CPU-spilled layers on current tier */
            if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) {
                if (!metal_graph_stream_map_layer_decode(model, weights, il)) {
                    ok = false; break;
                }
                if (ok) ok = ds4_gpu_begin_commands() != 0;
                if (ok) ok = metal_graph_encode_decode_layer(g, model, &weights->layer[il], il, pos,
                    g->layer_raw_cache[il], g->raw_cap, raw_row, n_raw, token);
                if (ok) {
                    ds4_gpu_tensor *tmp = metal_graph_cur_hc(g);
                    g->cur_hc_by_tier[g->active_tier] = metal_graph_after_ffn_hc(g);
                    g->after_ffn_hc_by_tier[g->active_tier] = tmp;
                    ok = metal_graph_dspark_capture_decode_layer(g, il);
                }
                if (ok) ok = ds4_gpu_end_commands() != 0;
                continue;
            }
            ok = metal_graph_encode_decode_layer(g,
                                                 model,
                                                 &weights->layer[il],
                                                 il,
                                                 pos,
                                                 g->layer_raw_cache[il],
                                                 g->raw_cap,
                                                 raw_row,
                                                 n_raw,
                                                 token);
            if (ok) {
                ds4_gpu_tensor *tmp = metal_graph_cur_hc(g);
                g->cur_hc_by_tier[g->active_tier] = metal_graph_after_ffn_hc(g);
                g->after_ffn_hc_by_tier[g->active_tier] = tmp;
                ok = metal_graph_dspark_capture_decode_layer(g, il);
            }'''

# Fix 2: non-batch decode path
old2 = '''        /* SSD streaming: skip CPU-spilled layers */
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        const double tl0 = profile ? now_sec() : 0.0;
        if (!static_decode_map && !metal_graph_stream_map_layer_decode(model, weights, il)) {
            ok = false;
            break;
        }
        if (!static_decode_map && il + 1 < DS4_N_LAYER) {
            metal_graph_stream_readahead_layer_decode(model, weights, il + 1);
        } else if (!static_decode_map && logits) {
            metal_graph_stream_readahead_output(model, weights);
        }
        if (ok) ok = ds4_gpu_begin_commands() != 0;
        bool encoded_layer = false;
        if (ok) {
            ok = metal_graph_encode_decode_layer(g,
                                                 model,
                                                 &weights->layer[il],
                                                 il,
                                                 pos,
                                                 g->layer_raw_cache[il],
                                                 g->raw_cap,
                                                 raw_row,
                                                 n_raw,
                                                 token);
            encoded_layer = true;
        }
        if (encoded_layer) {
            ds4_gpu_tensor *tmp = metal_graph_cur_hc(g);
            g->cur_hc_by_tier[g->active_tier] = metal_graph_after_ffn_hc(g);
            g->after_ffn_hc_by_tier[g->active_tier] = tmp;
            if (ok) ok = metal_graph_dspark_capture_decode_layer(g, il);
        }
        const double tl_encoded = profile ? now_sec() : 0.0;
        if (ok) ok = ds4_gpu_end_commands() != 0;
        const double tl_done = profile ? now_sec() : 0.0;
        if (profile) {
            encode_s += tl_encoded - tl0;
            execute_s += tl_done - tl_encoded;
        }'''

new2 = '''        /* SSD streaming: execute CPU-spilled layers on current tier */
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) {
            if (!metal_graph_stream_map_layer_decode(model, weights, il)) {
                ok = false; break;
            }
            if (ok) ok = ds4_gpu_begin_commands() != 0;
            if (ok) ok = metal_graph_encode_decode_layer(g, model, &weights->layer[il], il, pos,
                g->layer_raw_cache[il], g->raw_cap, raw_row, n_raw, token);
            if (ok) {
                ds4_gpu_tensor *tmp = metal_graph_cur_hc(g);
                g->cur_hc_by_tier[g->active_tier] = metal_graph_after_ffn_hc(g);
                g->after_ffn_hc_by_tier[g->active_tier] = tmp;
                ok = metal_graph_dspark_capture_decode_layer(g, il);
            }
            if (ok) ok = ds4_gpu_end_commands() != 0;
            continue;
        }
        const double tl0 = profile ? now_sec() : 0.0;
        if (!static_decode_map && !metal_graph_stream_map_layer_decode(model, weights, il)) {
            ok = false;
            break;
        }
        if (!static_decode_map && il + 1 < DS4_N_LAYER) {
            metal_graph_stream_readahead_layer_decode(model, weights, il + 1);
        } else if (!static_decode_map && logits) {
            metal_graph_stream_readahead_output(model, weights);
        }
        if (ok) ok = ds4_gpu_begin_commands() != 0;
        bool encoded_layer = false;
        if (ok) {
            ok = metal_graph_encode_decode_layer(g,
                                                 model,
                                                 &weights->layer[il],
                                                 il,
                                                 pos,
                                                 g->layer_raw_cache[il],
                                                 g->raw_cap,
                                                 raw_row,
                                                 n_raw,
                                                 token);
            encoded_layer = true;
        }
        if (encoded_layer) {
            ds4_gpu_tensor *tmp = metal_graph_cur_hc(g);
            g->cur_hc_by_tier[g->active_tier] = metal_graph_after_ffn_hc(g);
            g->after_ffn_hc_by_tier[g->active_tier] = tmp;
            if (ok) ok = metal_graph_dspark_capture_decode_layer(g, il);
        }
        const double tl_encoded = profile ? now_sec() : 0.0;
        if (ok) ok = ds4_gpu_end_commands() != 0;
        const double tl_done = profile ? now_sec() : 0.0;
        if (profile) {
            encode_s += tl_encoded - tl0;
            execute_s += tl_done - tl_encoded;
        }'''

count = 0
if old1 in content:
    content = content.replace(old1, new1, 1)
    count += 1
    print('FIXED: batch_static_decode path - CPU-spill layers now execute on current tier')
else:
    print('NOT FOUND: batch_static_decode path')

if old2 in content:
    content = content.replace(old2, new2, 1)
    count += 1
    print('FIXED: non-batch decode path - CPU-spill layers now execute on current tier')
else:
    print('NOT FOUND: non-batch decode path')

with open('ds4.c', 'w') as f:
    f.write(content)
print(f'DONE: {count} patches applied')
