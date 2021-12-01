#!/usr/bin/env python
import time
from samplebase import SampleBase
from PIL import Image
import threading
import time

class ImageScroller(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ImageScroller, self).__init__(*args, **kwargs)
        self.parser.add_argument("-i1", "--image1", help="The image to display", default="../../../examples-api-use/runtext.ppm")
        self.parser.add_argument("-i2", "--image2", help="The image to display", default="../../../examples-api-use/runtext.ppm")

    def show_image(self):
                #if not 'image' in self.__dict__:
        self.image1 = Image.open(self.args.image1).convert('RGB')
        self.image2 = Image.open(self.args.image2).convert('RGB')
        #self.image.resize((self.matrix.width, self.matrix.height), Image.ANTIALIAS)

        double_buffer = self.matrix.CreateFrameCanvas()
        self.img_width_1, self.img_height_1 = self.image1.size
        self.img_width_2, self.img_height_2 = self.image2.size

        print(self.img_width_2)
        print(self.img_height_2)

        self.img_width=self.img_width_1

        # let's scroll
        self.xpos = 0
        while True:
            self.xpos += 1
            if (self.xpos > self.img_width):
                self.xpos = 0

            #self.image1 = Image.open(self.args.image1).convert('RGB')

            #double_buffer.SetImage(self.image1, 0)
            #double_buffer.SetImage(self.image1, -xpos + img_width)

            #double_buffer.SetImage(self.image2, -xpos, 8)
            #double_buffer.SetImage(self.image2, -xpos + img_width, 8)

            double_buffer.SetImage(self.image1, -self.xpos)
            double_buffer.SetImage(self.image1, -self.xpos + self.img_width)

            double_buffer = self.matrix.SwapOnVSync(double_buffer)
            time.sleep(0.02)

    def run(self):

        def show_img():
            self.show_image()
        thread = threading.Thread(target=show_img)
        thread.start()

        time.sleep(0.5)

        while True:
            self.img_width = self.img_width_1
            self.xpos = 0

            time.sleep(4)
            self.image_tmp = self.image1
            self.image1 = self.image2

            self.img_width = self.img_width_2
            self.xpos = 0


            time.sleep(28)

            self.image1 = self.image_tmp



# Main function
# e.g. call with
#  sudo ./image-scroller.py --chain=4
# if you have a chain of four
if __name__ == "__main__":
    image_scroller = ImageScroller()
    if (not image_scroller.process()):
        image_scroller.print_help()
