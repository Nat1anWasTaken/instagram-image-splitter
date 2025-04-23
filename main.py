import os
import argparse
from typing import Tuple, Dict, Any, List, cast, TypeVar, Optional

import inquirer
from PIL import Image, ImageFilter, ImageOps

T = TypeVar('T')
InquirerQuestion = Any

def validate_digit(_: Any, x: Any) -> bool:
    return str(x).isdigit() and int(x) > 0

def get_user_inputs() -> Tuple[str, int, int, str, str]:
    questions: List[InquirerQuestion] = [
        inquirer.Path(
            "image_path",
            message="請輸入圖片的路徑",
            path_type=inquirer.Path.FILE,
            exists=True,
        ),
        inquirer.Text(
            "rows",
            message="請輸入要分割的行數",
            validate=validate_digit,
        ),
        inquirer.Text(
            "cols",
            message="請輸入要分割的列數",
            validate=validate_digit,
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
    if answers is None:
        raise ValueError("用戶取消了輸入")

    answers = cast(Dict[str, Any], answers)
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


def add_blur_safezones(tile: Image.Image, blur_width: int = 32) -> Image.Image:
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


def process_and_split_image(
    image_path: str, 
    rows: int, 
    cols: int, 
    output_dir: str, 
    edge_mode: str,
    resize_mode: str = "resize",
    interactive: bool = True
) -> None:
    img = Image.open(image_path)
    img_width, img_height = img.size

    content_width = 1016  # 1080 - 64 (The size of the left and right borders)
    content_height = 1350

    total_content_width = content_width * cols
    total_content_height = content_height * rows

    if img_width < total_content_width or img_height < total_content_height:
        if interactive:
            choices: List[Tuple[str, str]] = [
                ("調整圖片大小以適應網格", "resize"),
                ("添加黑色邊框以滿足所需尺寸", "pad"),
            ]
            action_question: List[InquirerQuestion] = [
                inquirer.List(
                    "action",
                    message="原始圖片尺寸小於所需的網格尺寸。請選擇你希望的處理方式：",
                    choices=choices,
                )
            ]
            action_result = inquirer.prompt(action_question)
            if action_result is None:
                raise ValueError("用戶取消了輸入")
            action = cast(Dict[str, str], action_result)["action"]
        else:
            action = resize_mode

        if action == "resize":
            img = img.resize((total_content_width, total_content_height), Image.Resampling.LANCZOS)
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
        img = img.crop((int(left), int(upper), int(right), int(lower)))

    tile_number = 1
    for row in reversed(range(rows)):
        for col in reversed(range(cols)):
            left = col * content_width
            upper = row * content_height
            right = left + content_width
            lower = upper + content_height

            tile = img.crop((int(left), int(upper), int(right), int(lower)))

            if edge_mode == "pad":
                processed_tile = ImageOps.expand(tile, (32, 0, 32, 0), fill="white")
            elif edge_mode == "blur":
                processed_tile = add_blur_safezones(tile)
            else:
                raise ValueError("Invalid edge mode selected.")

            tile_filename = os.path.join(output_dir, f"tile_{tile_number}.jpg")
            
            if processed_tile.mode == 'RGBA':
                processed_tile = processed_tile.convert('RGB')
                
            processed_tile.save(tile_filename, quality=95)
            tile_number += 1

    print(f"成功將圖片分割成 {rows * cols} 個區塊，並保存在 '{os.path.abspath(output_dir)}' 目錄中。")


def parse_args() -> Optional[argparse.Namespace]:
    parser = argparse.ArgumentParser(description='將圖片分割成多個小圖片，適合用於 Instagram 多圖發布')
    parser.add_argument('-i', '--image', default='input.jpg', help='輸入圖片的路徑（默認：input.jpg）')
    parser.add_argument('-r', '--rows', type=int, default=1, help='要分割的行數（默認：1）')
    parser.add_argument('-c', '--cols', type=int, default=1, help='要分割的列數（默認：1）')
    parser.add_argument('-o', '--output', default='./output', help='輸出目錄的路徑（默認：./output）')
    parser.add_argument('-e', '--edge-mode', choices=['blur', 'pad'], default='blur',
                      help='安全線處理模式：blur（模糊邊緣）或 pad（白色邊框）（默認：blur）')
    parser.add_argument('-m', '--resize-mode', choices=['resize', 'pad'], default='resize',
                      help='當圖片尺寸不足時的處理模式：resize（調整大小）或 pad（添加邊框）（默認：resize）')
    parser.add_argument('--interactive', action='store_true', help='使用交互式界面')
    
    args = parser.parse_args()
    
    if args.interactive:
        return args
        
    if not os.path.exists(args.image):
        return None
        
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        
    return args


def main() -> None:
    args = parse_args()
    
    if args is None or args.interactive:
        image_path, rows, cols, output_dir, edge_mode = get_user_inputs()
        process_and_split_image(image_path, rows, cols, output_dir, edge_mode, interactive=True)
    else:
        process_and_split_image(
            args.image, 
            args.rows, 
            args.cols, 
            args.output, 
            args.edge_mode, 
            args.resize_mode,
            interactive=False
        )


if __name__ == "__main__":
    main()
