import darkdetect

class Utils:

    _SIZE = 100
    _TOP_LEFT = (0, 0)

    def get_font_size(self):
        return self._SIZE

    def get_font_size_half(self):
        return self.get_font_size()//2

    def get_location(self):
        return self._TOP_LEFT

    def get_font_colour(self):  # This doesn't support custom themes yet
        if(darkdetect.isDark()):
            return 'white'
        else:
            return 'black'

