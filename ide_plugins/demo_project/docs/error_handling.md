# 错误处理规范

版本: 1.1.0
最后更新: 2026-02-28
⚠️ **警告**: 此文档与代码存在不一致，请勿直接使用！

## 1. 错误码定义

### 1.1 系统错误码 (0x0000-0x00FF)

| 错误码 | 名称 | 严重级 | 说明 |
|--------|------|--------|------|
| 0x00 | OK | INFO | 正常 |
| 0x01 | ERR_INIT | FATAL | 初始化失败 |
| 0x02 | ERR_WDT | FATAL | 看门狗超时 |
| 0x03 | ERR_STACK | FATAL | 栈溢出 |

### 1.2 I2C错误码 (0x0100-0x01FF)

| 错误码 | 名称 | 严重级 | 说明 |
|--------|------|--------|------|
| 0x0100 | ERR_I2C_BUSY | ERROR | 总线忙 |
| 0x0101 | ERR_I2C_NACK | ERROR | 设备无应答 |
| 0x0102 | ERR_I2C_TIMEOUT | ERROR | 通信超时 |
| 0x0103 | ERR_I2C_CRC | ERROR | CRC校验失败 |

### 1.3 传感器错误码 (0x0200-0x02FF)

| 错误码 | 名称 | 严重级 | 说明 |
|--------|------|--------|------|
| 0x0200 | ERR_SENSOR_INIT | ERROR | 传感器初始化失败 |
| 0x0201 | ERR_SENSOR_READ | ERROR | 读取失败 |
| 0x0202 | ERR_SENSOR_RANGE | WARNING | 数据超范围 |
| 0x0203 | ERR_SENSOR_CRC | ERROR | 校验失败 |

### 1.4 通信错误码 (0x0300-0x03FF)

| 错误码 | 名称 | 严重级 | 说明 |
|--------|------|--------|------|
| 0x0300 | ERR_MODBUS_TIMEOUT | ERROR | Modbus超时 |
| 0x0301 | ERR_MODBUS_CRC | ERROR | CRC错误 |
| 0x0302 | ERR_MODBUS_FRAME | ERROR | 帧格式错误 |

## 2. 严重级别定义

| 级别 | 值 | 处理方式 | 指示灯 |
|------|-----|----------|--------|
| DEBUG | 0 | 仅日志 | - |
| INFO | 1 | 仅日志 | 绿色闪烁 |
| WARNING | 2 | 日志+警告 | 绿色快闪 |
| ERROR | 3 | 日志+告警 | 红色慢闪 |
| FATAL | 4 | 日志+复位 | 红色快闪 |

## 3. 看门狗配置

⚠️ **错误**: 文档说2000ms，实际代码使用3000ms！

```c
// 文档值: 2000ms
#define WDT_TIMEOUT 2000

// 实际代码使用:
// #define WDT_TIMEOUT 3000
```

## 4. 错误处理流程

```c
void error_handler(uint16_t error_code) {
    // 1. 记录错误
    log_error(error_code);
    
    // 2. 根据严重级别处理
    switch (error_code & 0xFF00) {
        case 0x0000:  // 系统错误
            if ((error_code & 0xFF) >= 0x02) {
                // 触发系统复位
                NVIC_SystemReset();
            }
            break;
        case 0x0100:  // I2C错误
            // 尝试重新初始化
            i2c_reinit();
            break;
        // ...
    }
    
    // 3. 更新指示灯
    update_led_status(error_code);
}
```

## 5. 错误日志格式

```
[YYYY-MM-DD HH:MM:SS.mmm] [LEVEL] [TID] CODE:0x%04X MSG:%s
```

示例:
```
[2026-05-10 14:30:15.123] [ERROR] [T:1] CODE:0x0102 I2C通信超时
```
