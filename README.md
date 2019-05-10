# Fuck Login !

[![GitHub stars](https://img.shields.io/github/stars/IMWoolei/fuck-login.svg)](https://github.com/IMWoolei/fuck-login/stargazers)	[![GitHub forks](https://img.shields.io/github/forks/IMWoolei/fuck-login.svg)](https://github.com/IMWoolei/fuck-login/network)	[![GitHub issues](https://img.shields.io/github/issues/IMWoolei/fuck-login.svg)](https://github.com/IMWoolei/fuck-login/issues)	[![GitHub license](https://img.shields.io/github/license/IMWoolei/fuck-login.svg)](https://github.com/IMWoolei/fuck-login)	![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django.svg)	[![Email](https://img.shields.io/badge/email-Leo-orange.svg)](mailto:imwoolei@outlook.com)

### 1.介绍

#### 提供常见站点的模拟登陆

#### 前言

由于`xchaoinfo/fuck-login`的项目不再维护了，

所以利用业余时间参考`xchaoinfo`大神的代码重新做起一些常见站点的登录，希望一起交流学习。

#### 登陆方式

- 多数采用`requests`库创建会话`session`进行登陆
- 必要的`js`生成参数多采用`PyExecJS`，部分`js`代码过长会采用`Selenium`控制浏览器进行运行
- 尽量不采用`Selenium`进行自动化操作登陆
- 能力有限，水平一般。机器学习刚开始踩坑中，若登陆验证码的识别需要模型识别才能解决的话，暂时采用手动输入方案；若可通过`OCR`进行识别，会提提简单的处理思路。

### 2.程序结构

尽量每个登陆脚本采用相同的结构，希望能对执行流程的理解有所帮助。

```python
import requests


class LoginWebsiteName:
    """
    登录程序结构
    """
    # 登录操作会话对象
    session = requests.session()

    def __init__(self, username: str, password: str, **kwargs):
        self.username = username
        self.password = password
        pass

    def login(self) -> dict:
        """
        执行登录操作
        :return: `rtype:dict` 登录结果
        """
        pass

    def get_user_info(self) -> dict or None:
        """
        获取用户信息
        :return: 登录成功`rtype:dict`, 登录失败`rtype:None`
        """
        pass

    def get_login_cookies(self) -> dict:
        """
        获取用户登录后的cookies
        :return:
        """
        pass


if __name__ == '__main__':
    test_name = 'your username'
    test_password = 'your password'
    loginer = LoginWebsiteName(username=test_name, password=test_password)
    # 开始执行登录操作
    login_result = loginer.login()
    # 获取用户信息
    user_info = loginer.get_user_info()
    # 获取登录状态cookies
    cookies = loginer.get_login_cookies()
```

### 3. 已完成站点

- [x] 新浪微博
- [x] 今日头条
- [x] 搜狐新闻
- [x] 凤凰新闻
- [x] 豆瓣

### 4.写在最后

- 脚本还在逐渐完善添加中，欢迎大家提`Issues`、随意`Fork`，顺便再给个`Star`吧；
- 如果你觉得某个网站的登录很有代表性，欢迎在 `Issue `中提出，可以的话我会在之后的实现脚本中加入；
- 感谢女朋友，不知道为什么就是想感谢女朋友。





