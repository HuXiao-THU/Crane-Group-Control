"""
This file contains the world model of the crane-group-control problem
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
        self.hook_height = 0        # 吊钩高度（距离地面）
        self.hook_speed = 0         # 吊钩速度
        # self.hook_acceleration = 0  # 吊钩加速度

        self.locked = False # 大臂制动，用于考虑大风的场景
        self.load = 0       # 载重，假设不会超载
        # self.weightID = 0   # 记录所载货物的ID
        self.rotate_friction_domain = False # 标记摩擦阻力是否超过了动力，方便计算是否会停下（程序精度不够）
        self.car_friction_domain = False    # 同上，用于小车

        # 塔吊物理参数
        self.R1 = 0         # 大臂前端长度
        self.R2 = 0         # 大臂后端长度
        self.height = 100.0     # 大臂下侧高度

        self.theta_limit = 10 * math.pi # 大臂转动角度限制
        self.car_limit_near_end = 0     # 小车近端距离限制
        self.car_limit_far_end = 0      # 小车远端距离限制
        self.min_load = 0               # 最小载重量
        self.max_load = 3000.0          # 最大载重量

        self.basic_rotate_friction = 0  # 大臂转动的静摩擦力
        self.air_resistance_factor = 0  # 大臂转动空气阻力因数
        self.rotate_friction_load_factor = 0    # 大臂转动负载摩擦力因数
        self.basic_rotate_inertia = 0   # 塔机本身的转动惯量
        self.basic_car_friction = 0     # 小车运动的静摩擦力
        self.car_friction_load_factor = 0       # 小车运动负载摩擦力因数
        self.car_mass = 0               # 小车本身质量

        self.moment = [0, 100, 200, 300, 400, -400, -300, -200, -100]   # 各个挡位的转动力矩
        self.car_power = [0, 100, 200, 300, -300, -200, -100]           # 小车各个挡位的动力
        self.hook_power = [0, 0.05, 0.10, 0.15, -0.15, -0.10, -0.05]    # 吊钩各个挡位的速度

    def rotate(self, power, wind_direction=0, wind_speed=0):
        """
        operate the arm with certain power

        power: int, -4 to 4. the rotate power given by the motor to rotate the arm
        wind_direction: float, 0 to 2*pi. the direction where the wind comes
        wind_speed: float, 0 to ...100? the wind speed, which will affect the crane's rotate
        """
        if self.locked:
            return
        
        # 转动力矩来源于动力和风的作用，暂时先不考虑风的作用
        M = self.moment[power] # + self.getWindMoment(wind_direction, wind_speed)

        # 减去摩擦力
        if self.omega != 0:
            if abs(M) < self.getRotateFriction():   # 标记一下阻力是否大于动力，方便克服程序精度问题而判断旋转是否会停下
                self.rotate_friction_domain = True
            else:
                self.rotate_friction_domain = False
            if M > 0:
                M = M - self.getRotateFriction()
            else:
                M = M + self.getRotateFriction()
        else:
            if M > 0:
                M = max(M - self.getRotateFriction(), 0)
            else:
                M = min(M + self.getRotateFriction(), 0)
        
        self.arm_alpha = M / self.getRotateInertia()
    
    def moveCar(self, power, wind_direction=0, wind_speed=0):
        """
        operate the car with certain power

        power: int, -3 to 3. the power to drive the car
        wind_direction: float, 0 to 2*pi. the direction where the wind comes
        wind_speed: float, 0 to ...100? the wind speed, which will affect the crane's rotate
        """
        F = self.car_power[power]   # 暂时不考虑风会吹动小车的可能性

        if self.car_speed != 0:
            if abs(F) < self.getCarFraction():
                self.car_friction_domain = True
            else:
                self.car_friction_domain = False
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

        power: int, -3 to 3. the power to drive the hook
        """
        self.hook_speed = self.hook_power[power]

    def update(self, dt):
        """
        update all the physical state of the crane by the physical difference equation

        dt: positive float. the time difference to update the states, the lower the better
        """
        # arm
        if not self.locked:
            self.arm_theta += self.arm_omega * dt
            if self.rotate_friction_domain:
                original_sign = np.sign(self.arm_omega)
                self.arm_omega += self.arm_alpha * dt
                if original_sign != np.sign(self.arm_omega):
                    self.arm_omega = 0
            else:
                self.arm_omega += self.arm_alpha * dt
            
        # car
        self.car_pos += self.car_speed * dt
        if self.car_friction_domain:
            original_sign = np.sign(self.car_speed)
            self.car_speed += self.car_acceleration * dt
            if original_sign != np.sign(self.car_speed):
                self.car_speed = 0
        else:
            self.car_speed += self.car_acceleration * dt

        # hook
        self.hook_height += self.hook_speed * dt
        
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

    def loadWeight(self, weight, weightID):
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