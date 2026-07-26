import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Remove the single-GPU guard in ds4_cuda.cu
old = '''    if (g_n_gpus != 1) {
        fprintf(stderr,
                "ds4: CUDA SSD streaming requires single-GPU placement\\n");
        return 0;
    }'''

new = '''    /* Multi-GPU SSD streaming: guard removed for V100 multi-GPU support */'''

if old in content:
    content = content.replace(old, new, 1)
    print('FIXED: removed CUDA single-GPU guard')
else:
    print('NOT FOUND')

with open(sys.argv[1], 'w') as f:
    f.write(content)
print('DONE')
