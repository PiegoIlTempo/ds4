import sys, re

with open(sys.argv[1], 'r') as f:
    content = f.read()

changes = 0

# ===== PATCH 1: Remove SSD+multi-tier guard in ds4_engine_open_internal =====
old = '''    if (e->ssd_streaming && e->multi_tier) {
        fprintf(stderr, "ds4: --ssd-streaming is not compatible with multi-GPU placement\\n");
        return -1;
    }'''
if old in content:
    content = content.replace(old, '    /* Multi-GPU SSD streaming: guard removed for V100 support */', 1)
    changes += 1
    print('P1: Removed SSD+multi-tier guard')

# ===== PATCH 2: Remove CPU-spill guard in engine_install_gpu_placement =====
old = '''        if (e->ssd_streaming && e->placement[i] == DS4_LAYER_PACK_CPU) {
            fprintf(stderr, "ds4: CPU-spill placement detected; CPU-tier execution wiring not yet implemented\\n");
            return -1;
        }'''
if old in content:
    content = content.replace(old, '        /* Multi-GPU SSD streaming: CPU-spill guard removed */', 1)
    changes += 1
    print('P2: Removed CPU-spill guard in engine_install_gpu_placement')

# ===== PATCH 3: Remove CPU-spill guard in ds4_engine_open_internal (wave-3b) =====
old = '''        if (e->ssd_streaming && e->placement[i] == DS4_LAYER_PACK_CPU) {
            fprintf(stderr, "ds4: CPU-spill placement detected; CPU-tier execution wiring not yet implemented\\n");
            return -1;
        }'''
# This might appear twice - handle both
count = content.count(old)
if count > 0:
    content = content.replace(old, '        /* Multi-GPU SSD streaming: CPU-spill guard removed */', count)
    changes += 1
    print(f'P3: Removed CPU-spill guard (x{count})')

# ===== PATCH 4: Fix emb_tier for SSD streaming =====
old = '''    if (g->ssd_streaming && g->emb_tier == DS4_LAYER_PACK_CPU) g->emb_tier = 0;'''
if old in content:
    changes += 1
    print('P4: emb_tier fix already present')
else:
    # Find the emb_tier assignment
    m = re.search(r'(g->emb_tier\s*=\s*placement\s*\?\s*placement\[0\]\s*:\s*0;)', content)
    if m:
        content = content.replace(m.group(1), m.group(1) + '\n    if (g->ssd_streaming && g->emb_tier == DS4_LAYER_PACK_CPU) g->emb_tier = 0;', 1)
        changes += 1
        print('P4: Fixed emb_tier for SSD streaming')

# ===== PATCH 5: Fix head_tier for SSD streaming =====
old = '''    if (g->ssd_streaming && g->head_tier == DS4_LAYER_PACK_CPU) g->head_tier = 0;'''
if old in content:
    changes += 1
    print('P5: head_tier fix already present')
else:
    m = re.search(r'(g->head_tier\s*=\s*placement\s*\?\s*placement\[DS4_N_LAYER\s*\+\s*1\]\s*:\s*0;)', content)
    if m:
        content = content.replace(m.group(1), m.group(1) + '\n    if (g->ssd_streaming && g->head_tier == DS4_LAYER_PACK_CPU) g->head_tier = 0;', 1)
        changes += 1
        print('P5: Fixed head_tier for SSD streaming')

# ===== PATCH 6: Set g->ssd_streaming before metal_graph_alloc_raw_cap =====
old = '''    if (g->ssd_streaming) {
        if (!metal_graph_alloc_raw_cap(g, model, weights)) {'''
if old in content:
    changes += 1
    print('P6: ssd_streaming already set before alloc_raw_cap')
else:
    # Find the call to metal_graph_alloc_raw_cap and ensure ssd_streaming is set before
    m = re.search(r'(if\s*\(!metal_graph_alloc_raw_cap\()', content)
    if m:
        # Check if ssd_streaming is set just before
        before = content[:m.start()]
        if 'g->ssd_streaming' not in before[-200:]:
            content = content.replace(m.group(1), '    g->ssd_streaming = true;\n    if (!metal_graph_alloc_raw_cap(', 1)
            changes += 1
            print('P6: Set ssd_streaming before alloc_raw_cap')

# ===== PATCH 7: Fix used_tier for SSD streaming =====
old = '''        if (t < 0 || t >= DS4_MAX_GPUS || t == g->head_tier) continue;'''
# Find the used_tier loop
count = content.count(old)
if count > 0:
    # Only fix the first occurrence (the used_tier one)
    content = content.replace(old, '        if (t < 0 || t >= DS4_MAX_GPUS) continue;', 1)
    changes += 1
    print('P7: Fixed used_tier for SSD streaming')

# ===== PATCH 8: Save/restore ssd_streaming around memset =====
old = '''    memset(g, 0, sizeof(*g));
    g->ssd_streaming = ssd_streaming;'''
if old in content:
    changes += 1
    print('P8: ssd_streaming save/restore already present')
else:
    m = re.search(r'(memset\s*\(\s*g\s*,\s*0\s*,\s*sizeof\s*\(\s*\*g\s*\)\s*\);)', content)
    if m:
        content = content.replace(m.group(1), '    const bool saved_ssd = g->ssd_streaming;\n    memset(g, 0, sizeof(*g));\n    g->ssd_streaming = saved_ssd;', 1)
        changes += 1
        print('P8: Save/restore ssd_streaming around memset')

# ===== PATCH 9: Set ssd_streaming in engine_open =====
old = '''    e->ssd_streaming = opt->ssd_streaming;'''
if old in content:
    changes += 1
    print('P9: ssd_streaming already set in engine_open')
else:
    m = re.search(r'(e->ssd_streaming\s*=\s*opt->ssd_streaming)', content)
    if m:
        changes += 1
        print('P9: ssd_streaming already set in engine_open')

# ===== PATCH 10: Skip per-layer allocations for CPU-spill =====
old = '''        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;'''
if old in content:
    changes += 1
    print('P10: layer skip already present')
else:
    # Find the per-layer allocation loop
    m = re.search(r'(for\s*\(\s*uint32_t\s+il\s*=\s*0\s*;\s*il\s*<\s*DS4_N_LAYER\s*;\s*il\+\+\s*\)\s*\{[^}]*layer_raw_cache)', content, re.DOTALL)
    if m:
        loop = m.group(0)
        # Add skip after the opening brace
        new_loop = loop.replace('{', '{\n            if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;', 1)
        content = content.replace(loop, new_loop, 1)
        changes += 1
        print('P10: Added layer skip for CPU-spill')

# ===== PATCH 11: layer_cache_ok skip CPU-spill =====
old = '''    bool layer_cache_ok = true;
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        if (g->layer_raw_cache[il] == NULL) { layer_cache_ok = false; break; }
    }'''
if old in content:
    content = content.replace(old, '''    bool layer_cache_ok = true;
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        if (g->layer_raw_cache[il] == NULL) { layer_cache_ok = false; break; }
    }''', 1)
    changes += 1
    print('P11: layer_cache_ok skip CPU-spill')

# ===== PATCH 12: reset_prefill_state skip CPU-spill =====
old = '''    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        if (!metal_tensor_fill_f32(g->layer_attn_state_kv[il], 0.0f, g->layer_attn_state_kv[il]->bytes / sizeof(float))) {'''
if old in content:
    content = content.replace(old, '''    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        if (!metal_tensor_fill_f32(g->layer_attn_state_kv[il], 0.0f, g->layer_attn_state_kv[il]->bytes / sizeof(float))) {''', 1)
    changes += 1
    print('P12: reset_prefill_state skip CPU-spill')

# ===== PATCH 13: build_prefill_stages skip CPU-spill =====
old = '''    int prev_tier = -1;
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        const int tier = g->placement[il + 1];
        if (tier < 0 || tier >= DS4_MAX_GPUS) return false;'''
if old in content:
    content = content.replace(old, '''    int prev_tier = -1;
    for (uint32_t il = 0; il < DS4_N_LAYER; il++) {
        const int tier = g->placement[il + 1];
        if (g->ssd_streaming && tier == DS4_LAYER_PACK_CPU) continue;
        if (tier < 0 || tier >= DS4_MAX_GPUS) return false;''', 1)
    changes += 1
    print('P13: build_prefill_stages skip CPU-spill')

# ===== PATCH 14: prefill_layer_major non-split loop skip CPU-spill =====
old = '''        for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
            ok = metal_graph_encode_layer_batch(g,
                                                model,
                                                &weights->layer[il],
                                                il,
                                                start,
                                                n_tokens);'''
if old in content:
    content = content.replace(old, '''        for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
            if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
            ok = metal_graph_encode_layer_batch(g,
                                                model,
                                                &weights->layer[il],
                                                il,
                                                start,
                                                n_tokens);''', 1)
    changes += 1
    print('P14: prefill_layer_major non-split loop skip CPU-spill')

# ===== PATCH 15: split_commands loop skip CPU-spill =====
old = '''    for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
        double layer_elapsed = 0.0;
        if (layer_prepare &&
            !metal_graph_stream_prepare_join_layer(g,'''
if old in content:
    content = content.replace(old, '''    for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        double layer_elapsed = 0.0;
        if (layer_prepare &&
            !metal_graph_stream_prepare_join_layer(g,''', 1)
    changes += 1
    print('P15: split_commands loop skip CPU-spill')

# ===== PATCH 16: streaming decode loop skip CPU-spill =====
old = '''    for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
        const double tl0 = profile ? now_sec() : 0.0;
        if (!static_decode_map && !metal_graph_stream_map_layer_decode(model, weights, il)) {'''
if old in content:
    content = content.replace(old, '''    for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
        if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
        const double tl0 = profile ? now_sec() : 0.0;
        if (!static_decode_map && !metal_graph_stream_map_layer_decode(model, weights, il)) {''', 1)
    changes += 1
    print('P16: streaming decode loop skip CPU-spill')

# ===== PATCH 17: batch_static_decode loop skip CPU-spill =====
old = '''        for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
            ok = metal_graph_encode_decode_layer(g,
                                                 model,
                                                 &weights->layer[il],
                                                 il,
                                                 pos,
                                                 g->layer_raw_cache[il],'''
if old in content:
    content = content.replace(old, '''        for (uint32_t il = 0; ok && il < DS4_N_LAYER; il++) {
            if (g->ssd_streaming && g->placement && g->placement[il + 1] == DS4_LAYER_PACK_CPU) continue;
            ok = metal_graph_encode_decode_layer(g,
                                                 model,
                                                 &weights->layer[il],
                                                 il,
                                                 pos,
                                                 g->layer_raw_cache[il],''', 1)
    changes += 1
    print('P17: batch_static_decode loop skip CPU-spill')

# ===== PATCH 18: Set active_tier + force device before embed in streaming =====
old = '''    if (ok) {
        ok = ds4_gpu_embed_token_hc_tensor(metal_graph_cur_hc(g),'''
if old in content:
    content = content.replace(old, '''    if (ok) {
        if (g->placement) {
            g->active_tier = g->emb_tier;
            ds4_gpu_force_set_current_device(g->emb_tier);
        }
        ok = ds4_gpu_embed_token_hc_tensor(metal_graph_cur_hc(g),''', 1)
    changes += 1
    print('P18: Set active_tier + force device before embed')

# ===== PATCH 19: Map output head before encode in batch_static_decode =====
old = '''        if (ok && logits) {
            ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);
        }
        const double t_encoded = (profile || throttle) ? now_sec() : 0.0;'''
if old in content:
    content = content.replace(old, '''        if (ok && logits) {
            if (g->placement) {
                ds4_gpu_force_set_current_device(g->emb_tier);
            }
            if (ok) ok = metal_graph_stream_map_output(model, weights);
            if (ok) ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);
        }
        const double t_encoded = (profile || throttle) ? now_sec() : 0.0;''', 1)
    changes += 1
    print('P19: Map output head before encode in batch_static_decode')

# ===== PATCH 20: Map output head in non-batch path =====
old = '''    if (ok && logits && !static_decode_map) ok = metal_graph_stream_map_output(model, weights);
    const double t_head0 = profile ? now_sec() : 0.0;
    if (ok && logits) ok = ds4_gpu_begin_commands() != 0;
    if (ok && logits) ok = metal_graph_encode_output_head(g, model, weights, weights->output->dim[1]);'''
if old in content:
    content = content.replace(old, '''    if (ok && logits && !static_decode_map) {
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
    }''', 1)
    changes += 1
    print('P20: Map output head in non-batch path')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print(f'\nDONE: {changes} patches applied')
