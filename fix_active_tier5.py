import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: don't set active_tier before calling ds4_gpu_set_current_device
# This way metal_graph_set_active_tier_decode will actually call cudaSetDevice
old = '''        /* SSD streaming + multi-tier: reset active_tier and CUDA device to emb_tier before embed */
        if (g->placement) {
            g->active_tier = g->emb_tier;
            ds4_gpu_set_current_device(g->emb_tier);
        }'''

new = '''        /* SSD streaming + multi-tier: reset CUDA device to emb_tier before embed.
         * Do NOT set g->active_tier here — metal_graph_set_active_tier_decode
         * uses active_tier to detect device changes and would skip cudaSetDevice
         * if active_tier already matches the target tier. */
        if (g->placement) {
            ds4_gpu_set_current_device(g->emb_tier);
        }'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: don\'t set active_tier before embed, only set CUDA device')
else:
    print('NOT FOUND')

# Also fix the output head paths
old2 = '''            /* Multi-GPU SSD streaming: reset to emb_tier before output head */
            if (g->placement) {
                g->active_tier = g->emb_tier;
                ds4_gpu_set_current_device(g->emb_tier);
            }
            ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

new2 = '''            /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
            if (g->placement) {
                ds4_gpu_set_current_device(g->emb_tier);
            }
            ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: output head path - don\'t set active_tier')
else:
    print('NOT FOUND: output head path')

old3 = '''        /* Multi-GPU SSD streaming: reset to emb_tier before output head */
        if (g->placement) {
            g->active_tier = g->emb_tier;
            ds4_gpu_set_current_device(g->emb_tier);
        }
        ok = metal_graph_stream_map_output(model, weights);'''

new3 = '''        /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
        if (g->placement) {
            ds4_gpu_set_current_device(g->emb_tier);
        }
        ok = metal_graph_stream_map_output(model, weights);'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('FIXED: stream_map_output path - don\'t set active_tier')
else:
    print('NOT FOUND: stream_map_output path')

old4 = '''        /* Multi-GPU SSD streaming: reset to emb_tier before output head */
        if (g->placement) {
            g->active_tier = g->emb_tier;
            ds4_gpu_set_current_device(g->emb_tier);
        }
        ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

new4 = '''        /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
        if (g->placement) {
            ds4_gpu_set_current_device(g->emb_tier);
        }
        ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

if old4 in content:
    content = content.replace(old4, new4, 1)
    print('FIXED: non-batch output head path - don\'t set active_tier')
else:
    print('NOT FOUND: non-batch output head path')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
