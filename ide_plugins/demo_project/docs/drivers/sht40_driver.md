# SHT40 温湿度传感器驱动

版本: 1.3.0
更新: 2026-05-08

## 概述

SHT40 是 Sensirion 推出的高精度温湿度传感器，支持 I2C 接口。

## 电气特性

| 参数 | 数值 |
|------|------|
| 供电电压 | 1.08 - 3.6V |
| I2C地址 | 0x44 (默认) |
| 温度精度 | ±0.2°C |
| 湿度精度 | ±1.5%RH |

## 驱动实现

### 初始化

```c
#include "sht40.h"

#define SHT40_I2C_ADDR     0x44
#define SHT40_CMD_MEASURE  0xFD

static I2C_HandleTypeDef* sht40_i2c;

HAL_StatusTypeDef sht40_init(I2C_HandleTypeDef* hi2c) {
    sht40_i2c = hi2c;
    
    // 发送软复位
    uint8_t cmd_reset = 0x94;
    if (HAL_I2C_Master_Transmit(sht40_i2c, SHT40_I2C_ADDR << 1, &cmd_reset, 1, 100) != HAL_OK) {
        return HAL_ERROR;
    }
    HAL_Delay(10);
    
    return HAL_OK;
}
```

### 读取数据

```c
HAL_StatusTypeDef sht40_read(float* temperature, float* humidity) {
    uint8_t cmd[1] = {SHT40_CMD_MEASURE};
    uint8_t data[6];
    
    // 发送测量命令
    if (HAL_I2C_Master_Transmit(sht40_i2c, SHT40_I2C_ADDR << 1, cmd, 1, 100) != HAL_OK) {
        return HAL_ERROR;
    }
    
    // 等待测量完成
    HAL_Delay(10);
    
    // 读取数据
    if (HAL_I2C_Master_Receive(sht40_i2c, SHT40_I2C_ADDR << 1 | 1, data, 6, 100) != HAL_OK) {
        return HAL_ERROR;
    }
    
    // 解析温度 (Big Endian)
    uint16_t temp_raw = (data[0] << 8) | data[1];
    *temperature = -45.0f + 175.0f * ((float)temp_raw / 65535.0f);
    
    // 解析湿度 (Big Endian)
    uint16_t hum_raw = (data[3] << 8) | data[4];
    *humidity = 100.0f * ((float)hum_raw / 65535.0f);
    
    return HAL_OK;
}
```

## 使用示例

```c
void sensor_task(void* params) {
    float temp, hum;
    
    while (1) {
        if (sht40_read(&temp, &hum) == HAL_OK) {
            printf("Temp: %.2f°C, Hum: %.2f%%\n", temp, hum);
            
            // 检查异常值
            if (temp < -40 || temp > 125) {
                // 报警处理
                error_handler(ERR_SENSOR_RANGE);
            }
        } else {
            // I2C错误处理
            error_handler(ERR_I2C_TIMEOUT);
        }
        
        osDelay(1000);
    }
}
```

## 注意事项

1. ⚠️ I2C地址为0x44，不是0x45
2. ⚠️ 测量命令后需要等待至少10ms
3. ⚠️ 数据校验CRC不正确时应丢弃数据
