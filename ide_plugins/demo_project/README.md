# 嵌入式温湿度监控系统

## 项目概述

基于 STM32 的工业级温湿度监控系统，支持 Modbus RTU 协议。

## 硬件配置

- MCU: STM32F407VG
- 传感器: SHT40 (I2C)
- 通信: RS485 (Modbus RTU)
- 显示: 0.96" OLED (SPI)

## 目录结构

```
demo_project/
├── docs/                   # 知识文档
├── src/                    # 源代码
├── tests/                  # 测试文件
└── hardware/               # 硬件相关
```
