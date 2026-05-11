# 单元测试指南

版本: 0.5.0
最后更新: 2026-01-15
⚠️ **警告**: 文档已过期90天以上！

## 概述

本项目使用 Ceedling 进行嵌入式单元测试。

## 环境配置

### 必需工具

- Ruby 2.7+
- Ceedling 0.31+
- GCC for tests

### 安装

```bash
gem install ceedling
```

## 测试用例命名

```
test_<module>_<scenario>_<expected_result>.c
```

示例:
- `test_sht40_read_valid_data.c`
- `test_modbus_crc_calculation.c`

## 运行测试

```bash
ceedling test:all
ceedling test:coverage
ceedling verbosity[5]
```

## 覆盖率要求

| 模块 | 覆盖率目标 |
|------|------------|
| 驱动层 | 90% |
| 协议层 | 85% |
| 业务层 | 80% |

⚠️ **注意**: 当前覆盖率仅约60%，需要补充测试用例。
