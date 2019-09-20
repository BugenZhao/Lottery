# coding=utf_8
import random
import re
import time
import tkinter
import tkinter.simpledialog
import tkinter.font


def Get_HWND_DPI(window_handle):
    import os
    if os.name == "nt":
        from ctypes import windll, pointer, wintypes
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass  # this will fail on Windows Server and maybe early Windows
        DPI100pc = 96  # DPI 96 is 100% scaling
        DPI_type = 0
        # MDT_EFFECTIVE_DPI = 0, MDT_ANGULAR_DPI = 1, MDT_RAW_DPI = 2
        winH = wintypes.HWND(window_handle)
        monitorhandle = windll.user32.MonitorFromWindow(
            winH, wintypes.DWORD(2))  # MONITOR_DEFAULTTONEAREST = 2
        X = wintypes.UINT()
        Y = wintypes.UINT()
        try:
            windll.shcore.GetDpiForMonitor(
                monitorhandle, DPI_type, pointer(X), pointer(Y))
            return X.value, Y.value, (X.value + Y.value) / (2 * DPI100pc)
        except Exception:
            return 96, 96, 1  # Assume standard Windows DPI & scaling
    else:
        return None, None, 1  # What to do for other OSs?


def TkGeometryScale(s, cvtfunc):
    patt = r"(?P<W>\d+)x(?P<H>\d+)\+(?P<X>\d+)\+(?P<Y>\d+)"  # format "WxH+X+Y"
    R = re.compile(patt).search(s)
    G = str(cvtfunc(R.group("W"))) + "x"
    G += str(cvtfunc(R.group("H"))) + "+"
    G += str(cvtfunc(R.group("X"))) + "+"
    G += str(cvtfunc(R.group("Y")))
    return G


def MakeTkDPIAware(TKGUI):
    TKGUI.DPI_X, TKGUI.DPI_Y, TKGUI.DPI_scaling = Get_HWND_DPI(
        TKGUI.winfo_id())
    TKGUI.TkScale = lambda v: int(float(v) * TKGUI.DPI_scaling)
    TKGUI.TkGeometryScale = lambda s: TkGeometryScale(s, TKGUI.TkScale)


currentPos = 0
numbers = []

defaultMaxNumber = 350
maxNumber = defaultMaxNumber
for x in range(maxNumber):
    numbers.append(x)
random.shuffle(numbers)

defaultTitle = '2018 级西工大附中 - 上海交通大学宣讲活动抽奖器 by BugenZhao - 当前人数：'


def getNextNumber():
    global currentPos

    if currentPos >= maxNumber:
        currentPos = 0
        random.shuffle(numbers)
    ret = numbers[currentPos] + 1
    currentPos += 1
    return ret


def operateWindowForbidden():
    pass


class Application(tkinter.Tk):

    def __init__(self):
        super().__init__()
        self.title(defaultTitle + str(maxNumber))
        self.maxsize(width=1113, height=629)
        self.resizable(False, False)
        self.protocol(name="WM_DELETE_WINDOW", func=lambda:
                      tkinter.messagebox.showwarning(
                          title='提示', message='使用菜单中的 “退出” 来退出抽奖器'))

        self.bgImage = tkinter.PhotoImage(file='bg2.png')
        self.bgLabel = tkinter.Label(master=self, image=self.bgImage)
        self.bgLabel.pack(side='top')

        self.ftBig = tkinter.font.Font(
            family='Bahnschrift Condensed', size=30)
        self.ftLittle = tkinter.font.Font(
            family='Bahnschrift Condensed', size=20)

        self.numberImage = tkinter.PhotoImage(file='back.gif')
        self.numberLabel = tkinter.Label(
            master=self, text='000', font=self.ftBig, compound='center',
            fg='#F8F8FF', image=self.numberImage)
        self.numberLabel.place(relx=0.505, rely=0.63, anchor='center')

        self.goButton = tkinter.Button(self, text='G O !',
                                       fg='#FF4500', height=1, width=6,
                                       activeforeground='#FF4500',
                                       bg='#F8F8FF',
                                       activebackground='#F8F8FF',
                                       font=self.ftLittle,
                                       command=self.showNextNumber)
        self.goButton.place(relx=0.505, rely=0.85, anchor='center')

        self.historyCnt = 0
        self.histories = []

        self.createMenu()

    def createMenu(self):
        menus = ['抽奖', '帮助']
        items = [['设置总人数',  '-', '重置抽奖序列', '仅清空中奖列表',
                  '-', '在控制台中抽取一个数字', '退出'],
                 ['关于抽奖器']]
        callbacks = [[self.setMaxNumber, None, self.allReset, self.clear,
                      None, self.getNumberInConsole, self.quit],
                     [self.aboutMe]]
        menubar = tkinter.Menu(self)
        for i, x in enumerate(menus):
            m = tkinter.Menu(menubar, tearoff=0)
            for item, callback in zip(items[i], callbacks[i]):
                if isinstance(item, list):
                    sm = tkinter.Menu(menubar, tearoff=0)
                    for subitem, subcallback in zip(item, callback):
                        if subitem == '-':
                            sm.add_separator()
                        else:
                            sm.add_command(
                                label=subitem, command=subcallback,
                                compound='left')
                    m.add_cascade(label=item[0], menu=sm)
                elif item == '-':
                    m.add_separator()
                else:
                    m.add_command(label=item, command=callback,
                                  compound='left')
            menubar.add_cascade(label=x, menu=m)
        self.config(menu=menubar)

    def setMaxNumber(self):
        global maxNumber
        global currentPos

        ret = tkinter.simpledialog.askinteger(
            title='设置最大人数', prompt='当前最大人数：' + str(maxNumber) +
            '\n输入新的最大人数：')
        if ret is not None:
            maxNumber = ret
            currentPos = 0
            numbers.clear()
            for x in range(maxNumber):
                numbers.append(x)
            random.shuffle(numbers)
            self.title(defaultTitle + str(maxNumber).zfill(3))
            self.historyCnt = 0
            for button in self.histories:
                button.place_forget()
            self.histories.clear()
            self.numberLabel.config(text='000')

    def getNumberInConsole(self):
        print(getNextNumber())

    def justLookLook(self):
        global currentPos

        infoMessage = ''
        for x in range(12):
            infoMessage += str(numbers[currentPos + x] + 1).zfill(3)
        tkinter.messagebox.showinfo(message=infoMessage)

    def aboutMe(self):
        infoMessage = ''
        try:
            for x in range(12):
                infoMessage += str(numbers[currentPos + x] + 1).zfill(3)
        except Exception as e:
            infoMessage = str(e)

        tkinter.messagebox.showinfo(
            title='关于 bzRandom 抽奖器', message='build 190127, BugenZhao 2019.\n'
            + '仅限 2018 届西工大附中 - 上海交通大学宣讲活动使用。\n'
            + infoMessage)

    def showNextNumber(self):
        for i in range(15):
            time.sleep(0.1)
            self.numberLabel.config(
                text=str(random.randint(0, maxNumber - 1) + 1).zfill(3),
                fg='#BBBBBB')
            self.update()
        ret = getNextNumber()
        self.numberLabel.config(text=str(ret).zfill(3), fg='#BBBBBB')
        self.update()
        time.sleep(0.15)
        self.numberLabel.config(fg='#F8F8FF')

        self.histories.append(tkinter.Button(master=self, text=str(
            ret).zfill(3), font=self.ftLittle, compound='center',
            width=3,
            command=self.makeUnabled(self.historyCnt)))
        self.histories[self.historyCnt].place(
            relx=self.historyCnt*0.036, rely=1, anchor='sw')
        self.historyCnt += 1

    def makeUnabled(self, i):
        def do_makeUnabled():
            button = self.histories[i]
            button.config(text='000')
        return do_makeUnabled

    def allReset(self):
        global currentPos

        currentPos = 0
        random.shuffle(numbers)
        self.historyCnt = 0
        for button in self.histories:
            button.place_forget()
        self.histories.clear()
        self.numberLabel.config(text='000')

    def clear(self):
        self.historyCnt = 0
        for button in self.histories:
            button.place_forget()
        self.histories.clear()


if __name__ == '__main__':
    bzApplication = Application()
    MakeTkDPIAware(bzApplication)
    print('终端调试窗口，请勿关闭')
    bzApplication.mainloop()
