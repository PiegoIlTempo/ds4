import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Fix the non-split_commands loop in metal_graph_prefill_layer_major
old = '''    if (!split_commands) {
        ok = metal_graph_upload_prompt_embeddings_hc(metal_graph_batch_cur_hc(g),
                                                     metal_graph_prefill_tokens(g),
                                                     model,
                                                     weights,
                                                     prompt,
                                                     start,
                                                     n_tokens);
        if (ok) ok = ds4_gpu_begin_commands() != 0;
        for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
            ok = metal_graph_encode_layer_batch(g,
                                                model,
                                                &weights->layer[il],
                                                il,
                                                start,
                                                n_tokens);'''

new = '''    if (!split_commands) {
        ok = metal_graph_upload_prompt_embeddings_hc(metal_graph_batch_cur_hc(g),
                                                     metal_graph_prefill_tokens(g),
                                                     model,
                                                     weights,
                                                     prompt,
                                                     start,
                                                     n_tokens);
        if (ok) ok = ds4_gpu_begin_commands() != 0;
        for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
            /* SSD streaming: skip CPU-spilled layers (demand-loaded from SSD) */
            if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
            ok = metal_graph_encode_layer_batch(g,
                                                model,
                                                &weights->layer[il],
                                                il,
                                                start,
                                                n_tokens);'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: prefill_layer_major skip CPU-spill in non-split path')
else:
    print('NOT FOUND: non-split path')

# Also fix the split_commands path (SSD streaming path)
old2 = '''    if (g->ssd_streaming) {
        g->streaming_static_decode_map_current = false;
        if (!metal_graph_stream_map_token(model, weights)) return false;
    }
    metal_graph_stream_prefill_selected_profile_reset(g);
    metal_graph_stream_prepare_slot layer_prepare_slots[DS4_STREAM_PREFILL_MAX_PREPARE_AHEAD];
    memset(layer_prepare_slots, 0, sizeof(layer_prepare_slots));
    const bool layer_pagein =
        metal_graph_stream_prefill_layer_pagein_enabled(g);
    const bool layer_readahead =
        !layer_pagein &&
        metal_graph_stream_prefill_layer_readahead_enabled(g);
    const bool layer_pread =
        !layer_pagein && !layer_readahead &&
        metal_graph_stream_prefill_layer_pread_enabled(g);
    const bool layer_madvise =
        !layer_pagein && !layer_pread && !layer_readahead &&
        metal_graph_stream_prefill_layer_madvise_enabled(g);
    const bool layer_prepare =
        layer_pagein || layer_pread || layer_readahead || layer_madvise;
    const bool layer_prepare_overlap =
        layer_prepare && metal_graph_stream_prefill_layer_pagein_overlap_enabled();
    const uint32_t layer_prepare_ahead =
        layer_prepare && layer_prepare_overlap ?'''

new2 = '''    if (g->ssd_streaming) {
        g->streaming_static_decode_map_current = false;
        if (!metal_graph_stream_map_token(model, weights)) return false;
    }
    metal_graph_stream_prefill_selected_profile_reset(g);
    metal_graph_stream_prepare_slot layer_prepare_slots[DS4_STREAM_PREFILL_MAX_PREPARE_AHEAD];
    memset(layer_prepare_slots, 0, sizeof(layer_prepare_slots));
    const bool layer_pagein =
        metal_graph_stream_prefill_layer_pagein_enabled(g);
    const bool layer_readahead =
        !layer_pagein &&
        metal_graph_stream_prefill_layer_readahead_enabled(g);
    const bool layer_pread =
        !layer_pagein && !layer_readahead &&
        metal_graph_stream_prefill_layer_pread_enabled(g);
    const bool layer_madvise =
        !layer_pagein && !layer_pread && !layer_readahead &&
        metal_graph_stream_prefill_layer_madvise_enabled(g);
    const bool layer_prepare =
        layer_pagein || layer_pread || layer_readahead || layer_madvise;
    const bool layer_prepare_overlap =
        layer_prepare && metal_graph_stream_prefill_layer_pagein_overlap_enabled();
    const uint32_t layer_prepare_ahead =
        layer_prepare && layer_prepare_overlap ?'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('FIXED: split path (no change needed)')
else:
    print('NOT FOUND: split path')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
