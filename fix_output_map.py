import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: map output head via streaming before encoding in batch_static_decode path
old = '''        if (ok && logits) {
            /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
            if (g->placement) {
                ds4_gpu_force_set_current_device(g->emb_tier);
            }
            ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);
        }'''

new = '''        if (ok && logits) {
            /* Multi-GPU SSD streaming: reset CUDA device to emb_tier before output head */
            if (g->placement) {
                ds4_gpu_force_set_current_device(g->emb_tier);
            }
            /* Map output head weights via streaming before encoding */
            if (ok) ok = metal_graph_stream_map_output(model, weights);
            if (ok) ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);
        }'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: map output head before encode in batch_static_decode')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
