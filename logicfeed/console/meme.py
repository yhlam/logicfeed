from collections import namedtuple
from io import BytesIO
from itertools import count, product
from textwrap import wrap

from PIL import Image, ImageFont, ImageDraw


__all__ = ['draw_meme']


Position = namedtuple('Position', ['x', 'y'])
Text = namedtuple('Text', ['text', 'position'])


def draw_meme(message, image_path, fill_color, border_color, border_size,
              font_path, font_size, spacing, margin_bottom, wrap_width):
    """ Create meme for the provided text and parameters

    The color parameters support the following string formats:

    * Hexadecimal color specifiers, given as ``#rgb`` or ``#rrggbb``. For example,
      ``#ff0000`` specifies pure red.

    * RGB functions, given as ``rgb(red, green, blue)`` where the color values are
      integers in the range 0 to 255. Alternatively, the color values can be given
      as three percentages (0% to 100%). For example, ``rgb(255,0,0)`` and
      ``rgb(100%,0%,0%)`` both specify pure red.

    * Hue-Saturation-Lightness (HSL) functions, given as ``hsl(hue, saturation%,
      lightness%)`` where hue is the color given as an angle between 0 and 360
      (red=0, green=120, blue=240), saturation is a value between 0% and 100%
      (gray=0%, full color=100%), and lightness is a value between 0% and 100%
      (black=0%, normal=50%, white=100%). For example, ``hsl(0,100%,50%)`` is pure
      red.

    * Common HTML color names. 140 standard color names provided by `~PIL.ImageColor`
      module , based on the colors supported by the X Window system and most web
      browsers. color names are case insensitive. For example, ``red`` and``Red``
      both specify pure red.


    :param message: text on the meme
    :param image_path: path or a file object of them image file
    :param fill_color: color of the text
    :param border_color: color of the border of the text
    :param border_size: border width of the text
    :param font_path: path to the true type font
    :param font_size: font size
    :param spacing: spacing between lines in pixel
    :param margin_bottom: bottom margin
    :param wrap_width: maximum width of each line in pixel
    :return: bytes of the generated meme in PNG format
    :rtype: bytes
    :raise ValueError: if the text with the specified font size and margin cannot
                       fit into the background image
    """
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)

    lines = get_texts(draw, message, font, spacing, border_size,
                      image.size[0], image.size[1], margin_bottom, wrap_width)

    for line, position in lines:
        for offset in product((border_size, -border_size), repeat=2):
            offset_position = tuple(map(sum, zip(position, offset)))
            draw.text(offset_position, line, font=font, fill=border_color)

        draw.text(position, line, font=font, fill=fill_color)

    output = BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()


def get_texts(draw, message, font, spacing, border_size, image_width, image_height, margin_bottom, wrap_width):
    """ Wrap the message into lines based on the wrap width and calculate their positions

    :param draw: Draw object in PIL
    :param message: text to be draw on the meme
    :param font: Font object in PIL
    :param spacing: spacing between lines in pixel
    :param border_size: border width of the text
    :param image_width: width of the background image
    :param image_height: height of the background image
    :param margin_bottom: bottom margin
    :param wrap_width: maximum width of each line in pixel
    :return: list of Text(text, Position(x, y))
    :rtype: list
    :raise ValueError: if the message with the specified font size and margin cannot
                       fit into the background image
    """
    width, _ = draw.textsize(message, font=font)
    wrap_width_char = int(len(message) / width * wrap_width)
    lines = wrap(message, width=wrap_width_char)

    sizes = [draw.textsize(line, font=font) for line in lines]
    text_height = sum(map(lambda size: size[1], sizes)) + spacing * (len(lines) - 1)
    text_y = image_height - margin_bottom - text_height - border_size

    calc_x = lambda text_width: (image_width - text_width) / 2
    texts = []
    for i, line, (width, height) in zip(count(), lines, sizes):
        x, y, text_y = calc_x(width), text_y, text_y + height + spacing
        if x < 0 or y < 0:
            raise ValueError('Image is too small')
        texts.append(Text(line, Position(x, y)))

    return texts
