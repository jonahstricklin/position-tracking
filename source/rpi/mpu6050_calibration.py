import mpu6050, time
mpu6050 = mpu6050.mpu6050(0x68)
start_time = time.time()

print("mpu6050 must remain motionless for calibration process...")

n = 0
accel_error = {"x": 0, "y": 0, "z": 0}
gyro_error = {"x": 0, "y": 0, "z": 0}

while (time.time() - start_time) < 10:
    print(time.time() - start_time)
    
    accel = mpu6050.get_accel_data()
    gyro = mpu6050.get_gyro_data()

    for axis in accel.keys():
        accel_error[axis] += accel[axis]
        gyro_error[axis] += gyro[axis]
    
    n += 1

avg_accel_offset = {"x": 0, "y": 0, "z": 0}
avg_gyro_offset = {"x": 0, "y": 0, "z": 0}

for axis in accel.keys():
    avg_accel_offset[axis] = accel_error[axis] / n
    avg_gyro_offset[axis] = gyro_error[axis] / n

print(avg_accel_offset)
print(avg_gyro_offset)