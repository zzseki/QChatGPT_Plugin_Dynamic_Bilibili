import json
import os
import re
import time
from PIL import Image, ImageDraw, ImageOps
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def get_information(UID):
    url = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space'
    params = {
        'host_mid': UID
    }

    # 添加头信息
    headers = {
        'User-Agent': '',
        'Referer': 'https://www.bilibili.com/',
        'Origin': 'https://www.bilibili.com',
        'Host': 'api.bilibili.com',
    }
    cookies = {
        'SESSDATA': '',
    }

    response = requests.get(url, params=params, headers=headers, cookies=cookies, verify=False)

    # 如果成功获取数据，输出内容
    if response.status_code == 200:
        data = response.json()
        try:
            i = 0
            is_top = data['data']['items'][i]['modules']['module_tag']['text']
            while is_top == "置顶":
                i += 1
                try:
                    is_top = data['data']['items'][i]['modules']['module_tag']['text']
                    if is_top == "置顶":
                        continue
                    else:
                        print(f"已忽略{i}条置顶动态")
                        break
                except:
                    print(f"已忽略{i}条置顶动态")
                    break
        except:
            print("无置顶动态")
        id = data['data']['items'][i]['id_str']
        base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "path")
        path = os.path.join(base_path, f"{id}.png")
        if os.path.exists(path):
            print("未更新动态")
            # print("等待1分钟再次执行")
            # time.sleep(60)
            # continue
            return
        try:
            if data['data']['items'][i]['modules']['module_dynamic']['desc']['text']:
                dynamic_text = data['data']['items'][i]['modules']['module_dynamic']['desc']['text']
                print("原动态文本:", dynamic_text)
        except:
            dynamic_text = None
            print("无动态文本")
        try:
            if data['data']['items'][i]['modules']['module_dynamic']['desc']['rich_text_nodes']:
                items_list = data['data']['items'][i]['modules']['module_dynamic']['desc']['rich_text_nodes']
                emoji_list = [node['emoji']['icon_url'] for node in items_list if 'emoji' in node]
                emoji_list_text = [node['emoji']['text'] for node in items_list if 'emoji' in node]
                print("动态文本表情 URL:", emoji_list, emoji_list_text)
        except:
            emoji_list = None
            emoji_list_text = None
            print("无动态文本表情")
        try:
            if data['data']['items'][i]['modules']['module_dynamic']['major']['archive']['cover']:
                cover_url = data['data']['items'][i]['modules']['module_dynamic']['major']['archive']['cover']
                print("视频封面 URL:", cover_url)
        except:
            cover_url = None
            print("无视频封面")
        try:
            if data['data']['items'][i]['modules']['module_dynamic']['major']['archive']['title']:
                video_title = data['data']['items'][i]['modules']['module_dynamic']['major']['archive']['title']
                print("视频标题:", video_title)
        except:
            video_title = None
            print("无视频标题")
        try:
            if data['data']['items'][i]['modules']['module_dynamic']['major']['archive']['desc']:
                description = data['data']['items'][i]['modules']['module_dynamic']['major']['archive']['desc']
                print("视频简介:", description)
        except:
            description = None
            print("无视频简介")
        try:
            if data['data']['items'][i]['modules']['module_dynamic']['major']['draw']['items']:
                items_list = data['data']['items'][i]['modules']['module_dynamic']['major']['draw']['items']
                src_list = [item['src'] for item in items_list if 'src' in item]
                print("动态图片 URL:", src_list)
        except:
            src_list = None
            print("无动态图片")
        try:
            if data['data']['items'][i]['modules']['module_dynamic']['major']['live_rcmd']['content']:
                live = data['data']['items'][i]['modules']['module_dynamic']['major']['live_rcmd']['content']
                # 解析 JSON 字符串
                live_data = json.loads(live)
                live_cover_url = live_data['live_play_info']['cover']
                live_title = live_data['live_play_info']['title']
                print("直播封面 URL:", live_cover_url)
                print("直播标题:", live_title)
        except:
            live_cover_url = None
            live_title = None
        username_url = data['data']['items'][i]['modules']['module_author']['face']  # 头像
        username = data['data']['items'][i]['modules']['module_author']['name']  # 用户名名称
        pub_action = data['data']['items'][i]['modules']['module_author']['pub_action']
        pub_time = data['data']['items'][i]['modules']['module_author']['pub_time']
        # pub_action :投稿了视频\直播了\投稿了文章\更新了合集\与他人联合创作\发布了动态视频\投稿了直播回放
        # pub_time :更新时间
        if pub_action == '':
            pub_text = pub_time
        elif pub_time == '':
            pub_text = pub_action
        else:
            pub_text = pub_time + "·" + pub_action
        print("更新时间,更新动作描述:", pub_text)
        # 加载头像图片和视频封面图片
        response = requests.get(username_url)
        avatar_image = Image.open(BytesIO(response.content))  # 头像
        if cover_url is not None:
            response = requests.get(cover_url)
            cover_image = Image.open(BytesIO(response.content))
            cover_image = cover_image.resize((int(cover_image.width // 3.5), int(cover_image.height // 4)))  # 视频封面缩小
            cover_image = create_rounded_rectangle_image(cover_image, 10)
        # 缩小头像图片为五分之一
        avatar_image = avatar_image.resize((avatar_image.width // 5, avatar_image.height // 5))
        # 将头像转换为圆形
        avatar_image = create_circle_image(avatar_image)

        # 创建背景图片的宽度和高度
        desired_width = 1000  # 替换为所需的宽度
        desired_height = 400  # 替换为所需的高度

        # 创建背景图片
        background = Image.new('RGB', (desired_width, desired_height), color='white')

        # 创建一个绘图对象
        draw = ImageDraw.Draw(background)

        # 加载支持中文的字体并设置文本样式
        font_size = 25  # 替换为所需的字体大小
        font_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "msyh.ttc")  # 替换为支持中文的字体路径
        font_cu = ImageFont.truetype(font_path, font_size)
        font_xi = ImageFont.truetype(font_path, 20)

        # 将头像图片粘贴到背景图片的指定位置
        x_avatar = 50  # 头像的x坐标
        y_avatar = 30  # 头像的y坐标
        avatar_position = (x_avatar, y_avatar)
        background.paste(avatar_image, avatar_position)

        # 添加用户名到背景图片上
        username = username  # 视频标题
        x_position = 150  # 文本的x坐标
        y_position = 30  # 文本的y坐标
        draw.text((x_position, y_position), username, font=font_cu, fill='black')

        # 添加更新时间,更新动作描述到背景图片上
        x_position = 150  # 文本的x坐标
        y_position = 80  # 文本的y坐标
        draw.text((x_position, y_position), pub_text, font=font_xi, fill=(169, 169, 169))

        if dynamic_text is not None:
            # 添加动态文本内容到背景图片上
            x_position = 80  # 文本的x坐标
            y_position += 50  # 将 y 坐标向下移动
            i = 0
            for line in dynamic_text.split('\n'):
                if emoji_list is not None and emoji_list_text is not None and len(emoji_list) != 0:
                    if re.search(emoji_list_text[i], line):
                        new_line = re.sub(re.escape(emoji_list_text[i]), '', line)
                        y_position += 30
                        response = requests.get(emoji_list[i])
                        emoji_image = Image.open(BytesIO(response.content))
                        emoji_image = emoji_image.resize(
                            (int(emoji_image.width // 1.8), int(emoji_image.height // 1.8)))
                        if emoji_image.mode == 'RGBA':
                            # 创建一个白色背景的新图像
                            white_background = Image.new("RGB", emoji_image.size, (255, 255, 255))
                            # 将原图像粘贴到白色背景上，使用 alpha 通道作为透明度掩码
                            white_background.paste(emoji_image, (0, 0), emoji_image)
                            emoji_image = white_background
                        draw.text((x_position, y_position), new_line, font=font_cu, fill='black')
                        avatar_position = (x_position + 25 * len(new_line), y_position - 60)
                        background.paste(emoji_image, avatar_position)
                        i = min(i + 1, len(emoji_list) - 1)
                    else:
                        draw.text((x_position, y_position), line, font=font_cu, fill='black')
                else:
                    draw.text((x_position, y_position), line, font=font_cu, fill='black')
                y_position += 40  # 每行文本之间的间距

        if video_title is not None:
            # 添加视频标题到背景图片上
            x_position = 70 + cover_image.width  # 文本的x坐标
            y_position += 20  # 文本的y坐标
            y_line_position = y_position
            if cover_url is not None:
                # 将视频封面图片粘贴到背景图片的指定位置
                cover_position = (50, y_position)
                background.paste(cover_image, cover_position)
            len_video_title = 0
            for line in video_title.split('\n'):
                draw.text((x_position, y_position), line, font=font_cu, fill='black')
                y_position += 35  # 每行文本之间的间距
                len_video_title = max(x_position + len(line) * 30, len_video_title)
            if description is not None:
                # 添加视频简介到背景图片上
                y_position += 40  # 将 y 坐标向下移动
                len_description = 0
                i = 0
                for line in description.split('\n'):
                    if i > 2:
                        draw.text((x_position, y_position), "......", font=font_xi, fill=(169, 169, 169))
                        break
                    draw.text((x_position, y_position), line, font=font_xi, fill=(169, 169, 169))
                    y_position += 25  # 每行文本之间的间距
                    i += 1
                    len_description = max(x_position + len(line) * 30, len_description)

            # 添加边框
            border_width = 1  # 边框宽度
            draw.rectangle(
                [49, y_line_position - 1, max(len_video_title, len_description) + 15,
                 y_line_position + cover_image.height + 1],
                outline=(169, 169, 169),  # 边框颜色
                width=border_width  # 边框宽度
            )
            y_position = y_line_position + cover_image.height + 1
        # 添加动态图片
        if src_list is not None:
            i = 1
            x_position = 50
            y_position += 10
            image = None
            for url in src_list:
                if i % 2 == 0:
                    x_position += image.width + 5
                if i % 2 != 0 and i != 1:
                    x_position = 50
                    y_position += image.height + 5
                response = requests.get(url)
                image = Image.open(BytesIO(response.content))
                image = cropped_image(image)
                image = create_rounded_rectangle_image(image, 10)
                avatar_position = (x_position, y_position)
                background.paste(image, avatar_position)
                i += 1
            y_position += image.height + 5
        if live_title is not None:
            x_position = 50
            y_position += 50
            draw.text((x_position, y_position), live_title, font=font_cu, fill='black')
        if live_cover_url is not None:
            y_position += 50
            response = requests.get(live_cover_url)
            live_image = Image.open(BytesIO(response.content))
            # live_image = cropped_image(live_image, 470, 265)
            live_image = create_rounded_rectangle_image(live_image, 10)
            avatar_position = (x_position, y_position)
            background.paste(live_image, avatar_position)
            y_position += live_image.height + 10
        y_position += 20
        print("需要画布高度：", y_position)

        # 创建背景图片的宽度和高度
        desired_width = 1000
        desired_height = max(y_position, 200)

        # 创建背景图片
        background = Image.new('RGB', (desired_width, desired_height), color='white')

        draw = ImageDraw.Draw(background)

        # 加载支持中文的字体并设置文本样式
        font_size = 25  # 替换为所需的字体大小
        font_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "msyh.ttc")  # 替换为支持中文的字体路径
        font_cu = ImageFont.truetype(font_path, font_size)
        font_xi = ImageFont.truetype(font_path, 20)

        # 将头像图片粘贴到背景图片的指定位置
        x_avatar = 50  # 头像的x坐标
        y_avatar = 30  # 头像的y坐标
        avatar_position = (x_avatar, y_avatar)
        background.paste(avatar_image, avatar_position)

        # 添加用户名到背景图片上
        username = username
        x_position = 150  # 文本的x坐标
        y_position = 30  # 文本的y坐标
        draw.text((x_position, y_position), username, font=font_cu, fill='black')

        # 添加更新时间,更新动作描述到背景图片上
        x_position = 150  # 文本的x坐标
        y_position = 80  # 文本的y坐标
        draw.text((x_position, y_position), pub_text, font=font_xi, fill=(169, 169, 169))

        if dynamic_text is not None:
            # 添加动态文本内容到背景图片上
            x_position = 80  # 文本的x坐标
            y_position += 50  # 将 y 坐标向下移动
            i = 0
            for line in dynamic_text.split('\n'):
                if emoji_list is not None and emoji_list_text is not None and len(emoji_list) != 0:
                    if re.search(emoji_list_text[i], line):
                        new_line = re.sub(re.escape(emoji_list_text[i]), '', line)
                        y_position += 30
                        response = requests.get(emoji_list[i])
                        emoji_image = Image.open(BytesIO(response.content))
                        emoji_image = emoji_image.resize(
                            (int(emoji_image.width // 1.8), int(emoji_image.height // 1.8)))
                        if emoji_image.mode == 'RGBA':
                            # 创建一个白色背景的新图像
                            white_background = Image.new("RGB", emoji_image.size, (255, 255, 255))
                            # 将原图像粘贴到白色背景上，使用 alpha 通道作为透明度掩码
                            white_background.paste(emoji_image, (0, 0), emoji_image)
                            emoji_image = white_background
                        draw.text((x_position, y_position), new_line, font=font_cu, fill='black')
                        avatar_position = (x_position + 25 * len(new_line), y_position - 60)
                        background.paste(emoji_image, avatar_position)
                        i = min(i + 1, len(emoji_list) - 1)
                    else:
                        draw.text((x_position, y_position), line, font=font_cu, fill='black')
                else:
                    draw.text((x_position, y_position), line, font=font_cu, fill='black')
                y_position += 40  # 每行文本之间的间距

        if video_title is not None:
            # 添加视频标题到背景图片上
            x_position = 70 + cover_image.width  # 文本的x坐标
            y_position += 20  # 文本的y坐标
            y_line_position = y_position
            if cover_url is not None:
                # 将视频封面图片粘贴到背景图片的指定位置
                cover_position = (50, y_position)
                background.paste(cover_image, cover_position)
            len_video_title = 0
            for line in video_title.split('\n'):
                draw.text((x_position, y_position), line, font=font_cu, fill='black')
                y_position += 35  # 每行文本之间的间距
                len_video_title = max(x_position + len(line) * 30, len_video_title)
            if description is not None:
                # 添加视频简介到背景图片上
                y_position += 40  # 将 y 坐标向下移动
                len_description = 0
                i = 0
                for line in description.split('\n'):
                    if i > 2:
                        draw.text((x_position, y_position), "......", font=font_xi, fill=(169, 169, 169))
                        break
                    draw.text((x_position, y_position), line, font=font_xi, fill=(169, 169, 169))
                    y_position += 25  # 每行文本之间的间距
                    i += 1
                    len_description = max(x_position + len(line) * 30, len_description)

            # 添加边框
            border_width = 1  # 边框宽度
            draw.rectangle(
                [49, y_line_position - 1, min(max(len_video_title, len_description) + 15, 1000 - 50),
                 y_line_position + cover_image.height + 1],
                outline=(169, 169, 169),  # 边框颜色
                width=border_width  # 边框宽度
            )
            y_position = y_line_position + cover_image.height + 1
        # 添加动态图片
        if src_list is not None:
            i = 1
            x_position = 50
            y_position += 10
            image = None
            for url in src_list:
                if i % 2 == 0:
                    x_position += image.width + 5
                if i % 2 != 0 and i != 1:
                    x_position = 50
                    y_position += image.height + 5
                response = requests.get(url)
                image = Image.open(BytesIO(response.content))
                image = cropped_image(image)
                image = create_rounded_rectangle_image(image, 10)
                avatar_position = (x_position, y_position)
                background.paste(image, avatar_position)
                i += 1
            y_position += image.height + 5
        if live_title is not None:
            x_position = 50
            y_position += 50
            draw.text((x_position, y_position), live_title, font=font_cu, fill='black')
        if live_cover_url is not None:
            y_position += 50
            response = requests.get(live_cover_url)
            live_image = Image.open(BytesIO(response.content))
            # live_image = cropped_image(live_image, 470, 265)
            live_image = create_rounded_rectangle_image(live_image, 10)
            avatar_position = (x_position, y_position)
            background.paste(live_image, avatar_position)
            y_position += live_image.height + 10
        y_position += 10
        # 保存组合后的图片
        base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "path")
        path = os.path.join(base_path, f"{id}.png")
        background.save(path)  # 替换为保存路径
        print("已更新动态", "图片保存到：", path)
        # print("等待10分钟再次执行")
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "path.txt"), "a", encoding="utf-8") as file:
            file.write(path + f"\n")
        # time.sleep(600)
        return
    else:
        print("bilibili_api调取失败")
        return

def create_circle_image(image):
    """将图像转换为圆形，背景为白色"""
    width, height = image.size
    radius = min(width, height) // 2
    circle_image = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(circle_image)
    draw.ellipse((0, 0, width, height), fill=255)  # 蒙版为白色
    circular_avatar = Image.new("RGBA", (width, height), (255, 255, 255, 0))  # 背景为透明白色
    circular_avatar.paste(image, mask=circle_image)
    return circular_avatar


def create_rounded_rectangle_image(image, radius):
    """将图像转换为带有圆角的矩形，背景为白色"""
    width, height = image.size

    # 创建一个全白背景图像
    rounded_avatar = Image.new("RGB", (width, height), (255, 255, 255))

    # 创建一个带有圆角的矩形蒙版
    rounded_mask = Image.new('L', (width, height), 0)  # 'L' 表示灰度模式（黑白）
    draw = ImageDraw.Draw(rounded_mask)

    # 画出带有指定半径的圆角矩形蒙版
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)

    # 将原始图像粘贴到白色背景上，同时应用圆角矩形蒙版
    rounded_avatar.paste(image, (0, 0), mask=rounded_mask)

    return rounded_avatar

def cropped_image(cover_image, width=200, height=150):
    cover_image.thumbnail((400, 300))
    # 目标截取尺寸
    target_width = width
    target_height = height

    # 原始图像的宽度和高度
    original_width, original_height = cover_image.size

    # 计算中心点
    center_x = original_width // 2
    center_y = original_height // 2

    # 计算要截取区域的左上角和右下角坐标
    left = center_x - target_width // 2
    top = center_y - target_height // 2
    right = center_x + target_width // 2
    bottom = center_y + target_height // 2

    # 截取指定区域
    cropped_image = cover_image.crop((left, top, right, bottom))
    return cropped_image

