import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

old = '    if (engine_install_per_device_caches(e) != 0) return -1;'
new = '    if (!e->ssd_streaming) {\n        if (engine_install_per_device_caches(e) != 0) return -1;\n    } else {\n        fprintf(stderr,\n                "ds4: SSD streaming active: skipping per-device cache "\n                "installation (weights loaded on demand)\\n");\n    }'

if old in content:
    content = content.replace(old, new, 1)
    with open(sys.argv[1], 'w') as f:
        f.write(content)
    print('OK')
else:
    print('NOT FOUND')
    sys.exit(1)
