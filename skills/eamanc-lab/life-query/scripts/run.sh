#!/usr/bin/env bash
# 统一执行引擎：解析 apis/*.yaml → curl → 格式化输出
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
API_DIR="$SKILL_DIR/apis"
ENV_YAML="$API_DIR/_env.yaml"

usage() {
  echo "用法:"
  echo "  bash run.sh list                        # 列出所有可用接口"
  echo "  bash run.sh call <接口名> [参数...]      # 调用指定接口"
  echo "  bash run.sh show <接口名>               # 查看接口定义"
  echo ""
  echo "参数格式: --key value 或 --flag（布尔）"
  echo "输出格式: --format table|json（默认 json）"
}

cmd="${1:-}"
case "$cmd" in
  list)
    echo "可用接口："
    python3 - "$API_DIR" <<'PYEOF'
import os, sys, re, yaml
api_dir = sys.argv[1]
rows = []
for f in sorted(os.listdir(api_dir)):
    if f.startswith('_'):
        continue
    path = os.path.join(api_dir, f)
    if f.endswith('.yaml'):
        with open(path) as fp:
            d = yaml.safe_load(fp)
        rows.append((d.get('name',''), d.get('method',''), 'YAML', d.get('description','')))
    elif f.endswith('.sh'):
        name = f[:-3]
        desc = ''
        with open(path) as fp:
            for line in fp:
                m = re.match(r'^#\s*description:\s*(.+)', line)
                if m:
                    desc = m.group(1).strip()
                    break
        rows.append((name, '脚本', '脚本', desc))
if rows:
    w = [max(len(r[i]) for r in rows) for i in range(4)]
    fmt = f"  {{:<{w[0]}}}  {{:<{w[1]}}}  {{:<{w[2]}}}  {{}}"
    print(fmt.format('接口名', '方法', '类型', '说明'))
    print('  ' + '─'*(sum(w)+8))
    for r in rows:
        print(fmt.format(*r))
PYEOF
    ;;

  show)
    name="${2:-}"
    [ -z "$name" ] && { echo "错误: 请指定接口名"; exit 1; }
    yaml_file="$API_DIR/$name.yaml"
    [ ! -f "$yaml_file" ] && { echo "错误: 接口 '$name' 不存在"; exit 1; }
    cat "$yaml_file"
    ;;

  call)
    name="${2:-}"
    [ -z "$name" ] && { echo "错误: 请指定接口名"; exit 1; }
    shift 2

    # 脚本接口优先
    if [ -f "$API_DIR/$name.sh" ]; then
      bash "$API_DIR/$name.sh" "$@"
      exit 0
    fi

    yaml_file="$API_DIR/$name.yaml"
    [ ! -f "$yaml_file" ] && { echo "错误: 接口 '$name' 不存在"; exit 1; }

    python3 - "$ENV_YAML" "$yaml_file" "$@" <<'PYEOF'
import sys, os, json, re, subprocess, yaml

env_yaml, api_yaml = sys.argv[1], sys.argv[2]
raw_args = sys.argv[3:]

# 解析命令行 --key value
cli = {}
i = 0
while i < len(raw_args):
    if raw_args[i].startswith('--'):
        key = raw_args[i][2:]
        val = raw_args[i+1] if i+1 < len(raw_args) and not raw_args[i+1].startswith('--') else 'true'
        cli[key] = val
        i += 2 if val != 'true' else 1
    else:
        i += 1

output_format = cli.pop('format', os.environ.get('FENXIANG_OUTPUT_FORMAT', 'json'))

# 读公共配置
with open(env_yaml) as f:
    env_cfg = yaml.safe_load(f)

# 环境变量替换
def expand(v):
    if isinstance(v, str):
        return re.sub(r'\$\{(\w+)\}', lambda m: os.environ.get(m.group(1), m.group(0)), v)
    return v

base_url = expand(env_cfg.get('base_url', ''))
common_headers = {k: expand(v) for k, v in env_cfg.get('headers', {}).items()}

# 读接口定义
with open(api_yaml) as f:
    api = yaml.safe_load(f)

method = api.get('method', 'GET').upper()
path   = api.get('path', '')
body_cfg = api.get('body', {})

# 构造请求体（POST）
body_data = {}
for field, meta in (body_cfg.get('fields') or {}).items():
    if field in cli:
        body_data[field] = cli[field]
    elif isinstance(meta, dict) and meta.get('env') and os.environ.get(meta['env']):
        body_data[field] = os.environ[meta['env']]

# 路径参数替换
url = base_url.rstrip('/') + path
for param, val in list(body_data.items()):
    if '{' + param + '}' in url:
        url = url.replace('{' + param + '}', str(val))
        del body_data[param]

# 组装 curl
cmd = ['curl', '-sf', '-X', method]
for k, v in common_headers.items():
    cmd += ['-H', f'{k}: {v}']
for k, v in api.get('headers', {}).items():
    cmd += ['-H', f'{k}: {expand(v)}']
if method in ('POST', 'PUT', 'PATCH') and body_data:
    cmd += ['-d', json.dumps(body_data)]
cmd.append(url)

if os.environ.get('FENXIANG_VERBOSE', '').lower() == 'true':
    print('[DEBUG]', ' '.join(cmd), file=sys.stderr)

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print('HTTP 请求失败:', result.stderr, file=sys.stderr)
    sys.exit(1)

resp = json.loads(result.stdout)

# 提取数据
data_path = (api.get('response') or {}).get('data_path', '')
data = resp
for key in (data_path.split('.') if data_path else []):
    data = data.get(key, {}) if isinstance(data, dict) else data

if output_format == 'json':
    print(json.dumps(data, ensure_ascii=False, indent=2))
elif output_format == 'table':
    columns = (api.get('response') or {}).get('columns', [])
    items = data if isinstance(data, list) else [data]
    if columns and items:
        headers = [c['label'] for c in columns]
        fields  = [c['field'] for c in columns]
        rows = [[str(item.get(f, '')) for f in fields] for item in items]
        widths = [max(len(h), max((len(r[i]) for r in rows), default=0)) for i, h in enumerate(headers)]
        sep = '  '.join('-'*w for w in widths)
        header_row = '  '.join(h.ljust(widths[i]) for i, h in enumerate(headers))
        print(header_row)
        print(sep)
        for row in rows:
            print('  '.join(v.ljust(widths[i]) for i, v in enumerate(row)))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
PYEOF
    ;;

  *)
    usage
    ;;
esac
