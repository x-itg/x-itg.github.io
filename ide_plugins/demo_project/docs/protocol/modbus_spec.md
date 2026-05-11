# Modbus RTU 通信协议规范

版本: 3.0.0
更新: 2026-05-10

## 1. 协议概述

Modbus RTU 是工业广泛使用的通信协议，本项目用于与上位机通信。

### 帧格式

```
| 地址 | 功能码 | 数据 | CRC16 |
| 1字节 | 1字节 | N字节 | 2字节 |
```

### 支持的功能码

| 功能码 | 名称 | 说明 |
|--------|------|------|
| 0x03 | 读保持寄存器 | 读取传感器数据 |
| 0x06 | 写单个寄存器 | 设置参数 |
| 0x10 | 写多个寄存器 | 批量配置 |

## 2. 寄存器映射

### 2.1 保持寄存器 (0x0000 - 0x00FF)

| 地址 | 名称 | 类型 | 说明 |
|------|------|------|------|
| 0x0000 | TEMP_INT | INT16 | 内部温度 x100 |
| 0x0001 | TEMP_EXT | INT16 | 外部温度 x100 |
| 0x0002 | HUMIDITY | UINT16 | 湿度 x100 |
| 0x0003 | PRESSURE | UINT32 | 气压 Pa |
| 0x0005 | STATUS | UINT16 | 系统状态 |
| 0x0010 | DEVICE_ID | UINT16 | 设备ID |
| 0x0011 | FW_VERSION | UINT16 | 固件版本 |

### 2.2 示例帧

**读取温度 (0x03)**:
```
请求: 01 03 00 00 00 02 C4 0B
响应: 01 03 04 06 3C 09 D0 5A 38
```
解析: 温度 = (0x063C << 8 | 0x09D0) / 100 = 25.92°C

## 3. RS485配置

```c
#define MODBUS_SLAVE_ADDR   0x01
#define MODBUS_BAUDRATE     9600
#define MODBUS_TIMEOUT      1000  // ms

UART_HandleTypeDef huart2;

void modbus_init(void) {
    huart2.Instance = USART2;
    huart2.Init.BaudRate = MODBUS_BAUDRATE;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1;
    huart2.Init.Parity = UART_PARITY_NONE;
    huart2.Init.Mode = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;
    
    HAL_UART_Init(&huart2);
}
```

## 4. 超时处理

| 操作 | 超时时间 | 重试次数 |
|------|----------|----------|
| 读寄存器 | 1000ms | 3 |
| 写寄存器 | 1000ms | 3 |
| 批量写 | 2000ms | 2 |

## 5. CRC校验

```c
uint16_t modbus_crc16(uint8_t* data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    
    for (uint16_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    
    return crc;
}
```
