import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix: make metal_graph_encode_token_raw_swa use streaming path when ssd_streaming
old = '''static bool metal_graph_encode_token_raw_swa(
        ds4_gpu_graph *g,
        const ds4_model       *model,
        const ds4_weights     *weights,
        int                    token,
        uint32_t               pos,
        bool                   need_logits,
        bool                   allow_split_flush) {
    if (g->raw_cap == 0) {
        fprintf(stderr, "ds4: Metal graph raw KV cache is not allocated\\n");
        return false;
    }'''

new = '''static bool metal_graph_encode_token_raw_swa(
        ds4_gpu_graph *g,
        const ds4_model       *model,
        const ds4_weights     *weights,
        int                    token,
        uint32_t               pos,
        bool                   need_logits,
        bool                   allow_split_flush) {
    /* SSD streaming: redirect to the streaming-aware decode path */
    if (g && g->ssd_streaming) {
        return metal_graph_eval_token_raw_swa_streaming(g, model, weights, token, pos,
                                                        need_logits ? metal_graph_logits(g) : NULL);
    }
    if (g->raw_cap == 0) {
        fprintf(stderr, "ds4: Metal graph raw KV cache is not allocated\\n");
        return false;
    }'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: encode_token_raw_swa redirects to streaming path when ssd_streaming')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
