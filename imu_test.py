import smbus
import time

MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B

ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F

GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

bus = smbus.SMBus(1)

# Sensor aufwecken
bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)

def read_word_2c(reg):
    high = bus.read_byte_data(MPU_ADDR, reg)
    low = bus.read_byte_data(MPU_ADDR, reg + 1)
    value = (high << 8) + low

    if value >= 0x8000:
        value = -((65535 - value) + 1)

    return value

while True:
    acc_x = read_word_2c(ACCEL_XOUT_H)
    acc_y = read_word_2c(ACCEL_YOUT_H)
    acc_z = read_word_2c(ACCEL_ZOUT_H)

    gyro_x = read_word_2c(GYRO_XOUT_H)
    gyro_y = read_word_2c(GYRO_YOUT_H)
    gyro_z = read_word_2c(GYRO_ZOUT_H)

    print(f"ACC  X:{acc_x:6d}  Y:{acc_y:6d}  Z:{acc_z:6d}")
    print(f"GYRO X:{gyro_x:6d}  Y:{gyro_y:6d}  Z:{gyro_z:6d}")
    print("-" * 40)

    time.sleep(0.5)
