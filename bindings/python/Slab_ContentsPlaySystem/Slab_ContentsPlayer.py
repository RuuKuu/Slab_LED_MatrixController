#!/usr/bin/env python
import time
from samplebase import SampleBase
from PIL import Image
import threading
import os

#line_1　【表示1行目】16x32 RGBLED
#line_2　【表示2行目】32x64 RGBLEDの「1行目 16x64」
#line_3　【表示3行目】32x64 RGBLEDの「2行目 16x64」

LINE_1_START_Y_POS:int = 0
LINE_2_START_Y_POS:int = 8
#16
LINE_3_START_Y_POS:int = 32

TEXT_SCROLL_SPEED = 0.02

IMAGE_DIR_PASS = "/home/pi/ElectricBoardContentsFolder"


class ShowContents(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ShowContents, self).__init__(*args, **kwargs)

        #表示するためのイメージデータが入る変数(RGBに変換後のもの)
        self.line_1_image = None
        self.line_2_image = None
        self.line_3_image = None

    def load_image(self):
        number_of_files = sum(os.path.isfile(os.path.join(DIR, name)) for name in os.listdir(DIR))
        self.line_1_image = Image.open(self.args.image1).convert('RGB')
        #self.line_2_image = Image.open(self.args.image2).convert('RGB')

    def draw_image(self):
        image_buffer = self.matrix.CreateFrameCanvas()
        
        #描画部分
        def line_1_set_image(image_buffer, line_1_image):
            #スクロール表示

            line1_x_pos = 0
            img_width, img_height = line_1_image.size

            while True:
                line1_x_pos += 1
                if (line1_x_pos > img_width):
                    line1_x_pos = 0

                image_buffer.SetImage(line_1_image, -line1_x_pos, LINE_1_START_Y_POS)
                image_buffer.SetImage(line_1_image, -line1_x_pos + img_width, LINE_1_START_Y_POS)

                time.sleep(TEXT_SCROLL_SPEED)

        def line_2_set_image(image_buffer, line_2_image):
            #切り替え表示

            line2_x_pos = 0
            img_width, img_height = line_2_image.size

            while True:
                line2_x_pos += 1
                if (line2_x_pos > img_width):
                    line2_x_pos = 0

                image_buffer.SetImage(line_2_image, -line2_x_pos, LINE_2_START_Y_POS)
                image_buffer.SetImage(line_2_image, -line2_x_pos + img_width, LINE_2_START_Y_POS)

                time.sleep(TEXT_SCROLL_SPEED)

        def line_3_set_image(image_buffer, line_3_image):
            #スクロール表示

            line3_x_pos = 0
            img_width, img_height = line_3_image.size

            while True:
                line3_x_pos += 1
                if (line3_x_pos > img_width):
                    line3_x_pos = 0

                image_buffer.SetImage(line_3_image, -line3_x_pos, LINE_3_START_Y_POS)
                image_buffer.SetImage(line_3_image, -line3_x_pos + img_width, LINE_3_START_Y_POS)

                time.sleep(TEXT_SCROLL_SPEED)

        def all_line_draw_image(image_buffer):
            while True:
                image_buffer = self.matrix.SwapOnVSync(image_buffer)

        thread_line_1 = threading.Thread(target=line_1_set_image, args=(image_buffer,self.line_1_image))
        thread_line_1.start()

        thread_line_2 = threading.Thread(target=line_2_set_image, args=(image_buffer,self.line_2_image))
        thread_line_2.start()         

        thread_line_3 = threading.Thread(target=line_3_set_image, args=(image_buffer,self.line_3_image))
        thread_line_3.start()    

        thread_line_draw = threading.Thread(target=all_line_draw_image, args=(image_buffer,))
        thread_line_draw.start()        

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
