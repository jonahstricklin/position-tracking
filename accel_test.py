import mpu6050, time
mpu6050 = mpu6050.mpu6050(0x68)

accel_offset = {'x': -1.2631961061185335, 'y': 0.0016973226763842004, 'z': 9.830343885448244}

while True:
    accel = mpu6050.get_accel_data()
    for axis in accel.keys():
        accel[axis] = (accel[axis] - accel_offset[axis])
    print(accel)
    time.sleep(0.1)