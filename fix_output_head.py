import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: reset device to emb_tier before output head in batch_static_decode path
old = '''        if (ok && logits) {
            ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);
        }'''

new = '''        if (ok && logits) {
            /* Multi-GPU SSD streaming: reset to emb_tier before output head */
            if (g->placement) {
                g->active_tier = g->emb_tier;
                ds4_gpu_set_current_device(g->emb_tier);
            }
            ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);
        }'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: reset device before output head in batch_static_decode')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
