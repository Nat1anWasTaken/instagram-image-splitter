import os
from typing import Tuple

import inquirer
from PIL import Image, ImageFilter, ImageOps


def get_user_inputs() -> Tuple[str, int, int, str, str]:
    questions = [
        inquirer.Path(
            "image_path",
            message="請輸入圖片的路徑",
            path_type=inquirer.Path.FILE,
            exists=True,
        ),
        inquirer.Text(
            "rows",
            message="請輸入要分割的行數",
            validate=lambda _, x: x.isdigit() and int(x) > 0,
        ),
        inquirer.Text(
            "cols",
            message="請輸入要分割的列數",
            validate=lambda _, x: x.isdigit() and int(x) > 0,
        ),
        inquirer.Path(
            "output_dir",
            message="請輸入輸出目錄的路徑 (如: ./output)",
            path_type=inquirer.Path.DIRECTORY,
            exists=False,
        ),
        inquirer.List(
            "edge_mode",
            message="請選擇安全線處理模式",
            choices=[
                ("添加模糊邊緣", "blur"),
                ("添加白色邊框", "pad"),
            ],
            default="blur",
        )
    ]

    answers = inquirer.prompt(questions)

    answers["rows"] = int(answers["rows"])
    answers["cols"] = int(answers["cols"])

    if not os.path.exists(answers["output_dir"]):
        os.makedirs(answers["output_dir"])

    return (
        answers["image_path"],
        answers["rows"],
        answers["cols"],
        answers["output_dir"],
        answers["edge_mode"],
    )


def add_blur_safezones(tile, blur_width=32) -> Image.Image:
    content_width, content_height = tile.size

    left_edge = tile.crop((0, 0, blur_width, content_height)).filter(
        ImageFilter.GaussianBlur(radius=10)
    )
    right_edge = tile.crop(
        (content_width - blur_width, 0, content_width, content_height)
    ).filter(ImageFilter.GaussianBlur(radius=10))
    final_img = Image.new("RGB", (content_width + 2 * blur_width, content_height))

    final_img.paste(left_edge, (0, 0))
    final_img.paste(tile, (blur_width, 0))
    final_img.paste(right_edge, (blur_width + content_width, 0))

    return final_img


def process_and_split_image(image_path, rows, cols, output_dir, edge_mode):
    img = Image.open(image_path)
    img_width, img_height = img.size

    content_width = 1016  # 1080 - 64 (The size of the left and right borders)
    content_height = 1350

    total_content_width = content_width * cols
    total_content_height = content_height * rows

    if img_width < total_content_width or img_height < total_content_height:
        choices = [
            ("調整圖片大小以適應網格", "resize"),
            ("添加黑色邊框以滿足所需尺寸", "pad"),
        ]
        action_question = [
            inquirer.List(
                "action",
                message="原始圖片尺寸小於所需的網格尺寸。請選擇你希望的處理方式：",
                choices=choices,
            )
        ]
        action = inquirer.prompt(action_question)["action"]

        if action == "resize":
            img = img.resize((total_content_width, total_content_height), Image.LANCZOS)
        elif action == "pad":
            pad_width = max(0, total_content_width - img_width)
            pad_height = max(0, total_content_height - img_height)
            img = ImageOps.expand(
                img,
                (
                    pad_width // 2,
                    pad_height // 2,
                    pad_width - pad_width // 2,
                    pad_height - pad_height // 2,
                ),
                fill="black",
            )
    else:
        left = (img_width - total_content_width) / 2
        upper = (img_height - total_content_height) / 2
        right = left + total_content_width
        lower = upper + total_content_height
        img = img.crop((left, upper, right, lower))

    tile_number = 1
    for row in reversed(range(rows)):
        for col in reversed(range(cols)):
            left = col * content_width
            upper = row * content_height
            right = left + content_width
            lower = upper + content_height

            tile = img.crop((left, upper, right, lower))

            if edge_mode == "pad":
                processed_tile = ImageOps.expand(tile, (32, 0, 32, 0), fill="white")
            elif edge_mode == "blur":
                processed_tile = add_blur_safezones(tile)
            else:
                raise ValueError("Invalid edge mode selected.")

            tile_filename = os.path.join(output_dir, f"tile_{tile_number}.jpg")
            processed_tile.save(tile_filename, quality=95)
            tile_number += 1

    print(f"成功將圖片分割成 {rows * cols} 個區塊，並保存在 '{os.path.abspath(output_dir)}' 目錄中。")


def main():
    image_path, rows, cols, output_dir, edge_mode = get_user_inputs()
    process_and_split_image(image_path, rows, cols, output_dir, edge_mode)


if __name__ == "__main__":
    main()
