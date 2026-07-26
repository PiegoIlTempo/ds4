import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

changes = 0

# PATCH: Set active_tier + force device before embed in streaming path
old = '''    if (ok) {
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor\\n");
        ok = ds4_gpu_embed_token_hc_tensor(metal_graph_cur_hc(g),'''

new = '''    if (ok) {
        if (g->placement) {
            g->active_tier = g->emb_tier;
            ds4_gpu_force_set_current_device(g->emb_tier);
        }
        fprintf(stderr, "ds4: DEBUG streaming: calling embed_token_hc_tensor active_tier=%d\\n", g->active_tier);
        ok = ds4_gpu_embed_token_hc_tensor(metal_graph_cur_hc(g),'''

if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print('P1: Set active_tier + force device before embed')

# PATCH: Map output head in batch_static_decode
old = '''        if (ok && logits) {
            ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);
        }
        const double t_encoded = (profile || throttle) ? now_sec() : 0.0;'''

new = '''        if (ok && logits) {
            if (g->placement) {
                ds4_gpu_force_set_current_device(g->emb_tier);
            }
            if (ok) ok = metal_graph_stream_map_output(model, weights);
            if (ok) ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);
        }
        const double t_encoded = (profile || throttle) ? now_sec() : 0.0;'''

if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print('P2: Map output head in batch_static_decode')

# PATCH: Map output head in non-batch path
old = '''    if (ok && logits && !static_decode_map) ok = metal_graph_stream_map_output(model, weights);
    const double t_head0 = profile ? now_sec() : 0.0;
    if (ok && logits) ok = ds4_gpu_begin_commands() != 0;
    if (ok && logits) ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''

new = '''    if (ok && logits && !static_decode_map) {
        if (g->placement) {
            ds4_gpu_force_set_current_device(g->emb_tier);
        }
        ok = metal_graph_stream_map_output(model, weights);
    }
    const double t_head0 = profile ? now_sec() : 0.0;
    if (ok && logits) ok = ds4_gpu_begin_commands() != 0;
    if (ok && logits) {
        if (g->placement) {
            ds4_gpu_force_set_current_device(g->emb_tier);
        }
        ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);
    }'''

if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print('P3: Map output head in non-batch path')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print(f'DONE: {changes} patches applied')
