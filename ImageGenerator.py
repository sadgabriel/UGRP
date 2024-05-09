from PIL import Image, ImageDraw

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)


class ImageGenerator:
    def __init__(self, height = 512, width = 512, row = 10, column = 10, padding = -1):
        self.height = height
        self.width = width
        self.row = row
        self.column = column
        self.padding = padding
    
    def get_image(self):
        image = self._create_sketch()

        return image
    
    def _create_sketch(self):
        image = Image.new("RGB", (self.width, self.height), WHITE)
        draw = ImageDraw.Draw(image)
        
        self.draw_grid(draw)
        self.draw_circle(draw, 0, 1, 16, RED, BLACK)
        
        return image
    
    def draw_grid(self, draw, color = BLACK):
        padding = self.padding
        if padding == -1:
            padding = self.height / (self.row + 2)
        
        for i in range(self.row + 1):
            y = i * (self.height - 2 * padding) / self.row + padding
            draw.line([(padding, y), (self.width - padding, y)], fill=color, width=1)

        for j in range(self.column + 1):
            x = j * (self.width - 2 * padding) / self.column + padding
            draw.line([(x, padding), (x, self.height - padding)], fill=color, width=1)

    def draw_circle(self, draw, x, y, radius, circle_color, outline_color):
        padding = self.padding
        if padding == -1:
            padding = self.height / (self.row + 2)
            
        center = ((x + 0.5) * (self.width - 2 * padding) / self.column + padding, (y + 0.5) * (self.height - 2 * padding) / self.row + padding)
        draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=circle_color, outline=outline_color)
    
if __name__ == "__main__":
    ig = ImageGenerator()
    img = ig.get_image()
    
    img.show()
    input()