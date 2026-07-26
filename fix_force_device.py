import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Add ds4_gpu_force_set_current_device after ds4_gpu_set_current_device
old = '''extern \"C\" int ds4_gpu_set_current_device(int logical_tier) {
    if (logical_tier < 0 || logical_tier >= g_n_gpus) return -1;
    if (!g_cuda_no_setdevice_cache && g_current_logical_tier == logical_tier) {
        return 0;
    }
    if (cudaSetDevice(g_gpu[logical_tier].device_id) == cudaSuccess) {
        g_current_logical_tier = logical_tier;
        return 0;
    }
    g_current_logical_tier = -1;
    return -1;
}'''

new = '''extern \"C\" int ds4_gpu_set_current_device(int logical_tier) {
    if (logical_tier < 0 || logical_tier >= g_n_gpus) return -1;
    if (!g_cuda_no_setdevice_cache && g_current_logical_tier == logical_tier) {
        return 0;
    }
    if (cudaSetDevice(g_gpu[logical_tier].device_id) == cudaSuccess) {
        g_current_logical_tier = logical_tier;
        return 0;
    }
    g_current_logical_tier = -1;
    return -1;
}

/* Force a CUDA device switch, bypassing the g_current_logical_tier cache.
 * Used by multi-GPU SSD streaming to reset the device after per-layer decode
 * pipelines leave the actual device on a different GPU. */
extern \"C\" int ds4_gpu_force_set_current_device(int logical_tier) {
    if (logical_tier < 0 || logical_tier >= g_n_gpus) return -1;
    if (cudaSetDevice(g_gpu[logical_tier].device_id) == cudaSuccess) {
        g_current_logical_tier = logical_tier;
        return 0;
    }
    g_current_logical_tier = -1;
    return -1;
}'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: added ds4_gpu_force_set_current_device')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
