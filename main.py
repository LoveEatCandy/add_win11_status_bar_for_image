from PIL import Image, ImageFilter, ImageDraw, ImageFont
import argparse
import os


def apply_bottom_blur(image, blur_radius=100, blur_height=200):
    """对图片底部特定高度区域应用高斯模糊（毛玻璃效果）"""
    width, height = image.size

    # 确保模糊高度不超过图片高度
    if blur_height > height:
        blur_height = height

    # 分割图片为上下两部分
    bottom_area = (0, height - blur_height, width, height)

    # 复制原图
    result = image.copy()

    # 对底部区域应用毛玻璃效果
    bottom_part = image.crop(bottom_area)
    blurred_bottom = bottom_part.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # 将处理后的底部区域放回原图
    result.paste(blurred_bottom, bottom_area)

    return result


def add_icons_to_blur(image, icon_paths, blur_height=200, icon_size=80, spacing=50):
    """在毛玻璃效果区域添加图标"""
    width, height = image.size
    blur_start_y = height - blur_height

    # 创建可绘制对象
    draw_image = image.copy()

    # 计算图标总宽度和起始位置（居中显示）
    total_icons_width = len(icon_paths) * icon_size + (len(icon_paths) - 1) * spacing
    start_x = (width - total_icons_width) // 2

    # 加载并放置图标
    for i, icon_path in enumerate(icon_paths):
        try:
            icon = Image.open(icon_path).convert("RGBA")
            # 调整图标大小
            icon = icon.resize((icon_size, icon_size), Image.LANCZOS)

            # 计算图标位置（垂直居中）
            icon_x = start_x + i * (icon_size + spacing)
            icon_y = blur_start_y + (blur_height - icon_size) // 2

            # 透明粘贴图标
            draw_image.paste(icon, (icon_x, icon_y), icon)
        except Exception as e:
            print(f"无法加载图标 {icon_path}: {e}")

    return draw_image


def add_time_to_blur(
    image, time_text, blur_height=200, font_size=80, padding=50, vertical_offset=0
):
    """在毛玻璃效果区域右侧添加时间"""
    width, height = image.size
    # blur_start_y = height - blur_height
    blur_start_y = height - blur_height
    blur_center_y = blur_start_y + blur_height // 2

    # 创建可绘制对象
    draw = ImageDraw.Draw(image)

    # 加载字体
    font = ImageFont.truetype("font/YaHei.ttf", font_size)

    # 计算时间文本的宽度和高度 (兼容新旧版本Pillow)
    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 计算文本的垂直中心偏移（基于字体metrics）
    ascent, descent = font.getmetrics()
    text_center_y = ascent - text_height // 2

    # 计算时间位置（水平居右，垂直居中）
    text_x = width - text_width - padding
    text_y = blur_center_y - text_center_y + vertical_offset

    # # 计算时间位置（垂直居中，右侧留出padding）
    # text_x = width - text_width - padding
    # text_y = blur_start_y + (blur_height - text_height) // 2

    # 绘制时间文本（带黑色描边效果）
    outline_color = (0, 0, 0)  # 黑色描边
    for adj in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        draw.text(
            (text_x + adj[0], text_y + adj[1]), time_text, font=font, fill=outline_color
        )
    draw.text((text_x, text_y), time_text, font=font, fill=(255, 255, 255))  # 白色文本

    return image


def process_image(
    input_path,
    output_path,
    icon_paths,
    time_text,
    blur_radius=100,
    blur_height=200,
    icon_size=128,
    spacing=50,
    font_size=80,
):
    """处理图片文件，添加毛玻璃效果、图标和时间"""
    try:
        # 打开图片
        with Image.open(input_path) as img:
            # 应用底部毛玻璃效果
            blurred_img = apply_bottom_blur(img, blur_radius, blur_height)

            # 添加图标
            if icon_paths:
                icon_img = add_icons_to_blur(
                    blurred_img, icon_paths, blur_height, icon_size, spacing
                )
            else:
                icon_img = blurred_img

            # 添加时间
            final_img = add_time_to_blur(
                icon_img, time_text, blur_height, font_size=font_size
            )

            # 保存处理后的图片
            final_img.save(output_path)
            print(f"图片处理完成，已保存至: {output_path}")
    except Exception as e:
        print(f"处理图片时出错: {e}")


def main():
    parser = argparse.ArgumentParser(description="为图片底部添加毛玻璃效果、图标和时间")
    parser.add_argument("-i", "--input", required=True, help="输入图片文件路径")
    parser.add_argument("-o", "--output", help="输出图片文件路径")
    parser.add_argument("-r", "--radius", type=int, default=100, help="模糊半径")
    parser.add_argument(
        "-H", "--height", type=int, default=200, help="底部模糊区域高度"
    )
    parser.add_argument("-s", "--iconsize", type=int, default=128, help="图标大小")
    parser.add_argument("-f", "--fontsize", type=int, default=80, help="字体大小")
    parser.add_argument("-S", "--spacing", type=int, default=50, help="图标间距")
    parser.add_argument("-t", "--time", default="13:14", help="要显示的时间文本")
    parser.add_argument("-I", "--icons", default="icons", help="图标文件路径列表")

    args = parser.parse_args()

    # 确定输出文件名
    if not args.output:
        base_name, ext = os.path.splitext(args.input)
        args.output = f"{base_name}_enhanced{ext}"

    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件 '{args.input}' 不存在")
        return

    # 检查图标文件
    icon_dir = args.icons
    icon_paths = []
    for filename in os.listdir(icon_dir):
        icon_paths.append(os.path.join(icon_dir, filename))

    # 处理图片
    if os.path.isdir(args.input):
        for filename in os.listdir(args.input):
            input_path = os.path.join(args.input, filename)
            output_path = os.path.join(args.output, filename)
            process_image(
                input_path,
                output_path,
                icon_paths,
                args.time,
                args.radius,
                args.height,
                args.iconsize,
                args.spacing,
                args.fontsize,
            )
    else:
        process_image(
            args.input,
            args.output,
            icon_paths,
            args.time,
            args.radius,
            args.height,
            args.iconsize,
            args.spacing,
            args.fontsize,
        )

    print("处理完成!")


if __name__ == "__main__":
    main()
