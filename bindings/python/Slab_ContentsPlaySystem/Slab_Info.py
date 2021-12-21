#!/usr/bin/env python
import time
from samplebase import SampleBase
from PIL import Image
import threading


class ImageScroller(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ImageScroller, self).__init__(*args, **kwargs)
        self.parser.add_argument("-i", "--image", help="The image to display", default="../../../examples-api-use/runtext.ppm")

    def draw_image(self):
        global double_buffer

        double_buffer = self.matrix.CreateFrameCanvas()

        if not 'image' in self.__dict__:
            self.image = Image.open(self.args.image).convert('RGB')
        self.image.resize((self.matrix.width, self.matrix.height), Image.ANTIALIAS)

        image = self.image

        def text():
            global double_buffer
            
            img_width, img_height = image.size

            # let's scroll
            xpos = 0

            while True:
                xpos += 1
                if (xpos > img_width):
                    xpos = 0

                double_buffer.SetImage(image, -xpos, 1)
                double_buffer.SetImage(image, -xpos + img_width, 1)
            
                double_buffer = self.matrix.SwapOnVSync(double_buffer)

                time.sleep(0.02)


        def color():
            global double_buffer

            continuum = 0
            x = 0

            while True:
                continuum += 1
                continuum %= 3 * 255

                x += 1
                if x == 32:
                    x =0

                red = 0
                green = 0
                blue = 0

                if continuum <= 255:
                    c = continuum
                    blue = 255 - c
                    red = c
                elif continuum > 255 and continuum <= 511:
                    c = continuum - 256
                    red = 255 - c
                    green = c
                else:
                    c = continuum - 512
                    green = 255 - c
                    blue = c


                for x in range(0, double_buffer.width):
                    #double_buffer.SetPixel(x, 0, (red+10*x)%256, (green+10*x)%256, (blue+10*x)%256)
                    double_buffer.SetPixel(x, 0, red, green, blue)
                    double_buffer.SetPixel(x, double_buffer.height - 1, red, green, blue)
                
                """
                for y in range(0, double_buffer.height):
                    double_buffer.SetPixel(0, y, red, green, blue)
                    double_buffer.SetPixel(double_buffer.height -1, y, red, green, blue)
                """

                time.sleep(0.01)


        def draw_image(double_buffer):
            while True:
                double_buffer = self.matrix.SwapOnVSync(double_buffer)
                time.sleep(0.001)
        

        thread_line_1 = threading.Thread(target=text)
        thread_line_1.start()

        thread_line_2 = threading.Thread(target=color)
        thread_line_2.start() 

        #thread_draw = threading.Thread(target=draw_image,args=(double_buffer,))    ,args=(double_buffer,)
        #thread_draw.start()


    def run(self):
        self.draw_image()

# Main function
# e.g. call with
#  sudo ./image-scroller.py --chain=4
# if you have a chain of four
if __name__ == "__main__":
    image_scroller = ImageScroller()
    if (not image_scroller.process()):
        image_scroller.print_help()
