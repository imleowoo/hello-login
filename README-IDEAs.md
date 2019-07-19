## 各站点登陆实现思路

### 01 weibo-新浪微博

1. 登陆前有个预登陆请求，用于请求获取本次登录账号的加密信息；

2. 用户名和密码均进行了加密后提交；

   - 用户名：先进行`URL`编码后再进行`base64`编码

   - 密码：采用了`rsa`的对称加密，每次的加密信息包括混合的字符串，公钥等信息需要请求`ssologin.js`来获取

```python
    def _get_s_password(self, server_time, nonce, pubkey):
        """
        获取将密码加密后用于登录的字符串
        :return:
        """
        encode_password = (str(server_time) + "\t" + str(nonce) + "\n" + str(self.password)).encode("utf-8")
        public_key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        encry_password = rsa.encrypt(encode_password, public_key)
        password = binascii.b2a_hex(encry_password)
        return password.decode()
```

3. 验证码：五位字母+数字的带干扰线验证码。

   - 提供了一个新浪的验证码识别接口

     ```http
     # 新浪微博验证码识别接口，可在线测试
     # 识别准确率98%以上，可用于训练原始数据模型
     - API: http://captcha.faceme.site/sina
     - Method: POST (multipart/form-data)
     ```

   - 验证码使用示例脚本

     ```python
     import requests
     
     img_path = 'fake-path/captcha.png'  # 验证码图片地址
     file = {"captcha": ("captcha.png", open(img_path, 'rb'), "image/png")}
     resp = requests.post(url='http://captcha.faceme.site/sina', files=file)
     # print(resp.json())
     print(resp.text)
     ```

     

----

### 02 toutiao-今日头条

1. `Web`页面中，`PC`版登录存在滑动验证码。由于在本例程中避免使用`Selenium`进行操作，所以更换`User-Agent`采用移动端`Web`页面可以避免出现滑动验证码，与之代替的是图形验证码；

   ```python
   'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
   ```

2. 用户名和密码均未进行任何加密；

3. 通过移动端`Web`页面登录生成的`Cookies`信息可以直接在`PC-Web`页面上使用。



----

### 03 sohu-搜狐新闻

1. 搜狐新闻在`PC-Web`页面中进行登录时会出现验证码，而切换至移动端`Web`页面时不会产生验证码，所以可以通过移动`Web`界面进行登录完美的绕过验证码；

2. 用户名未加密，密码采用`md5`进行加密后提交。

   ```python
       def _get_password_md5(password):
           """
           密码的md5字符串
           :return:
           """
           return md5(password.encode(encoding='UTF-8')).hexdigest()
   ```



----

### 04 ifeng-凤凰新闻

1. 采用`PC-Web`页面完成，账号密码均未做加密处理；

2. 登陆需要验证码，验证码为4位数由字母+数字组成。

   ```http
   验证码链接：https://id.ifeng.com/public/authcode
   ```



-----

### 05 douban-豆瓣

1. 账号密码均未做任何加密处理，并且无验证码出现。



------

### 06 itouchtv-触电新闻媒体平台

1. 采用`PC-Web`页面完成，账号密码均未做加密处理；

2. 出这个站点的原因是因为在登录之后，进行其它操作时需要生成`sign`值需要进行两次加密，并且`GET`和`POST`请求生成`sign`方式不一致。

   - `sign`是由登录后获取的`token`，`useId`以及当前的`13位毫米时间戳`组合后，先经过`md5`加密后生成的`32`位字符串，再经过`sha1`加密生成`40`位字符串；

   - 如果是`POST`请求需要将`form-data`的数据转换成字典类型后根据`key`值排正序后，所有`key+value`拼接成字符串，一起混入进行加密生成`sign`

     ```python
     from hashlib import md5, sha1
     
     
     def get_sign(token, user_id, timestamp_ms):
         """
         GET请求时sign的生成方式
         :param token: 登录获取的token
         :param user_id: 登录可获取的userId
         :param timestamp_ms: 13位毫秒时间戳
         :return:
         """
         # get请求时明文字符串组成
         get_method_clear_text_format = '{token}{user_id}{timestamp_ms}'
         clear_text = get_method_clear_text_format.format(token=token, user_id=user_id, timestamp_ms=timestamp_ms)
         md5_text = md5(clear_text.encode(encoding='UTF-8')).hexdigest()
         sha1_text = sha1(md5_text.encode('utf-8')).hexdigest()
         return sha1_text
     
     
     def post_sign(token, user_id, timestamp_ms, post_form_data):
         """
         POST请求时sign的生成方式
         :param token: 登录获取的token
         :param user_id: 登录可获取的userId
         :param timestamp_ms: 13位毫秒时间戳
         :param post_form_data: POST请求时提交的表单数据
         :return:
         """
         # POST请求时明文字符串组成
         post_method_clear_text_format = '{token}{user_id}{content_str}{timestamp_ms}'
         # 将表单数据按key排序之后再组合成字符串
         sorted_items = sorted(post_form_data.items(), key=lambda t: t[0], reverse=False)
         content_str = ''.join([str(k) + str(v) for k, v in sorted_items])
         clear_text = post_method_clear_text_format.format(token=token, user_id=user_id, content_str=content_str, timestamp_ms=timestamp_ms)
         md5_text = md5(clear_text.encode(encoding='UTF-8')).hexdigest()
         sha1_text = sha1(md5_text.encode('utf-8')).hexdigest()
         return sha1_text
     
     ```

   

-----
   
### 07 github-GitHub

1. 采用`PC-Web`页面完成，账号密码均未做加密处理，且不需要验证码；
2. 登录需要提取隐藏表单中的`authenticity_token`
   
   ```html
   <form action="/session" accept-charset="UTF-8" method="post">
       <input name="utf8" type="hidden" value="&#x2713;"/>
       <input type="hidden" name="authenticity_token" value="rzuceXctjkBoZGUcxGwtNJsgd8bor3GSVHO3GsBMMNpfVNHRAassqVO6rUETWiaiFqW0EUdMBgl1qJAp3ppWlw=="/>
       <div class="auth-form-header p-0">
           <h1>Sign in to GitHub</h1>
       </div>
       <div id="js-flash-container"></div>
       <div class="auth-form-body mt-3">
           <label for="login_field">Username or email address
           </label>
           <input type="text" name="login" id="login_field" class="form-control input-block" tabindex="1" autocapitalize="off" autocorrect="off" autofocus="autofocus"/>
           <label for="password">
               Password <a class="label-link" href="/password_reset">Forgot password?</a>
           </label>
           <input type="password" name="password" id="password" class="form-control form-control input-block" tabindex="2"/>
           <input type="hidden" class="js-webauthn-support" name="webauthn-support" value="unknown">
           <input type="submit" name="commit" value="Sign in" tabindex="3" class="btn btn-primary btn-block" data-disable-with="Signing in…"/>
       </div>
   </form>
   ```
   
   
   
   
   
   
   
   