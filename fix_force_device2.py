import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: use ds4_gpu_force_set_current_device to bypass the cache
old = '''        if (g->placement) {
            g->active_tier = g->emb_tier;
            ds4_gpu_set_current_device(g->emb_tier);
        }
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor active_tier=%d\\n", g->active_tier);'''

new = '''        if (g->placement) {
            g->active_tier = g->emb_tier;
            ds4_gpu_force_set_current_device(g->emb_tier);
        }
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor active_tier=%d\\n", g->active_tier);'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: use ds4_gpu_force_set_current_device in embed')
else:
    print('NOT FOUND')

# Also fix the output head paths
old2 = '''            /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
            if (g->placement) {
                ds4_gpu_set_current_device(g->emb_tier);
            }
            ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

new2 = '''            /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
            if (g->placement) {
                ds4_gpu_force_set_current_device(g->emb_tier);
            }
            ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: use ds4_gpu_force_set_current_device in batch output head')
else:
    print('NOT FOUND: batch output head')

old3 = '''        /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
        if (g->placement) {
            ds4_gpu_set_current_device(g->emb_tier);
        }
        ok = metal_graph_stream_map_output(model, weights);'''

new3 = '''        /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
        if (g->placement) {
            ds4_gpu_force_set_current_device(g->emb_tier);
        }
        ok = metal_graph_stream_map_output(model, weights);'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('FIXED: use ds4_gpu_force_set_current_device in stream_map_output')
else:
    print('NOT FOUND: stream_map_output')

old4 = '''        /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
        if (g->placement) {
            ds4_gpu_set_current_device(g->emb_tier);
        }
        ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

new4 = '''        /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
        if (g->placement) {
            ds4_gpu_force_set_current_device(g->emb_tier);
        }
        ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

if old4 in content:
    content = content.replace(old4, new4, 1)
    print('FIXED: use ds4_gpu_force_set_current_device in non-batch output head')
else:
    print('NOT FOUND: non-batch output head')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
