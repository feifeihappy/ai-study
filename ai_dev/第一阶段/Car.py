class Car:
    """一个简单的汽车类"""

    # __init__ 是构造方法，在创建对象时自动调用
    def __init__(self, brand, color):
        # 初始化对象的属性
        self.brand = brand  # 品牌
        self.color = color  # 颜色
        self.speed = 0      # 速度，默认为0

    # 这是一个方法，定义了汽车的行为
    def drive(self):
        print(f"一辆{self.color}的{self.brand}正在行驶，当前速度是 {self.speed} km/h")

    # 另一个方法，用于加速
    def accelerate(self, amount):
        self.speed += amount
        print(f"{self.brand}加速了！当前速度: {self.speed} km/h")



# 1. 创建两个具体的汽车对象
# 这会触发 __init__ 方法，为 my_car 和 your_car 设置初始属性
my_car = Car("特斯拉", "白色")
your_car = Car("比亚迪", "黑色")

# 2. 访问对象的属性
print(my_car.brand)  # 输出: 特斯拉
print(your_car.color) # 输出: 黑色

# 3. 调用对象的方法
my_car.drive()       # 输出: 一辆白色的特斯拉正在行驶，当前速度是 0 km/h
your_car.drive()     # 输出: 一辆黑色的比亚迪正在行驶，当前速度是 0 km/h

my_car.accelerate(50) # 输出: 特斯拉加速了！当前速度: 50 km/h
my_car.drive()       # 输出: 一辆白色的特斯拉正在行驶，当前速度是 50 km/h



