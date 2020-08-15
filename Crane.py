"""
This file contains the world model of the crane-group-control problem
"""
import math

class Crane(object):
    def __init__(self):
        super().__init__()
        self.x = 0          # 塔吊平面坐标
        self.y = 0

        # 状态变量
        self.theta = 0      # 角位置
        self.omega = 0      # 角速度
        self.alpha = 0      # 角加速度
        self.car_pos = 0    # 小车位置
        self.car_speed = 0  # 小车速度
        self.car_acceleration = 0   # 小车加速度
        self.hook_height = 0        # 吊钩高度（距离地面）
        self.hook_speed = 0         # 吊钩速度
        self.hook_acceleration = 0  # 吊钩加速度

        self.locked = False # 大臂制动
        self.load = 0       # 载重，假设不会超载
        self.rotate_friction_domain = False # 标记摩擦阻力是否超过了

        # 塔吊参数
        self.R1 = 0         # 大臂前端长度
        self.R2 = 0         # 大臂后端长度
        self.height = 0     # 大臂高度

        self.theta_limit = 10 * math.pi # 大臂转动角度限制
        self.car_limit_near_end = 0     # 小车近端距离限制
        self.car_limit_far_end = 0      # 小车远端距离限制

        self.basic_rotate_friction = 0  # 大臂转动的静摩擦力
        self.air_resistance_factor = 0  # 大臂转动空气阻力因数
        self.rotate_friction_load_factor = 0    # 大臂转动负载摩擦力因数
        self.basic_rotate_inertia = 0   # 塔机本身的转动惯量
        self.basic_car_friction = 0     # 小车运动的静摩擦力
        self.car_friction_load_factor = 0       # 小车运动负载摩擦力因数

        self.moment = [0, 100, 200, 300, 400, -400, -300, -200, -100]   # 各个挡位的转动力矩
        self.car_power = [0, 100, 200, 300, -300, -200, -100]           # 小车各个挡位的动力
        self.hook_power = [0, 100, 200, 300, -300, -200, -100]          # 吊钩各个挡位的动力

    def rotate(self, power, wind_direction=0, wind_speed=0):
        """
        operate the arm with certain power

        power: int, -4 to 4. the rotate power given by the motor to rotate the arm
        wind_direction: float, 0 to 2*pi. the direction where the wind comes
        wind_speed: float, 0 to ...100? the wind speed, which will affect the crane's rotate
        """
        if self.locked:
            return
        
        # 转动力矩来源于动力和风的作用
        M = self.moment[power] + self.getWindMoment(wind_direction, wind_speed)

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
        
        self.alpha = M / self.getRotateInertia()
    
    def moveCar(self, power):
        """
        operate the car with certain power

        power: int, -3 to 3. the power to drive the car
        """
        pass

    def moveHook(self, power):
        """
        operate the hook with certain power

        power: int, -3 to 3. the power to drive the hook
        """
        pass

    def update(self):
        """
        update all the physical state of the crane by the physical difference equation
        """
        pass
        
    def getWindMoment(self, wind_direction, wind_speed):
        """
        return the moment that the wind pushed on the crane
        """
        pass

    def getRotateFriction(self):
        """
        return the ABS of the rotate friction (including air resistance) according to the current speed and load
        """
        return self.basic_rotate_friction + abs(self.omega) * self.air_resistance_factor + self.load * self.rotate_friction_load_factor

    def getRotateInertia(self):
        """
        return the rotational inertia of the arm
        """
        return self.basic_rotate_inertia + self.load * (self.car_pos**2)

    def loadWeight(self, weight):
        """
        load with weight

        weight: float, 0 to MAX_WEIGHT. the weight to be loaded on the crane
        """
        if self.load == 0:
            self.load = weight
        else:
            print("ERROR: load new weight before unload!")
    
    def unloadWeight(self):
        """
        unload the load
        """
        if self.load > 0:
            self.load = 0
        else:
            print("ERROR: unload before load anythin!")