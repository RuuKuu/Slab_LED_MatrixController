import threading
import time


class Test():

    def set_str(self):
        while True:
            self.a = "this is test"
            time.sleep(5)
            self.a = "change test"
            time.sleep(5)


    def run(self):
        def test():
            self.set_str()
        thread = threading.Thread(target=test)
        thread.start()


    def draw_image(self):
        #global ans
        #ans = self.a
        #print(self.a)
        time.sleep(1)

        def line_1_draw_image(ans):
            #global ans
            print(ans)

        line_1_draw_image(self.a)


if __name__ == "__main__":
    ob = Test()
    ob.run()
    while True:
        ob.draw_image()