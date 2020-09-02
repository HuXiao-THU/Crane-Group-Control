import tkinter as tk
import math
import time
from Crane_discrete import Crane
from World import Target
from math import pi

class Renderer(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Crane Control Demo')
        self.root.geometry('1600x600+50+50')

        self.main_frame = tk.Frame(self.root, width=1600, height=600, bg='pink')
        self.main_frame.pack()
        self.plane_frame = tk.Frame(self.main_frame, width=800, height=600, bg='blue')
        self.plane_frame.pack(side='left')
        self.vertical_frame = tk.Frame(self.main_frame, width=800, height=600, bg='green')
        self.vertical_frame.pack(side='right')

        self.plane = tk.Canvas(self.plane_frame, width=800, height=600, bg='white')
        self.plane.pack()
        self.vertical = tk.Canvas(self.vertical_frame, width=800, height=600, bg='white')
        self.vertical.pack()

        self.current_crane = 0

        self.crane_image = tk.PhotoImage(file='./data/crane.png')
        
    def render(self, crane_list, target_list, env_state):
        """
        render one frame

        paras:
        crane_list(list): list of Crane objects
        target_list(list): list of targets in (x, y, )
        env_state(dict): dict of the environment states
        """
        # self.plane.destroy()
        # self.plane = tk.Canvas(self.plane_frame, width=800, height=600, bg='white')
        self.plane.delete(tk.ALL)
        for crane in crane_list:
            self.plane.create_polygon(crane.x, crane.y - 2, crane.x - 2, crane.y + 1, crane.x + 2, crane.y + 1, fill='black')
            self.plane.create_oval(crane.x - crane.R1, crane.y - crane.R1, crane.x + crane.R1, crane.y + crane.R1)
            self.plane.create_line(crane.x - math.cos(crane.arm_theta / 180 * pi) * crane.R2,
                                    crane.y - math.sin(crane.arm_theta / 180 * pi) * crane.R2,
                                    crane.x + math.cos(crane.arm_theta / 180 * pi) * crane.R1,
                                    crane.y + math.sin(crane.arm_theta / 180 * pi) * crane.R1)
            x = crane.x + crane.car_pos * math.cos(crane.arm_theta / 180 * pi)
            y = crane.y + crane.car_pos * math.sin(crane.arm_theta / 180 * pi)
            self.plane.create_oval(x-1, y-1, x+1, y+1, fill='black')
        
        # car range: y = 200~550, x 大约 250~700
        self.vertical.delete(tk.ALL)
        if self.current_crane != None:
            self.vertical.create_image(0,50,anchor=tk.NW, image=self.crane_image)
            crane = crane_list[self.current_crane]
            x = 250 + (crane.car_pos - crane.car_limit_near_end) * 450 / (crane.car_limit_far_end - crane.car_limit_near_end)
            y = 200 + (crane.height - crane.hook_height) * 350 / crane.height
            print(y,"   ",crane.hook_height)
            self.vertical.create_line(x,200,x,y,width=2)
            self.vertical.create_rectangle(x-10, y-10, x+10, y+10)
            y = 200 + (crane.height - target_list[self.current_crane].h) * 350 / crane.height
            self.vertical.create_line(0,y,800,y,fill='red')



        self.plane.scale('all',0,0,3,3)
        self.root.update()


if __name__ == '__main__':
    renderer = Renderer()
    crane = Crane()
    crane.x = 100
    crane.y = 100
    crane.hook_height = 5
    target = Target()
    target.h = 3
    while True:
        crane.rotate(1)
        crane.moveCar(1)
        crane.moveHook(-1)
        renderer.render([crane], [target], None)
        time.sleep(1)