# China Rules

自动合并 **4 个 domain 源 + 4 个 IP 源** 的中国大陆域名/IP 规则集，去重后通过 GitHub Release 发布。

## 下载

```
https://github.com/<你的用户名>/china-rules/releases/latest/download/ChinaDomain.yaml
https://github.com/<你的用户名>/china-rules/releases/latest/download/ChinaIP.yaml
https://github.com/<你的用户名>/china-rules/releases/latest/download/ChinaDomain.mrs
https://github.com/<你的用户名>/china-rules/releases/latest/download/ChinaIP.mrs
```

## 规则来源

### Domain（4 源合并）

| 源 | 获取方式 | 说明 |
|----|---------|------|
| **v2dat 提取 geosite:cn** | `geosite.dat` → v2dat unpack | 含 `12306.cn` 等 v2fly 原始条目 |
| **MetaCubeX** | `geo/geosite/cn.yaml` | v2fly 编译版 YAML |
| **Loyalsoldier** | `direct.txt` | 112K 条商业域名 |
| **blackmatrix7** | `ChinaTest_Domain.txt` | 112K 条显式域名 |

### IPCIDR（4 源合并）

| 源 | 获取方式 |
|----|---------|
| **v2dat 提取 geoip:cn** | `geoip.dat` → v2dat unpack |
| **MetaCubeX** | `geo/geoip/cn.yaml` |
| **Loyalsoldier** | `cncidr.txt` |
| **blackmatrix7** | `ChinaMax_IP.txt` |

## Domain 输出格式

- `+.example.com` → DOMAIN-SUFFIX（匹配域名及所有子域名）
- `example.com` → DOMAIN 精确匹配（来自 v2dat `full:` 规则，仅此域名不含子域名）

## 更新

每周日 22:00（北京时间）自动更新。
