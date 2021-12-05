import time
from samplebase import SampleBase
from PIL import Image
import threading

#line_1　【表示1行目】16x32 RGBLED
#line_2　【表示2行目】32x64 RGBLEDの「1行目 16x64」
#line_3　【表示3行目】32x64 RGBLEDの「2行目 16x64」

LINE_1_START_Y_POS:int = 0
LINE_2_START_Y_POS:int = 16
LINE_3_START_Y_POS:int = 32

TEXT_SCROLL_SPEED = 0.02

IMAGE_DIR_PASS = "/home/pi"


class ShowContents(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ShowContents, self).__init__(*args, **kwargs)
        self.parser.add_argument("-i1", "--image1", help="The image to display", default="../../../examples-api-use/runtext.ppm")

        #表示するためのイメージデータが入る変数(RGBに変換後のもの)
        self.line_1_image = None
        self.line_2_image = None
        self.line_3_image = None

    def load_image(self):
        self.image1 = Image.open(self.args.image1).convert('RGB')
        #self.image2 = Image.open(self.args.image2).convert('RGB')

    def draw_image(self):
        image_buffer = self.matrix.CreateFrameCanvas()
        
        #描画部分
        def line_1_draw_image(image_buffer, line_1_image):
            line1_x_pos = 0
            img_width, img_height = line_1_image.size

            while True:
                line1_x_pos += 1
                if (line1_x_pos > img_width):
                    line1_x_pos = 0

                image_buffer.SetImage(self.image2, -line1_x_pos, LINE_1_START_Y_POS)
                image_buffer.SetImage(self.image2, -line1_x_pos + img_width, LINE_1_START_Y_POS)

                double_buffer = self.matrix.SwapOnVSync(double_buffer)
                time.sleep(TEXT_SCROLL_SPEED)

        def line_2_draw_image(self):
            line2_x_pos = 0

        def line_3_draw_image(self):
            line3_x_pos = 0
        
        thread = threading.Thread(target=line_1_draw_image, args=(image_buffer,self.line_1_image))
        thread.start()        


    def run(self):
        self.load_image()
        self.draw_image()


# Main function
# e.g. call with
#  sudo ./image-scroller.py --chain=4
# if you have a chain of four
if __name__ == "__main__":
    image_scroller = ShowContents()
    if (not image_scroller.process()):
        image_scroller.print_help()
