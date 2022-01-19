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
from PIL import Image, ImageFont, ImageDraw
import serial

#line_1　【表示1行目】32x64 RGBLEDの「1行目 12x64」
#line_2　【表示2行目】32x64 RGBLEDの「2行目 20x64」


class ShowContents(SampleBase):

    LINE_1_START_Y_POS:int = 0
    LINE_2_START_Y_POS:int = 12

    LINE_1_TEXT_SIZE:int = 12

    TEXT_SCROLL_SPEED = 0.01

    IMAGE_DIR_PASS = "/home/pi/ElectricBoardContentsFolder"

    Temp = 0
    Humidity = 0
    HeatIndex = 0

    #表示するためのイメージデータ等のデータが入る変数(RGBに変換後のもの)
    line_1_image_etc = None
    line_2_image_etc = None



    def __init__(self, *args, **kwargs):
        super(ShowContents, self).__init__(*args, **kwargs)

        schedule.every(2).minutes.do(self.load_image)
        schedule.every(1).minutes.do(self.read_sensor)

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

            line_dir = os.path.join(ShowContents.IMAGE_DIR_PASS, dir) #各LineごとのDir名作成
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

        ShowContents.line_1_image_etc = display_information_data[0]
        ShowContents.line_2_image_etc = display_information_data[1]

    def read_sensor(self):
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2)
        sensor_rowdata = ser.readline()
        ser.close()

        sensor_data = sensor_rowdata.decode("utf-8")

        sensor_data_list = sensor_data.split()

        if sensor_data_list[0] == "Data:":
            ShowContents.Temp = sensor_data_list[2]
            ShowContents.Humidity = sensor_data_list[4]
            ShowContents.HeatIndex = sensor_data_list[6]

        elif sensor_data_list[0] != "Data:":
            ShowContents.Temp = "センサ"
            ShowContents.Humidity = "接続"
            ShowContents.HeatIndex = "異常" 

        print(ShowContents.Temp)
        print(ShowContents.Humidity)
        print(ShowContents.HeatIndex)



    def draw_image(self):
        #グローバル変数のimage_buffer
        global image_buffer
        #キャンバス的なものを作る
        image_buffer = self.matrix.CreateFrameCanvas()
        
        #描画部分
        def line_1_set_image():
            #切り替え表示
            #グローバル変数のimage_bufferに描画データを書き込む
            global image_buffer

            #今選択している画像
            selecting_drawing_image = 0
            #今描画している画像のポジション(固定表示なので0)
            line1_x_pos = 0

            font = ImageFont.truetype("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", ShowContents.LINE_1_TEXT_SIZE)

            #Line1の画像表示ループ
            #各画像の表示を処理します
            while True:
                #画像データの読み出しと、縦横サイズの取得
                line_1_image = ShowContents.line_1_image_etc[2][selecting_drawing_image]
                img_width, img_height = line_1_image.size

                #表示秒数を取得
                display_seconds = ShowContents.line_1_image_etc[1][selecting_drawing_image]

                #画像データをディスプレイにセット
                image_buffer.SetImage(line_1_image, -line1_x_pos, ShowContents.LINE_1_START_Y_POS)
                image_buffer.SetImage(line_1_image, -line1_x_pos, ShowContents.LINE_1_START_Y_POS)
                time.sleep(0.5)
                image_buffer.SetImage(line_1_image, -line1_x_pos, ShowContents.LINE_1_START_Y_POS)

                #次の表示画像にセットされた値が、画像等のデータを格納した配列の大きさを超えている場合は
                # 0(先頭の画像)にセットしなおして
                # 日付・時刻・気温・湿度を表示する
                if  selecting_drawing_image == len(ShowContents.line_1_image_etc[0])-1:
                    #最後の画像に対しての表示待ち
                    time.sleep(int(display_seconds))

                    #https://a-tak.com/blog/2017/03/raspberry-pi-led-clock-4/
                    #今の時刻を取得
                    dt_now = datetime.now()

                    date_str = str(dt_now.month) + "/" + str(dt_now.day)
                    
                    h = (" " + str(dt_now.hour))[-2:]
                    #スペースを頭に着けて最後から2文字背取得。1-9時の間も真ん中に時計が表示されるようにする考慮
                    time_str = h + ":" + dt_now.strftime("%M")

                    date_str = "   " + date_str + "       "
                    time_str = "  " + time_str + "       "
                    temp_str = "気温:" + str(ShowContents.Temp) + "   "
                    humidity_str = "湿度:" + str(ShowContents.Humidity) + "   "
                    heatindex_str = "体感:" + str(ShowContents.HeatIndex) + "   "

                    realtime_contents_str = [date_str, time_str, temp_str, humidity_str, heatindex_str]

                    for realtime_content in realtime_contents_str:
                        width, height = font.getsize(realtime_content)
                        img = Image.new("RGB", (width, ShowContents.LINE_1_TEXT_SIZE), (0, 0, 0))
                        draw = ImageDraw.Draw(img)
                        draw.text((0, 0), realtime_content, (255, 255, 255), font=font)

                        image_buffer.SetImage(img, -line1_x_pos, ShowContents.LINE_1_START_Y_POS)

                        #print("日付" + date_str + "表示中")
                        time.sleep(6)

                    """
                    width, height = font.getsize(time_str)
                    img = Image.new("RGB", (width, ShowContents.LINE_1_TEXT_SIZE), (0, 0, 0))
                    draw = ImageDraw.Draw(img)
                    draw.text((0, 0), time_str, (255, 255, 255), font=font)

                    image_buffer.SetImage(img, -line1_x_pos, ShowContents.LINE_1_START_Y_POS)

                    print("時刻" + time_str + "表示中")
                    time.sleep(6)
                    """

                    display_seconds = 0
                    selecting_drawing_image = 0
                #超えていない場合は次の画像に進める
                else:
                    selecting_drawing_image += 1

                time.sleep(int(display_seconds))


        def line_2_set_image():
            #スクロール表示
            #最終整備日:2022/1/12

            #グローバル変数のimage_bufferに描画データを書き込む
            global image_buffer

            #今選択している画像
            selecting_drawing_image = 0
            #今描画している画像のポジション
            # 0のときは一番左端に画像の開始部分が来る。
            # そのため、描画できる領域(64px)以上の空白領域を画像側で入れないと、いきなり文字が表示されることになります。
            line2_x_pos = 0

            #Line2の画像表示ループ
            #各画像の表示、スクロールを処理します
            while True:
                #画像データの読み出しと、縦横サイズの取得
                line_2_image = ShowContents.line_2_image_etc[2][selecting_drawing_image]
                img_width, img_height = line_2_image.size

                #画像データをディスプレイにセット
                image_buffer.SetImage(line_2_image, -line2_x_pos, ShowContents.LINE_2_START_Y_POS)
                image_buffer.SetImage(line_2_image, -line2_x_pos + img_width, ShowContents.LINE_2_START_Y_POS)

                #実際にディスプレイのLine2の領域に描画
                image_buffer = self.matrix.SwapOnVSync(image_buffer)

                #次の描画領域(1px進む)のセット
                line2_x_pos += 1
                #もし、描画領域が[画像データ-64]のポジションに来ていたらポジションを0にリセットし、次の画像に進める
                """
                理由として、
                描画領域の値は一番左端の列に対しての値なので、画像が終わりに近づき、画像の残り幅数が64以下になって進んでいくと
                描画できる画像がないことになります。
                そのため、再び先頭の画像が出てくるという事になってしまいます。そのための対策です。
                （表示画像の末尾に空白が入っている場合はあまり関係ないです。）
                """
                if (line2_x_pos > img_width-64):
                    line2_x_pos = 0
                    selecting_drawing_image += 1
                
                #次の表示画像にセットされた値が、画像等のデータを格納した配列の大きさを超えている場合は0(先頭の画像)にセットしなおす
                if selecting_drawing_image >= len(ShowContents.line_2_image_etc[0]):
                    selecting_drawing_image = 0

                #書き換えるタイミングを調整
                time.sleep(ShowContents.TEXT_SCROLL_SPEED)


        def all_line_draw_image():
            #最終的に描画の指示を出す関数
            #グローバル変数のimage_buffer
            global image_buffer

            #永遠に画面を描画し続ける
            while True:
                image_buffer = self.matrix.SwapOnVSync(image_buffer)
                time.sleep(0.001)
                

        #全部個別のスレッドで永遠に動作させる

        thread_line_1 = threading.Thread(target=line_1_set_image)
        thread_line_1.start()

        thread_line_2 = threading.Thread(target=line_2_set_image)
        thread_line_2.start()          

        thread_line_draw = threading.Thread(target=all_line_draw_image)
        thread_line_draw.start()

    def run(self):
        self.load_image()
        self.read_sensor()
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
