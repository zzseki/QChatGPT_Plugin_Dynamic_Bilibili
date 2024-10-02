## 安装

配置完成 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get <插件发布仓库地址>
```
或查看详细的[插件安装说明](https://github.com/RockChinQ/QChatGPT/wiki/5-%E6%8F%92%E4%BB%B6%E4%BD%BF%E7%94%A8)

## 使用

前往图床  https://sm.ms/  进行注册并获取token

在本插件文件夹下main.py文件中找到这行(大概在17行左右)，并替换成你获取到的token（不要弄丢引号）
```
api_token = 'YOUR_TOKEN'  # 请将这里的'YOUR_TOKEN'替换为你实际获取的token
```

## 配置

将main.py文件中找到这行(大概在145行左右)，并替换成需要推送动态的群号，当然你也可以将'group'改成'person'并将群号改成个人账号为你私人推送动态通知
```
await ctx.send_message(target_type='group', target_id=123456789, message=MessageChain([Image(url=image_url)]))
```

将dynamic.py文件中找到下面的部分(大概在17行左右)，并进行配置你的'User-Agent'和'SESSDATA'，具体如何获取请自行百度或ChatGPT(很简单)，强烈建议使用B站小号以防B站账号被官方认定为机器人
```
headers = {
        'User-Agent': '',
        'Referer': 'https://www.bilibili.com/',
        'Origin': 'https://www.bilibili.com',
        'Host': 'api.bilibili.com',
    }
    cookies = {
        'SESSDATA': '',
    }
```

## 注意

请不要随意删除path文件夹下的png图片，否则可能会导致重复推送动态
UID.txt中为你已关注的up主的UID
可对QQ机器人执行以下命令(请不要丢失'#'和'[]'符号否则无法识别)：
```
#开启动态推送
#关闭动态推送
#关注up[UID]
#取消关注up[UID]
```

注意：上述所有命令只可以私聊发送，在群聊中无法识别