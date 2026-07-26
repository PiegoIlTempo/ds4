import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: add stream_map_output before encode_output_head in batch_static_decode
old = '''            if (g->placement) {
                g->active_tier = g->emb_tier;
                ds4_gpu_force_set_current_device(g->emb_tier);
            }
            ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

new = '''            if (g->placement) {
                g->active_tier = g->emb_tier;
                ds4_gpu_force_set_current_device(g->emb_tier);
            }
            if (ok) ok = metal_graph_stream_map_output(model, weights);
            if (ok) ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added stream_map_output in batch_static_decode')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
