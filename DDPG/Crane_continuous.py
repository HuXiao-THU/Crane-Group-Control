"""
This file contains the world model of the crane-group-control problem
The crane control will be modeled in continuous format
"""
import math
import numpy as np

class Crane(object):
    def __init__(self):
        super().__init__()
        self.x = 0          # 塔吊平面坐标
        self.y = 0

        # 状态变量
        self.arm_theta = 0      # 角位置
        self.arm_omega = 0      # 角速度
        self.arm_alpha = 0      # 角加速度
        self.car_pos = 0    # 小车位置
        self.car_speed = 0  # 小车速度
        self.car_acceleration = 0   # 小车加速度
        self.hook_height = 0        # 吊钩底高度（距离地面）
        self.hook_speed = 0         # 吊钩速度
        # self.hook_acceleration = 0  # 吊钩加速度

        self.locked = False # 大臂制动，用于考虑大风的场景
        self.load = 0       # 载重，假设不会超载
        # self.weightID = 0   # 记录所载货物的ID
        self.rotate_friction_domain = False # 标记摩擦阻力是否超过了动力，方便计算是否会停下（程序精度不够）
        self.car_friction_domain = False    # 同上，用于小车

        # 塔吊物理参数
        self.R1 = 35         # 大臂前端长度
        self.R2 = 10         # 大臂后端长度
        self.height = 25.0     # 大臂下侧高度
        self.hook_length = 0.6  # 吊钩的长度（竖向）

        self.theta_limit = 10 * math.pi # 大臂转动角度限制
        self.car_limit_near_end = 2.5     # 小车近端距离限制
        self.car_limit_far_end = 30.0      # 小车远端距离限制
        self.min_load = 10               # 最小载重量
        self.max_load = 800.0          # 最大载重量

        self.basic_rotate_friction = 30.0  # 大臂转动的静摩擦力
        self.air_resistance_factor = 300.0  # 大臂转动空气阻力因数
        self.rotate_friction_load_factor = 0.1    # 大臂转动负载摩擦力因数
        self.basic_rotate_inertia = 1e3   # 塔机本身的转动惯量
        self.basic_car_friction = 5.0     # 小车运动的静摩擦力
        self.car_friction_load_factor = 0.1       # 小车运动负载摩擦力因数
        self.car_mass = 500.0               # 小车本身质量
        self.car_speed_limit = 0.1          # 小车前后移动最大速度

        # 最大动力输出
        self.max_moment = 200.0
        self.max_car_power = 5000.0
        self.max_hook_speed = 0.1

        # 用于计算reward，暂不考虑
        self.rotate_power_factor = 200  # 转动电力最大消耗
        self.car_power_factor = 100     # 小车电力最大消耗
        self.hook_power_factor = 100    # 吊钩电力最大消耗

    def rotate(self, power, wind_direction=0, wind_speed=0):
        """
        operate the arm with certain power

        power: float, -1 to 1. the rotate power given by the motor to rotate the arm
        wind_direction: float, 0 to 2*pi. the direction where the wind comes
        wind_speed: float, 0 to ...100? the wind speed, which will affect the crane's rotate
        """
        if self.locked:
            return
        
        # 转动力矩来源于动力和风的作用，暂时先不考虑风的作用
        M = self.max_moment * power # + self.getWindMoment(wind_direction, wind_speed)
        # print("\nM: {:.3f}, friction: {:.3f}".format(M, self.getRotateFriction()))

        # 减去摩擦力
        if abs(M) < self.getRotateFriction():   # 标记一下阻力是否大于动力，方便克服程序精度问题而判断旋转是否会停下
            self.rotate_friction_domain = True
        else:
            self.rotate_friction_domain = False
        if self.arm_omega != 0:
            if M > 0:
                M = M - self.getRotateFriction()
            else:
                M = M + self.getRotateFriction()
        else:
            if M > 0:
                M = max(M - self.getRotateFriction(), 0)
            else:
                M = min(M + self.getRotateFriction(), 0)
        
        # print("M_real: {:.3f}".format(M))
        self.arm_alpha = M / self.getRotateInertia()
    
    def moveCar(self, power, wind_direction=0, wind_speed=0):
        """
        operate the car with certain power

        power: float, -1 to 1. the power to drive the car
        wind_direction: float, 0 to 2*pi. the direction where the wind comes
        wind_speed: float, 0 to ...100? the wind speed, which will affect the crane's rotate
        """
        F = self.max_car_power * power   # 暂时不考虑风会吹动小车的可能性

        if abs(F) < self.getCarFraction():
            self.car_friction_domain = True
        else:
            self.car_friction_domain = False

        if self.car_speed != 0:
            if F > 0:
                F = F - self.getCarFraction()
            else:
                F = F + self.getCarFraction()
        else:
            if F > 0:
                F = max(F - self.getCarFraction(), 0)
            else:
                F = min(F + self.getCarFraction(), 0)
        
        self.car_acceleration = F / (self.car_mass + self.load)

    def moveHook(self, power):
        """
        operate the hook with certain power
        to simplify the model, here we directly use set the hook's speed

        power: float, -1 to 1. the power to drive the hook
        """
        self.hook_speed = self.max_hook_speed * power

    def update(self, dt):
        """
        update all the physical state of the crane by the physical difference equation

        dt: positive float. the time difference to update the states, the lower the better
        """
        # arm
        if not self.locked:
            self.arm_theta += self.arm_omega * dt
            # 限位
            if abs(self.arm_theta) > self.theta_limit:
                self.arm_theta = np.sign(self.arm_theta) * self.theta_limit
                self.arm_omega = 0.0

            if self.rotate_friction_domain:
                original_sign = np.sign(self.arm_omega)
                self.arm_omega += self.arm_alpha * dt
                if original_sign != np.sign(self.arm_omega):
                    self.arm_omega = 0.0
            else:
                self.arm_omega += self.arm_alpha * dt
            
        # car
        self.car_pos += self.car_speed * dt
        # 小车限位
        if self.car_pos > self.car_limit_far_end:
            self.car_pos = self.car_limit_far_end
            self.car_speed = 0.0
        if self.car_pos < self.car_limit_near_end:
            self.car_pos = self.car_limit_near_end
            self.car_speed = 0.0

        # 小车限速
        if abs(self.car_speed) >= self.car_speed_limit:
            if np.sign(self.car_acceleration) == np.sign(self.car_speed):
                self.car_acceleration = 0.0
            self.car_speed = np.sign(self.car_speed) * self.car_speed_limit
            

        if self.car_friction_domain:
            original_sign = np.sign(self.car_speed)
            self.car_speed += self.car_acceleration * dt
            if original_sign != np.sign(self.car_speed):
                self.car_speed = 0
        else:
            self.car_speed += self.car_acceleration * dt

        # hook
        self.hook_height += self.hook_speed * dt
        if self.hook_height > self.height - self.hook_length:
            self.hook_height = self.height - self.hook_length
        if self.hook_height < 0.0:
            self.hook_height = 0.0
    
    def getSpeed(self):
        """
        return the speed of the hook(load)
        """
        x_1 = self.car_speed * math.cos(self.arm_theta) - self.car_pos * math.sin(self.arm_theta) * self.arm_omega
        y_1 = self.car_speed * math.sin(self.arm_theta) + self.car_pos * math.cos(self.arm_theta) * self.arm_omega
        z_1 = self.hook_speed
        speed = (x_1**2 + y_1**2 + z_1**2)**0.5
        return speed

    def getWindMoment(self, wind_direction, wind_speed):
        """
        return the moment that the wind pushed on the crane
        """
        # TODO
        pass

    def getRotateFriction(self):
        """
        return the ABS of the rotate friction (including air resistance) according to the current speed and load
        """
        return self.basic_rotate_friction + abs(self.arm_omega) * self.air_resistance_factor + self.load * self.rotate_friction_load_factor

    def getRotateInertia(self):
        """
        return the rotational inertia of the arm
        """
        return self.basic_rotate_inertia + self.load * (self.car_pos**2)

    def getCarFraction(self):
        """
        return the friction of the car
        """
        return self.basic_car_friction + self.load * self.car_friction_load_factor

    def loadWeight(self, weight, weightID=0):
        """
        load with weight

        weight: float, 0 to MAX_WEIGHT. the weight to be loaded on the crane
        """
        if self.load == 0:
            self.load = weight
            self.weightID = weightID
        else:
            print("ERROR: load new weight before unload!")
    
    def unloadWeight(self):
        """
        unload the load
        """
        if self.load > 0:
            self.load = 0
            self.weightID = None
        else:
            print("ERROR: unload before load anythin!")