import pygame
from PIL import Image, ImageFilter

class Effects(object):

    @staticmethod
    def blur_surf(surface, radius, opacity = 1):
        size, image_mode, raw = surface.get_size(), 'RGBA', pygame.image.tostring(surface, 'RGBA')
        pil_blured = Image.frombytes('RGBA', size, raw).filter(ImageFilter.GaussianBlur(radius=radius))
        return pygame.image.fromstring(pil_blured.tobytes('raw', 'RGBA'), size, image_mode)

    @staticmethod
    def draw_progressbar(surface, rect, value, max_value, color):
        percentage = (value / max_value)
        if percentage != 1:
            pygame.draw.rect(surface, color, rect, 1)
            rect[2] *= percentage
        pygame.draw.rect(surface, color, rect)

    @staticmethod
    def aspect_scale(img, bx, by):
        ix,iy = img.get_size()
        if ix > iy:
            # fit to width
            scale_factor = bx/float(ix)
            sy = scale_factor * iy
            if sy > by:
                scale_factor = by/float(iy)
                sx = scale_factor * ix
                sy = by
            else:
                sx = bx
        else:
            # fit to height
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            if sx > bx:
                scale_factor = bx/float(ix)
                sx = bx
                sy = scale_factor * iy
            else:
                sy = by
        return pygame.transform.smoothscale(img, (int(sx),int(sy)))

    @staticmethod
    def draw_text(surface, text, color, rect, font, aa=False, bkg=None):
        rect = pygame.Rect(rect)
        y = rect.top
        lineSpacing = -2
        # get the height of the font
        fontHeight = font.size("Tg")[1]
        while text:
            i = 1
            # determine if the row of text will be outside our area
            if y + fontHeight > rect.bottom:
                break
            # determine maximum width of line
            while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1
            # if we've wrapped the text, then adjust the wrap to the last word
            if i < len(text):
                i = text.rfind(" ", 0, i) + 1
            # render the line and blit it to the surface
            if bkg:
                image = font.render(text[:i], 1, color, bkg)
                image.set_colorkey(bkg)
            else:
                image = font.render(text[:i], aa, color)
            surface.blit(image, (rect.left, y))
            y += fontHeight + lineSpacing
            # remove the text we just blitted
            text = text[i:]
        return text

    def draw_list_selected(surface, texts, colors, rect, font, selected_index = 0):
        # texts is a array of texts
        # colors is a array of colors in the following order:
        # 0: text_color_selected
        # 1: text_color_not_selected
        # 2: color_background
        # 3: color_selection
        pygame.draw.rect(surface, colors[2], rect)
        for idx, text in enumerate(texts):
            text = str(text)
            if (idx == selected_index):
                text = font.render(text, True, colors[0])
                pygame.draw.rect(surface, colors[3], (rect.left, rect.top, rect.width, text.get_height()))
            else:
                text = font.render(text, True, colors[1])
            surface.blit(text, (rect.left, rect.top + (text.get_height() * idx)))
            del text
        pass

