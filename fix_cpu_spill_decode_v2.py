import sys

with open('ds4.c', 'r') as f:
    content = f.read()

# Fix 1: batch_static_decode path - switch to head_tier for CPU-spill layers
old1 = '''            /* SSD streaming: execute CPU-spilled layers on current tier */
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
            }'''

new1 = '''            /* SSD streaming: execute CPU-spilled layers on head_tier */
            if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) {
                if (!metal_graph_set_active_tier_decode(g, g->head_tier)) {
                    ok = false; break;
                }
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
            }'''

# Fix 2: non-batch decode path - switch to head_tier for CPU-spill layers
old2 = '''        /* SSD streaming: execute CPU-spilled layers on current tier */
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
        }'''

new2 = '''        /* SSD streaming: execute CPU-spilled layers on head_tier */
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) {
            if (!metal_graph_set_active_tier_decode(g, g->head_tier)) {
                ok = false; break;
            }
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
        }'''

count = 0
if old1 in content:
    content = content.replace(old1, new1, 1)
    count += 1
    print('FIXED: batch_static_decode path - CPU-spill layers now execute on head_tier')
else:
    print('NOT FOUND: batch_static_decode path')

if old2 in content:
    content = content.replace(old2, new2, 1)
    count += 1
    print('FIXED: non-batch decode path - CPU-spill layers now execute on head_tier')
else:
    print('NOT FOUND: non-batch decode path')

with open('ds4.c', 'w') as f:
    f.write(content)
print(f'DONE: {count} patches applied')
