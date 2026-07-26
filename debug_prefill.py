import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add debug at start of metal_graph_prefill_raw_swa
old = '''static bool metal_graph_prefill_raw_swa(
        ds4_gpu_graph *g,
        const ds4_model       *model,
        const ds4_weights     *weights,
        const token_vec       *prompt,
        int                    n_tokens,
        float                 *logits,
        bool                   show_progress,
        ds4_session_progress_fn display_progress,
        void                  *display_progress_ud,
        ds4_session_cancel_fn  cancel,
        void                  *cancel_ud,
        bool                  *cancelled) {
    if (n_tokens <= 0 || n_tokens > prompt->len) return false;
    if ((uint32_t)n_tokens > g->prefill_cap) return false;
    if (metal_graph_use_streaming_decode_prefill_range(g, weights, 0,
                                                       (uint32_t)n_tokens)) {
        return metal_graph_prefill_decode_streaming_range(g,'''

new = '''static bool metal_graph_prefill_raw_swa(
        ds4_gpu_graph *g,
        const ds4_model       *model,
        const ds4_weights     *weights,
        const token_vec       *prompt,
        int                    n_tokens,
        float                 *logits,
        bool                   show_progress,
        ds4_session_progress_fn display_progress,
        void                  *display_progress_ud,
        ds4_session_cancel_fn  cancel,
        void                  *cancel_ud,
        bool                  *cancelled) {
    fprintf(stderr, "ds4: DEBUG prefill_raw_swa: n_tokens=%d prefill_cap=%u ssd_streaming=%d quality=%d\\n",
            n_tokens, g->prefill_cap, g->ssd_streaming, g->quality);
    if (n_tokens <= 0 || n_tokens > prompt->len) { fprintf(stderr, "ds4: DEBUG prefill_raw_swa: n_tokens check fail\\n"); return false; }
    if ((uint32_t)n_tokens > g->prefill_cap) { fprintf(stderr, "ds4: DEBUG prefill_raw_swa: prefill_cap check fail\\n"); return false; }
    if (metal_graph_use_streaming_decode_prefill_range(g, weights, 0,
                                                       (uint32_t)n_tokens)) {
        fprintf(stderr, "ds4: DEBUG prefill_raw_swa: using streaming decode path\\n");
        return metal_graph_prefill_decode_streaming_range(g,'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added prefill_raw_swa debug')
else:
    print('NOT FOUND')

# Add debug in metal_graph_prefill_decode_streaming_range
old2 = '''    if (!metal_graph_use_streaming_decode_prefill(g, weights, n_tokens)) return false;
    if (!prompt || start > (uint32_t)prompt->len ||
        n_tokens > (uint32_t)prompt->len - start) return false;'''

new2 = '''    if (!metal_graph_use_streaming_decode_prefill(g, weights, n_tokens)) {
        fprintf(stderr, "ds4: DEBUG streaming_decode_prefill_range: use_streaming_decode_prefill returned false\\n");
        return false;
    }
    if (!prompt || start > (uint32_t)prompt->len ||
        n_tokens > (uint32_t)prompt->len - start) { fprintf(stderr, "ds4: DEBUG streaming_decode_prefill_range: bounds check fail\\n"); return false; }'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: added streaming_range debug')
else:
    print('NOT FOUND')

# Add debug in metal_graph_eval_token_raw_swa
old3 = '''    if (g && g->ssd_streaming) {
        return metal_graph_eval_token_raw_swa_streaming(g, model, weights, token, pos, logits);
    }'''

new3 = '''    if (g && g->ssd_streaming) {
        fprintf(stderr, "ds4: DEBUG eval_token_raw_swa: using streaming path, pos=%d\\n", pos);
        return metal_graph_eval_token_raw_swa_streaming(g, model, weights, token, pos, logits);
    }'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('FIXED: added eval_token debug')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
