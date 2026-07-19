#!/usr/bin/env python3
"""
Merge China domain/IP rules from 3 upstream sources, deduplicate by exact string match,
output merged YAML files, and compile to MRS via mihomo.
"""

import os
import sys
import yaml
import subprocess
import urllib.request
import tempfile
import re
from collections import OrderedDict

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE, "output")
MIHOMO_BIN = os.path.join(WORKSPACE, "mihomo")

# --- Source definitions ---
DOMAIN_SOURCES = [
    {
        "name": "MetaCubeX",
        "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/cn.yaml",
        "type": "yaml-payload",     # YAML with `payload: [+.domain, ...]`
    },
    {
        "name": "Loyalsoldier",
        "url": "https://github.com/Loyalsoldier/clash-rules/releases/latest/download/direct.txt",
        "type": "yaml-payload",      # Same format: `payload:\n  - '+.domain'`
    },
    {
        "name": "blackmatrix7",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/ChinaTest/ChinaTest_Domain.txt",
        "type": "plain-domain",     # One domain per line, no prefix
    },
]

IP_SOURCES = [
    {
        "name": "MetaCubeX",
        "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/cn.yaml",
        "type": "yaml-payload",     # YAML with `payload: [cidr, ...]`
    },
    {
        "name": "Loyalsoldier",
        "url": "https://github.com/Loyalsoldier/clash-rules/releases/latest/download/cncidr.txt",
        "type": "yaml-payload",     # Same format
    },
    {
        "name": "blackmatrix7",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/ChinaMax/ChinaMax_IP.txt",
        "type": "plain-ip",         # One CIDR per line
    },
]


def download(url, path):
    """Download url to path, skip if file exists."""
    if os.path.exists(path):
        print(f"  skipping {path}, already exists")
        return
    print(f"  downloading {url}")
    urllib.request.urlretrieve(url, path)
    print(f"    -> {os.path.getsize(path)} bytes")


def parse_yaml_payload(path):
    """Parse a YAML file with `payload:` list."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or "payload" not in data:
        return []
    return [str(item).strip() for item in data["payload"] if item]


def parse_plain_domain(path):
    """Parse plain text file, one domain per line, skip comments/blank."""
    results = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Strip leading `.` or `+.` for normalization
            results.append(line)
    return results


def parse_plain_ip(path):
    """Parse plain text IP CIDR file, one per line."""
    results = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            results.append(line)
    return results


def normalize_domain(entry):
    """
    Normalize a domain entry to a consistent format for dedup.
    Returns (bare_key, output_entry).
    - bare_key: the domain string without any prefix (for exact string dedup)
    - output_entry: with +. prefix for mihomo compatibility
    """
    s = entry.strip().strip("'\"")

    # meta/loyalsoldier format: +.domain  or +.alibaba (no TLD)
    if s.startswith("+."):
        bare = s[2:]
        return (bare, s)  # keep original +. prefix

    # Could also be just .domain (dot prefix only)
    if s.startswith("."):
        bare = s[1:]
        return (bare, s)

    # Plain domain from blackmatrix7
    return (s, f"+.{s}")


def normalize_ip(entry):
    """IP CIDR entries have no prefix, just the CIDR string."""
    s = entry.strip().strip("'\"")
    return (s, s)


def collect_items(sources, parse_fn, normalize_fn):
    """Collect, deduplicate, and sort items from multiple sources."""
    os.makedirs(os.path.join(WORKSPACE, "tmp"), exist_ok=True)
    all_items = {}

    for src in sources:
        print(f"\n  [{src['name']}]")
        tmp_path = os.path.join(WORKSPACE, "tmp", f"source_{src['name']}.tmp")
        download(src["url"], tmp_path)
        entries = parse_fn(tmp_path)
        print(f"    parsed {len(entries)} entries")

        for entry in entries:
            bare_key, output_entry = normalize_fn(entry)
            all_items[bare_key] = output_entry

    # Sort for deterministic output
    sorted_items = sorted(all_items.values())
    print(f"\n  total unique: {len(sorted_items)}")
    return sorted_items


def write_yaml(items, path):
    """Write items as YAML payload list."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump({"payload": items}, f, allow_unicode=True, default_style=None)
    print(f"  wrote {path} ({os.path.getsize(path)} bytes)")


def compile_mrs(yaml_path, behavior, output_path):
    """Compile YAML to MRS using mihomo convert-ruleset."""
    if not os.path.exists(MIHOMO_BIN):
        print(f"  [SKIP] mihomo not found at {MIHOMO_BIN}")
        return False

    cmd = [MIHOMO_BIN, "convert-ruleset", behavior, yaml_path, output_path]
    print(f"  running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    if os.path.exists(output_path):
        print(f"  compiled: {output_path} ({os.path.getsize(output_path)} bytes)")
        return True
    return False


def main():
    print("=" * 60)
    print("China Rules Merge Script")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Domain merge ---
    print("\n--- Domain Sources ---")
    domains = collect_items(DOMAIN_SOURCES, parse_yaml_payload, normalize_domain)
    domain_yaml = os.path.join(OUTPUT_DIR, "ChinaDomain.yaml")
    write_yaml(domains, domain_yaml)

    domain_mrs = os.path.join(OUTPUT_DIR, "ChinaDomain.mrs")
    compile_mrs(domain_yaml, "domain", domain_mrs)

    # --- IP merge ---
    print("\n--- IP CIDR Sources ---")
    # blackmatrix7 uses plain text format, not YAML
    # We handle it differently: MetaCubeX & Loyalsoldier = yaml-payload, blackmatrix7 = plain-ip
    ip_all = []

    for src in IP_SOURCES:
        print(f"\n  [{src['name']}]")
        tmp_path = os.path.join(WORKSPACE, "tmp", f"source_ip_{src['name']}.tmp")
        download(src["url"], tmp_path)

        if src["type"] == "yaml-payload":
            entries = parse_yaml_payload(tmp_path)
        else:
            entries = parse_plain_ip(tmp_path)

        print(f"    parsed {len(entries)} entries")
        for entry in entries:
            bare_key, output_entry = normalize_ip(entry)
            ip_all.append((bare_key, output_entry))

    # Dedup by bare key
    ip_dict = OrderedDict()
    for bare_key, output_entry in sorted(ip_all, key=lambda x: x[0]):
        ip_dict[bare_key] = output_entry

    ips = list(ip_dict.values())
    print(f"\n  total unique: {len(ips)}")

    ip_yaml = os.path.join(OUTPUT_DIR, "ChinaIP.yaml")
    write_yaml(ips, ip_yaml)

    ip_mrs = os.path.join(OUTPUT_DIR, "ChinaIP.mrs")
    compile_mrs(ip_yaml, "ipcidr", ip_mrs)

    # --- Summary ---
    print("\n" + "=" * 60)
    print("Summary:")
    for f in os.listdir(OUTPUT_DIR):
        fpath = os.path.join(OUTPUT_DIR, f)
        print(f"  {f}: {os.path.getsize(fpath)/1024:.1f} KB")
    print("=" * 60)


if __name__ == "__main__":
    main()
