# I2C驱动开发规范

版本: 2.1.0
更新: 2026-05-10

## 1. 初始化规范

### 1.1 标准初始化流程

```c
/**
 * I2C初始化 - 标准流程
 * @param instance I2C实例 (I2C1, I2C2, I2C3)
 * @param clock_speed 时钟速度 (100000, 400000)
 */
void i2c_init(I2C_TypeDef* instance, uint32_t clock_speed) {
    // 1. 使能时钟
    __HAL_RCC_I2C1_CLK_ENABLE();
    
    // 2. 配置GPIO
    GPIO_InitTypeDef gpio = {
        .Pin = GPIO_PIN_6 | GPIO_PIN_7,
        .Mode = GPIO_MODE_AF_OD,
        .Pull = GPIO_PULLUP,
        .Speed = GPIO_SPEED_FREQ_VERY_HIGH,
        .Alternate = GPIO_AF4_I2C1
    };
    HAL_GPIO_Init(GPIOB, &gpio);
    
    // 3. 初始化I2C
    I2C_HandleTypeDef hi2c = {
        .Instance = instance,
        .Init.ClockSpeed = clock_speed,
        .Init.DutyCycle = I2C_DUTYCYCLE_2,
        .Init.OwnAddress1 = 0,
        .Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT,
        .Init.DualAddressMode = I2C_DUALADDRESS_DISABLE,
        .Init.GeneralCallMode = I2C_GENERALCALL_DISABLE,
        .Init.NoStretchMode = I2C_NOSTRETCH_DISABLE
    };
    HAL_I2C_Init(&hi2c);
}
```

### 1.2 禁止在ISR中调用的函数

🚫 **禁止列表**:
- `HAL_I2C_Master_Transmit()` - 阻塞，不可在ISR中使用
- `HAL_Delay()` - 会阻塞系统
- 任何带有 `_IT` 后缀但不正确的函数

✅ **正确方式**: 使用DMA + 中断

## 2. 读写操作规范

### 2.1 标准读操作

```c
/**
 * I2C标准读操作
 * @param addr 设备地址 (7位)
 * @param reg 寄存器地址
 * @param data 数据缓冲区
 * @param len 数据长度
 * @retval HAL_StatusTypeDef
 */
HAL_StatusTypeDef i2c_read_reg(uint16_t addr, uint16_t reg, uint8_t* data, uint16_t len) {
    // 超时检测
    uint32_t tick = HAL_GetTick();
    
    // 发送寄存器地址
    if (HAL_I2C_Master_Transmit(&hi2c1, addr << 1, (uint8_t*)&reg, 1, 100) != HAL_OK) {
        return HAL_ERROR;
    }
    
    // 读取数据
    if (HAL_I2C_Master_Receive(&hi2c1, addr << 1 | 1, data, len, 100) != HAL_OK) {
        return HAL_ERROR;
    }
    
    return HAL_OK;
}
```

### 2.2 重试机制

```c
#define I2C_MAX_RETRIES 3

HAL_StatusTypeDef i2c_read_with_retry(uint16_t addr, uint16_t reg, uint8_t* data, uint16_t len) {
    for (int i = 0; i < I2C_MAX_RETRIES; i++) {
        if (i2c_read_reg(addr, reg, data, len) == HAL_OK) {
            return HAL_OK;
        }
        // 重试前等待
        HAL_Delay(10);
    }
    return HAL_ERROR;
}
```

## 3. 错误处理

### 3.1 错误码定义

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 0x01 | 总线忙 | 等待后重试 |
| 0x02 | 设备无应答 | 检查接线/地址 |
| 0x03 | 数据校验失败 | 重试读取 |

### 3.2 错误日志格式

```c
#define LOG_I2C_ERROR(op, addr, code) \
    printf("[I2C ERR] %s addr=0x%02X code=%d time=%lu\n", \
           op, addr, code, HAL_GetTick())
```

## 4. 相关文档

- 硬件配置: hardware_config.md
- SHT40驱动: sht40_driver.c
- 错误处理: error_handling.md
