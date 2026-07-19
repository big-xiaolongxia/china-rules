# China Rules

自动合并 [MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat)、[Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules)、[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 三源的中国大陆域名/IP 规则集，去重后发布。

## 下载

```
https://github.com/<你的用户名>/china-rules/releases/latest/download/ChinaDomain.yaml
https://github.com/<你的用户名>/china-rules/releases/latest/download/ChinaIP.yaml
https://github.com/<你的用户名>/china-rules/releases/latest/download/ChinaDomain.mrs
https://github.com/<你的用户名>/china-rules/releases/latest/download/ChinaIP.mrs
```

## 规则来源

### Domain（三源合并）
| 源 | 文件 | 条目 |
|----|------|:----:|
| MetaCubeX | geo/geosite/cn.yaml | ~111K |
| Loyalsoldier | direct.txt | ~112K |
| blackmatrix7 | ChinaTest_Domain.txt | ~112K |

### IPCIDR（三源合并）
| 源 | 文件 | 条目 |
|----|------|:----:|
| MetaCubeX | geo/geoip/cn.yaml | ~5.8K |
| Loyalsoldier | cncidr.txt | ~5.7K |
| blackmatrix7 | ChinaMax_IP.txt | ~6K |

## 更新

每周日 22:00（北京时间）自动更新。
