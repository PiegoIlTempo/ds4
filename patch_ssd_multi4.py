import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

old = '''    if (has_cpu_spill) {
        fprintf(stderr,
            "ds4: CPU-spill placement detected; CPU-tier execution wiring lands in\\n"
            "ds4: cpu-spill execution (follow-up) (CPU-spill execution). Aborting engine creation.\\n");
        return -1;
    }'''

new = '''    if (has_cpu_spill) {
        if (e->ssd_streaming) {
            fprintf(stderr,
                    "ds4: SSD streaming active: %d CPU-spilled entries "
                    "will be demand-loaded from SSD\\n",
                    has_cpu_spill);
        } else {
            fprintf(stderr,
                "ds4: CPU-spill placement detected; CPU-tier execution wiring lands in\\n"
                "ds4: cpu-spill execution (follow-up) (CPU-spill execution). Aborting engine creation.\\n");
            return -1;
        }
    }'''

if old in content:
    content = content.replace(old, new, 1)
    with open(sys.argv[1], 'w') as f:
        f.write(content)
    print('OK')
else:
    print('NOT FOUND')
    sys.exit(1)
