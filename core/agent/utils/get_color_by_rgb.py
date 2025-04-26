import webcolors

from core.utils.logger import Logger


class ColorName:
    def __init__(self):
        self.logger = Logger()

    def _is_rgb_code(self, code: str) -> bool:
        if code.startswith("rgb"):
            return True
        return False

    def _closest_color(self, code: tuple) -> str:

        min_color = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            try:
                r_c, g_c, b_c = webcolors.hex_to_rgb(key)
                rd = (r_c - code[0]) ** 2
                gd = (g_c - code[1]) ** 2
                bd = (b_c - code[2]) ** 2
                min_color[(rd + gd + bd)] = name
                return min_color[min(min_color.keys())]

            except ValueError:
                self.logger.error(f"Invalid hex code: {key}")
                continue

    def _convert_to_hex(self, code: tuple) -> str:
        try:
            hex_value = webcolors.rgb_to_hex((code[0], code[1], code[2]))
            return hex_value
        except ValueError:
            self.logger.info(f"Not a valid RGB color: {code} getting closest color")
            return self._closest_color(code)

    def get_color_by_rgb(self, code: str) -> str:
        """
        Get the color name by RGB code
        :param code: RGB code
        :return: Color name
        """
        if self._is_rgb_code(code):
            try:
                rgb = tuple(map(int, code[5:-1].split(",")))
                return webcolors.hex_to_name(self._convert_to_hex(rgb))
            except ValueError:
                self.logger.error(f"Invalid RGB code: {code}")
                return None
        else:
            self.logger.error(f"Invalid RGB code: {code}")
            return None
