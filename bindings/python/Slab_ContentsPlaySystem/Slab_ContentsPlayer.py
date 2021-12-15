#!/usr/bin/env python
import time
from samplebase import SampleBase
from rgbmatrix import graphics
from datetime import datetime
import time
from PIL import Image
import threading
import os
from natsort import natsorted
import schedule

#line_1　【表示1行目】32x64 RGBLEDの「1行目 12x64」
#line_2　【表示2行目】32x64 RGBLEDの「2行目 20x64」

LINE_1_START_Y_POS:int = 0
LINE_2_START_Y_POS:int = 12

TEXT_SCROLL_SPEED = 0.01

IMAGE_DIR_PASS = "/home/pi/ElectricBoardContentsFolder"


class ShowContents(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ShowContents, self).__init__(*args, **kwargs)

        #表示するためのイメージデータ等のデータが入る変数(RGBに変換後のもの)
        self.line_1_image_etc = None
        self.line_2_image_etc = None

        schedule.every(5).minutes.do(self.load_image)

    def load_image(self):
        """
        1.各lineごとのdirに入る
        2.ファイル一覧を取得し、頭文字を用いてソート
        3.ソートした順番で画像ファイルのオープンを行い画像ファイル・表示秒数を切り出したリストを作成
        4.そのリストをファイル数分結合したリストを作る
        5.4までの処理を各Dir分行う
        """
        #ディレクトリのリスト
        line_dir_list = ["Line1", "Line2"]
        #各ディレクトリごとのイメージデータなどを格納したリスト
        display_information_data_dir = []
        #全ディレクトリのイメージデータなどを格納したリスト(多ネストリストになってる)
        display_information_data = []

        for dir in line_dir_list:
            display_information_data_dir = []
            files = []
            display_seconds = []
            image = []

            line_dir = os.path.join(IMAGE_DIR_PASS, dir) #各LineごとのDir名作成
            dir_files = os.listdir(line_dir) #上記Dir内の物をリスト化
            files = [f for f in dir_files if os.path.isfile(os.path.join(line_dir, f))] #Dirの中からファイルのものをリスト化
            files = natsorted(files) #頭文字順にリストを整列

            for file in files: #各Dir内の各ファイルに対しての操作
                file_name_splited = file.split("_") #表示秒数読み出し
                display_seconds.append(file_name_splited[1]) #表示秒数をリスト化

                image.append(Image.open(os.path.join(line_dir, file)).convert('RGB')) #画像のオープン処理とそれをリストに入れる
            
            display_information_data_dir.append(files)
            display_information_data_dir.append(display_seconds)
            display_information_data_dir.append(image)

            display_information_data.append(display_information_data_dir)

            #print(display_information_data_dir)
            #print("---------------------------------------------")
            #print(display_seconds)
            #print(image)

        print(display_information_data)

        self.line_1_image_etc = display_information_data[0]
        self.line_2_image_etc = display_information_data[1]


    def draw_image(self):
        image_buffer = self.matrix.CreateFrameCanvas()
        
        #描画部分
        def line_1_set_image(image_buffer, line_1_image_etc):
            #スクロール表示

            selecting_drawing_image = 0
            line1_x_pos = 0

            font = graphics.Font()
            font.LoadFont("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
            textColor = graphics.Color(100, 100, 255)

            while True:
                line_1_image = line_1_image_etc[2][selecting_drawing_image]
                img_width, img_height = line_1_image.size

                display_seconds = line_1_image_etc[1][selecting_drawing_image]
                
                image_buffer.SetImage(line_1_image, -line1_x_pos, LINE_1_START_Y_POS)
                #image_buffer.SetImage(line_1_image, -line1_x_pos + img_width, LINE_1_START_Y_POS)


                if  selecting_drawing_image == len(line_1_image_etc)+1:
                    #https://a-tak.com/blog/2017/03/raspberry-pi-led-clock-4/
                    d = datetime.now()
                    h = (" " + str(d.hour))[-2:]
                    #スペースを頭に着けて最後から2文字背取得。1-9時の間も真ん中に時計が表示されるようにする考慮
                    clock = h + ":" + d.strftime("%M")
                    print(clock)
                    graphics.DrawText(image_buffer, font, 0, 12, textColor, clock)

                    selecting_drawing_image = 0
                    time.sleep(5)
                else:
                    selecting_drawing_image += 1

                time.sleep(int(display_seconds))


        def line_2_set_image(image_buffer, line_2_image_etc):
            #切り替え表示

            selecting_drawing_image = 0
            line2_x_pos = 0

            while True:
                line_2_image = line_2_image_etc[2][selecting_drawing_image]
                img_width, img_height = line_2_image.size


                image_buffer.SetImage(line_2_image, -line2_x_pos, LINE_2_START_Y_POS)
                image_buffer.SetImage(line_2_image, -line2_x_pos + img_width, LINE_2_START_Y_POS)

                line2_x_pos += 1
                if (line2_x_pos > img_width-64):
                    line2_x_pos = 0
                    selecting_drawing_image += 1
                
                if selecting_drawing_image == len(line_2_image_etc)+1:
                    selecting_drawing_image = 0

                time.sleep(TEXT_SCROLL_SPEED)


        def all_line_draw_image(image_buffer):
            while True:
                image_buffer = self.matrix.SwapOnVSync(image_buffer)


        thread_line_1 = threading.Thread(target=line_1_set_image, args=(image_buffer,self.line_1_image_etc))
        thread_line_1.start()

        thread_line_2 = threading.Thread(target=line_2_set_image, args=(image_buffer,self.line_2_image_etc))
        thread_line_2.start()          

        thread_line_draw = threading.Thread(target=all_line_draw_image, args=(image_buffer,))
        thread_line_draw.start()        

    def run(self):
        self.load_image()
        self.draw_image()
        while True:
            schedule.run_pending()
            time.sleep(1)


# Main function
# e.g. call with
#  sudo ./image-scroller.py --chain=4
# if you have a chain of four
if __name__ == "__main__":
    image_scroller = ShowContents()
    if (not image_scroller.process()):
        image_scroller.print_help()
