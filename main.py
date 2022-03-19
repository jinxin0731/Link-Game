# _*_coding:utf-8_*_
# reference: https://www.runoob.com/python/python-gui-tkinter.html
# reference: https://www.tutorialspoint.com/python/python_gui_programming.htm

import tkinter as tk
import pygame
from PIL import Image, ImageTk
import random
import numpy

'''
define the position of icon in matrix
'''


class Point:
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def is_equal(self, point):
        if self.row == point.row and self.column == point.column:
            return True
        else:
            return False


class MainWindow:
    # the size of the window
    _gameWidth = 750
    _gameHeight = 750
    # the list of map of the game
    _map = []
    # the list of icons of the game
    _icons = []
    # the number of blocks each row and column
    _gameSize = 10
    # the number of kinds of icons
    _iconCount = int(_gameSize * _gameSize / 4)
    # the size of icons
    _iconWidth = 70
    _iconHeight = 70
    _margin = 25
    # first time click the icon
    _isFirst = True
    # game start or not
    _isGameStart = False
    # two icon are connected
    LINK_LINK = 1
    # two icon are not connected
    NONE_LINK = 0
    # two icon are connected next to each other
    NEIGHBOR_LINK = 10
    # two icon are connected in a line
    LINE_LINK = 11
    # two icon are connected through a corner
    ONE_LINK = 12
    # two icon are connected through two corners
    TWO_LINK = 13
    EDGE_LINK = 14
    EMPTY = -1

    def __init__(self):
        # create the window in the game and in the center of the screen
        self.window = tk.Tk()
        self.window.title("Link Game")
        self.window.minsize(self._gameWidth, self._gameHeight)
        self.window_center(self._gameWidth, self._gameWidth)
        # add components
        self.add_components()
        # play and stop music
        pygame.mixer.init()
        self.play_music(music="bg.mp3")
        # draw background picture through canvas
        self.background_im = False
        self.background_win = False
        self.draw_background()
        self.init_icon_list()
        self.window.mainloop()
        self._formerPoint = 0
        self.pt1 = 0
        self.pb1 = 0
        self.pl1 = 0
        self.pr1 = 0
        self.pt2 = 0
        self.pb2 = 0
        self.pl2 = 0
        self.pr2 = 0

    '''
    place window in the screen center
    the origin of window = screenwidth / 2 - width / 2, screenheight / 2 - height / 2
    '''
    def window_center(self, width, height):
        screenwidth = self.window.winfo_screenwidth()
        screenheight = self.window.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, screenwidth / 2 - width / 2, screenheight / 2 - height / 2)
        self.window.geometry(size)

    '''
    add menu, canvas in the window
    menu function: start the game, refresh the game
    canvas function: add background picture
    '''
    def add_components(self):
        # menu
        self.menubar = tk.Menu(self.window, bg="lightgrey", fg="black")
        self.file_menu = tk.Menu(self.menubar, bg="lightgrey", fg="black")
        self.menubar.add_cascade(label="click here", menu=self.file_menu)
        self.file_menu.add_command(label="new game", command=self.file_menu_clicked, accelerator="Ctrl+N")
        self.file_menu.add_command(label="end game", command=self.file_end, accelerator="Ctrl+N")
        self.window.configure(menu=self.menubar)
        # canvas
        self.canvas = tk.Canvas(self.window, bg="white", width=self._gameWidth, height=self._gameHeight)
        self.canvas.pack()
        # bind mouse actions
        self.canvas.bind('<Button-1>', self.click_icon)

    def draw_background(self):
        self.background_im = ImageTk.PhotoImage(file="bg.png")
        self.canvas.create_image((0, 0), anchor="nw", image=self.background_im)

    '''
    when click 'new game'
    game starts or refreshes, map initializes, music stops
    '''
    def file_menu_clicked(self):
        self.stop_music()
        self.init_map()
        self.draw_map()
        self._isGameStart = True

    def file_end(self):
        self.window.destroy()

    def play_music(self, music, volume=0.5):
        pygame.mixer.music.load(music)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()

    def stop_music(self):
        pygame.mixer.music.stop()

    '''
    initialize the game map
    we have 100 blocks in total and 25 kinds of icons
    every icon shows 4 times in random
    use numpy turn list into a 10 * 10 matrix
    the value of matrix is the index of icons
    '''
    def init_map(self):
        records = []
        for i in range(self._iconCount):
            for j in range(4):
                records.append(i)
        random.shuffle(records)
        self._map = numpy.array(records).reshape(10, 10)
        print(self._map)

    '''
    get x and y position of top left point of the icon
    '''
    def get_x(self, row):
        return self._margin + row * self._iconWidth

    def get_y(self, column):
        return self._margin + column * self._iconHeight

    def get_coordinate(self, row, column):
        return self.get_x(row), self.get_y(column)

    '''
    turn matrix position into x and y position of the block the player clicked
    '''
    def get_click_point(self, x, y):
        try:
            for row in range(self._gameSize):
                x1 = self.get_x(row)
                x2 = self.get_x(row + 1)
                if x1 <= x < x2:
                    point_row = row

            for column in range(self._gameSize):
                y1 = self.get_y(column)
                y2 = self.get_y(column + 1)
                if y1 <= y < y2:
                    point_column = column

            return Point(point_row, point_column)

        except Exception as ex:
            print(type(ex), "something wrong")

    '''
    open all the icons and put into a list
    '''
    def init_icon_list(self):
        try:
            for i in range(int(self._iconCount)):
                file_path = 'image/%d.jpg' % i
                t_img = Image.open(file_path).resize((self._iconWidth, self._iconHeight))
                self._icons.append(ImageTk.PhotoImage(image=t_img))

        except Exception as ex:
            print(type(ex), "wrong picture name")
            file_path = 'image/%d.jpg' % 0
            t_img = Image.open(file_path).resize((self._iconWidth, self._iconHeight))
            self._icons.append(ImageTk.PhotoImage(image=t_img))

    '''
    put icons into map according to the value in the matrix
    the index of list == the value of matrix
    '''
    def draw_map(self):
        for row in range(self._gameSize):
            for column in range(self._gameSize):
                index = self._map[row][column]
                x, y = self.get_coordinate(row, column)
                self.canvas.create_image((x, y), image=self._icons[index], anchor='nw', tags='image%d%d' % (row, column))

    '''
    when game start and left click the icon, it has a red frame
    '''
    def click_icon(self, event):
        if self._isGameStart:
            point = self.get_click_point(event.x, event.y)
            if self._isFirst:
                print("the first click")
                self._isFirst = False
                self.red_frame(point)
                self._formerPoint = point
            else:
                print("the second click")
                if point.is_equal(self._formerPoint):
                    print("click the same icon")
                    self.canvas.delete("rectRedOne")
                    self._isFirst = True
                else:
                    print("click a different icon")
                    link_type = self.get_type(self._formerPoint, point)
                    print(link_type)
                    if link_type['type'] != self.NONE_LINK:
                        self.clear_icons(self._formerPoint, point)
                        self.canvas.delete("rectRedOne")
                        self._isFirst = True
                        if self.is_game_end():
                            self.end_background()
                            self._isGameStart = False
                    else:
                        self._formerPoint = point
                        self.canvas.delete("rectRedOne")
                        self.red_frame(point)

    '''
    calculate the position of four points of icon clicked
    red frame the icon
    '''
    def red_frame(self, point):
        lt_x, lt_y = self.get_coordinate(point.row, point.column)
        rb_x, rb_y = self.get_coordinate(point.row + 1, point.column + 1)
        self.canvas.create_rectangle(lt_x, lt_y, rb_x, rb_y, outline='red', tag='rectRedOne')

    '''
    the types of how icons link
    '''
    def get_type(self, p1, p2):
        if self._map[p1.row][p1.column] != self._map[p2.row][p2.column]:
            print("two icons are not connected")
            return {'type': self.NONE_LINK}

        if self.is_neighbor(p1, p2):
            print("two icons to be connected next to each other")
            return {'type': self.NEIGHBOR_LINK}
        elif self.is_straight_link(p1, p2):
            print("two icons are linked in a straight line")
            return {'type': self.LINE_LINK}
        elif self.is_one_corner(p1, p2):
            print("two icons are connected through a corner")
            return {'type': self.ONE_LINK}
        elif self.is_two_corner(p1, p2):
            print("two icons are connected through two corners")
            return {'type': self.TWO_LINK}
        elif self.is_edge(p1, p2):
            print("two icons are connected through two corners")
            return {'type': self.EDGE_LINK}

        return {'type': self.NONE_LINK}

    '''
    delete two same icons
    '''
    def clear_icons(self, p1, p2):
        self.canvas.delete('image%d%d' % (p1.row, p1.column))
        self.canvas.delete('image%d%d' % (p2.row, p2.column))

        self._map[p1.row][p1.column] = self.EMPTY
        self._map[p2.row][p2.column] = self.EMPTY

    '''
    if two icons to be connected next to each other
    '''
    def is_neighbor(self, p1, p2):
        # in the same vertical direction, determine the upper and lower positions
        if p1.column == p2.column:
            if p2.row < p1.row:
                if p2.row + 1 == p1.row:
                    return True
            else:
                if p1.row + 1 == p2.row:
                    return True

        # in the same horizontal direction, determine the left anf right positions
        if p1.row == p2.row:
            if p2.column < p1.column:
                if p2.column + 1 == p1.column:
                    return True
            else:
                if p1.column + 1 == p2.column:
                    return True

        return False

    '''
    if two icons are linked in a straight line
    '''
    def is_straight_link(self, p1, p2):
        # in the same horizontal direction, determine the left anf right position
        if p1.row == p2.row:
            if p1.column > p2.column:
                start = p2.column
                end = p1.column
            else:
                start = p1.column
                end = p2.column
            for column in range(start + 1, end):
                if self._map[p1.row][column] != self.EMPTY:
                    return False
            return True

        # in the same vertical direction, determine the supper and lower positions
        if p1.column == p2.column:
            if p1.row > p2.row:
                start = p2.row
                end = p1.row
            else:
                start = p1.row
                end = p2.row
            for row in range(start + 1, end):
                if self._map[row][p1.column] != self.EMPTY:
                    return False
            return True

        return False

    '''
    if two icons are connected through a corner
    corner is empty
    corner to p1 is straightly linked
    corner to p2 is straightly linked
    '''
    def is_one_corner(self, p1, p2):
        pointCorner = Point(p1.row, p2.column)
        if self.is_empty(pointCorner) and self.is_straight_link(p1, pointCorner) and \
                self.is_straight_link(p2, pointCorner):
            return pointCorner

        pointCorner = Point(p2.row, p1.column)
        if self.is_empty(pointCorner) and self.is_straight_link(p1, pointCorner) and \
                self.is_straight_link(p2, pointCorner):
            return pointCorner

        return False

    '''
    if the corner is empty
    '''
    def is_empty(self, point):
        if self._map[point.row][point.column] == self.EMPTY:
            return True
        else:
            return False

    '''
    if two icons are connected through tow corners:
    tow corners are empty
    corner 1 to p1 is straightly linked
    corner 2 to p2 is straightly linked
    corner 1 to corner 2 is straightly linked
    '''
    def is_two_corner(self, p1, p2):
        # in horizontal direction
        for column in range(self._gameSize):
            if column == p1.column or column == p2.column:
                continue
            pointCorner1 = Point(p1.row, column)
            pointCorner2 = Point(p2.row, column)
            if self.is_straight_link(p1, pointCorner1) and self.is_straight_link(pointCorner1, pointCorner2) and \
                    self.is_straight_link(p2, pointCorner2) and self.is_empty(pointCorner1) and self.is_empty(
                pointCorner2):
                return {'p1': pointCorner1, 'p2': pointCorner2}

        # in vertical direction
        for row in range(self._gameSize):
            if row == p1.row or row == p2.row:
                continue
            pointCornor1 = Point(row, p1.column)
            pointCornor2 = Point(row, p2.column)
            if self.is_straight_link(p1, pointCornor1) and self.is_straight_link(pointCornor1, pointCornor2) and \
                    self.is_straight_link(p2, pointCornor2) and self.is_empty(pointCornor1) and self.is_empty(
                pointCornor2):
                return {'p1': pointCorner1, 'p2': pointCorner2}

    '''
    icons in the edges of the canvas
    '''
    def is_edge(self, p1, p2):
        try:
            if (p1.row == p2.row) and (p1.row == 0 or p1.row == 9):
                self.clear_icons(p1, p2)
                return True

            elif (p1.column == p2.column) and (p1.column == 0 or p1.column == 9):
                self.clear_icons(p1, p2)
                return True

            for i in range(p1.row):
                if self._map[i][p1.column] != self.EMPTY:
                    self.pt1 = -1
                    break
                self.pt1 = 0

            for i in range(p1.row + 1, self._gameSize):
                if self._map[i][p1.column] != self.EMPTY:
                    self.pb1 = -1
                    break
                self.pb1 = 0

            for i in range(p1.column):
                if self._map[p1.row][i] != self.EMPTY:
                    self.pl1 = -1
                    break
                self.pl1 = 0

            for i in range(p1.column + 1, self._gameSize):
                if self._map[p1.row][i] != self.EMPTY:
                    self.pr1 = -1
                    break
                self.pr1 = 0

            for i in range(p2.row):
                if self._map[i][p2.column] != self.EMPTY:
                    self.pt2 = -1
                    break
                self.pt2 = 0

            for i in range(p2.row + 1, self._gameSize):
                if self._map[i][p2.column] != self.EMPTY:
                    self.pb2 = -1
                    break
                self.pb2 = 0

            for i in range(p2.column):
                if self._map[p2.row][i] != self.EMPTY:
                    self.pl2 = -1
                    break
                self.pl2 = 0

            for i in range(p2.column + 1, self._gameSize):
                if self._map[p2.row][i] != self.EMPTY:
                    self.pr2 = -1
                    break
                self.pr2 = 0

            if (p1.row == 0 or self.pt2 == 0) and (self.pt1 == 0 or p2.row == 0):
                self.clear_icons(p1, p2)
                return True

            if (p1.row == 9 or self.pt2 == 0) and (self.pt1 == 0 or p2.row == 9):
                self.clear_icons(p1, p2)
                return True

            if (p1.column == 0 or self.pt2 == 0) and (self.pt1 == 0 or p2.column == 0):
                self.clear_icons(p1, p2)
                return True

            if (p1.column == 9 or self.pt2 == 0) and (self.pt1 == 0 or p2.column == 9):
                self.clear_icons(p1, p2)
                return True

            if (self.pt1 == 0 or self.pt2 == 0) and self.pt1 == self.pt2:
                self.clear_icons(p1, p2)
                return True

            if (self.pb1 == 0 or self.pb2 == 0) and self.pb1 == self.pb2:
                self.clear_icons(p1, p2)
                return True

            if (self.pl1 == 0 or self.pl2 == 0) and self.pl1 == self.pl2:
                self.clear_icons(p1, p2)
                return True

            if (self.pr1 == 0 or self.pr2 == 0) and self.pr1 == self.pr2:
                self.clear_icons(p1, p2)
                return True

            return False

        except Exception as ex:
            print("{'type': 14}")
            self.clear_icons(p1, p2)
            return True

    def is_game_end(self):
        for column in range(self._gameSize):
            for row in range(self._gameSize):
                if self._map[row][column] != self.EMPTY:
                    return False
        return True

    def end_background(self):
        self.background_win = ImageTk.PhotoImage(file="win.png")
        self.canvas.create_image((275, 275), anchor="nw", image=self.background_win)


if __name__ == "__main__":
    MainWindow()
