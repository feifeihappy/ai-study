# Python 基础笔记

## 列表推导式

列表推导式是 Python 创建列表的简洁方式，比 for 循环更高效。

```python
# 普通写法
squares = []
for i in range(10):
    squares.append(i ** 2)

# 推导式写法
squares = [i ** 2 for i in range(10)]
```

**为什么更快？** 推导式在 C 层面执行，避免了每次迭代调用 append 方法的开销。

## 装饰器

装饰器本质是一个接受函数、返回函数的高阶函数。用于在不修改原函数的前提下增加功能。

```python
def timer(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)

slow_function()  # 输出: slow_function 耗时: 1.00s
```

常见用途：日志记录、性能计时、权限校验、缓存。

## 上下文管理器

`with` 语句背后的协议：`__enter__` 和 `__exit__`。确保资源被正确释放。

```python
with open("file.txt") as f:
    content = f.read()
# f 在这里自动关闭，即使 read() 抛异常也会关闭
```
