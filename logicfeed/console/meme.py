from itertools import product, count
from textwrap import wrap

from PIL import Image, ImageFont, ImageDraw


__all__ = ['draw_meme']


def draw_meme(output_path, image_path, text, fill_color='white', outline_color='black', border_size=1, font_size=30,
              font='/usr/share/fonts/truetype/msttcorefonts/arial.ttf', spacing=15, y_offset=30, wrap_width=None):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font_style = ImageFont.truetype(font, font_size)

    text_positions = _get_text_positions(draw, text, font_style, spacing, border_size,
                                         image.size[0], image.size[1], y_offset, wrap_width)

    for sentence, position in text_positions:
        for offset in product((border_size, -border_size), repeat=2):
            offseted_position = tuple(map(sum, zip(position, offset)))
            draw.text(offseted_position, sentence, font=font_style, fill=outline_color)

        draw.text(position, sentence, font=font_style, fill=fill_color)

    image.save(output_path)


def _get_text_positions(draw, text, font_style, spacing, border_size, image_width, image_height,
                        y_offset, wrap_width):
    calc_x = lambda text_width: (image_width - text_width) / 2 - border_size
    calc_y = lambda text_height: image_height - y_offset - text_height - border_size * 2

    positions = None
    if type(text) is str:
        text_width, text_height = draw.textsize(text, font=font_style)
        text_x = calc_x(text_width)
        text_y = calc_y(text_height)

        if text_x >= 0:
            positions = [(text, (text_x, text_y))]
        else:
            wrap_width = wrap_width or int(len(text) * image_width / text_width)
            text = wrap(text, width=wrap_width)

    if not positions:
        text_widths, text_heights = list(zip(*[draw.textsize(sentence, font=font_style) for sentence in text]))
        text_width = max(text_widths)
        text_height = sum(text_heights) + spacing * (len(text_heights) - 1)
        text_y = calc_y(text_height)
        positions = [(sentence, (calc_x(width), text_y + sum(text_heights[0:i]) + spacing * i))
                     for i, sentence, width in zip(count(), text, text_widths)]

    if text_y < 0:
        raise RuntimeError('Image too small')

    return positions
