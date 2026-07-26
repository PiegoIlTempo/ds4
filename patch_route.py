import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

old = '    if (!dist_coordinator_ensure_route(state, &plan, &plan_generation, err, sizeof(err))) {\n        fprintf(stderr, "ds4: distributed coordinator: %s\\n", err);\n        return 1;\n    }'

new = '    int route_retries = 0;\n    while (!dist_coordinator_ensure_route(state, &plan, &plan_generation, err, sizeof(err))) {\n        if (route_retries >= 30) {\n            fprintf(stderr, "ds4: distributed coordinator: %s\\n", err);\n            return 1;\n        }\n        if (route_retries == 0) fprintf(stderr, "ds4: distributed coordinator: waiting for workers...\\n");\n        route_retries++;\n        sleep(1);\n    }'

if old in content:
    content = content.replace(old, new, 1)
    with open(sys.argv[1], 'w') as f:
        f.write(content)
    print('OK')
else:
    print('NOT FOUND')
    sys.exit(1)
