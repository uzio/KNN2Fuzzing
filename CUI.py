# -*- coding: UTF-8 -*-
import os
import sys
import Tkinter as tk
from Tkinter import *
import tkFileDialog as tkfd
from SearchHosts import *
from get_inet import get_net


reload(sys)  
sys.setdefaultencoding('utf8') 

class Application(tk.Frame):
    '''
    面向对象的方式创建GUI
    '''

    def __init__(self, master = None):
        tk.Frame.__init__(self,  master)
        self.master = master
        self.grid(row = 0,column = 0,sticky =N)
        
        self.createWidget()
        self.loadWIdget()
        

    def createWidget(self):
        '''创建组件'''
        # 参数类别
        self.lb_target_hosts = Label(self, text = '目标网段')
        self.lb_target_port = Label(self, text = '目标端口')
        self.lb_target_case = Label(self, text = '测试用例')
        self.lb_job_id = Label(self, text = '工作编号')
        self.lb_fuzz_count = Label(self, text = '模糊次数')
        self.lb_interface = Label(self, text = '活动网卡名')
        # 输入
        hosts = StringVar()
        lo_host = get_net()[0]
        hosts.set(lo_host)
        # hosts.set('0.0.0.0/24') # 检索通用主机
        self.ety_target_hosts = Entry(self, textvariable = hosts)

        port = StringVar()
        port.set('102')# 默认snap7
        self.ety_port = Entry(self,textvariable = port)

        self.filename = StringVar()
        self.ety_target_case = Entry(self,textvariable = self.filename)

        job_id = StringVar()
        self.ety_job_id = Entry(self,textvariable = job_id)

        count = IntVar()
        count.set(2)
        self.ety_fuzz_count = Entry(self,textvariable = count)

        iface = StringVar()
        iface.set(get_net()[1])
        # iface.set('lo')# 默认本地环回
        self.ety_interface = Entry(self,textvariable = iface)
        # 功能
        self.btn_search = Button(self, text = '搜索', command = self.getHosts)
        self.btn_choose_case = Button(self, text = '选择用例', command = self.chooseFile)
        self.btn_start_fuzz = Button(self, text = '开始测试', command = self.sendArg)
        self.btn_quit = Button(self, text = '退出', command = root.destroy)
        #  交互
        self.txt_target = Text(root, width = 72,height = 12, bg = 'white')
        self.txt_target.config(state=DISABLED)

    def loadWIdget(self):
        '''挂载组件'''
        self.lb_target_hosts.grid(row = 0,column = 0, pady = 2,  sticky = E)
        self.ety_target_hosts.grid(row = 0,column = 1, pady = 2)
        self.lb_target_port.grid(row = 1,column = 0, pady = 2,  sticky = E)
        self.ety_port.grid(row = 1,column = 1, pady = 2)
        self.btn_search.grid(row = 1,column = 2, padx = 2, sticky = W)
        self.lb_target_case.grid(row = 2,column = 0, pady = 2, sticky = E)
        self.ety_target_case.grid(row = 2,column = 1,pady = 2)
        self.btn_choose_case.grid(row = 2,column = 2, padx = 2, sticky = W)
        self.lb_job_id.grid(row = 3,column = 0, pady = 2,  sticky = E)
        self.ety_job_id.grid(row = 3,column = 1, pady = 2)
        self.lb_fuzz_count.grid(row = 4,column = 0, pady = 2,  sticky = E)
        self.ety_fuzz_count.grid(row = 4,column = 1, pady = 2)
        self.lb_interface.grid(row = 5,column = 0, pady = 2,  sticky = E)
        self.ety_interface.grid(row = 5,column = 1, pady = 2)
        self.btn_start_fuzz.grid(row = 6,column = 1)
        self.btn_quit.grid(row = 6,column = 2, padx = 5,  sticky = E)
        self.txt_target.grid(row = 7,column = 0, rowspan=3,padx = 7, pady = 5, sticky = N)

    # 功能
    def getHosts(self): 
        '''获取目标网段内开放指定端口的主机信息'''
        print('正在搜索...\n')
        self.txt_target.config(state=NORMAL)
        ip = SearchHosts(self.ety_target_hosts.get(),self.ety_port.get())
        ip_list = ip.searchTCP()
        lenth = len(ip_list)
        for i in range(0,lenth):
            self.txt_target.insert(END,'No.{0} > {1} Host: {2} >>>{3}. | service~# {4} \n'.format(i+1, ip_list[i]['port'], ip_list[i]['host'], ip_list[i]['status'], ip_list[i]['name']))
        self.txt_target.insert(END,'..搜索完成.\n')
        self.txt_target.config(state=DISABLED) 
        print('..搜索完成.\n')
    
    def chooseFile(self):
        '''选择用例'''
        self.path = tkfd.askopenfilename(initialdir = './cases/')
        self.filename.set(self.path.split("/")[-1].split(".")[0])
        print('path >' + os.path.split(self.path)[0])
        print('case >> ' + self.filename.get())
        
    def sendArg(self):
        '''提交模糊测试参数'''
        params={
            'FUZZ_COUNT':int(self.ety_fuzz_count.get()),
            'DELAY':2,
            'TARGET_IP': self.ety_target_hosts.get(),
            'TIME_OUT':2,
            'JOB_ID':self.ety_job_id.get(),
            'INTERFACE':self.ety_interface.get(),
            }

        abspath =  os.path.split(self.path)[0] 
        sys.path.append(abspath)
        module = __import__(self.filename.get())
        module.fuzz(params)
        sys.path.remove(abspath)
        
        
if __name__=='__main__':
    root = tk.Tk()
    root.geometry("600x400+720+320")
    root.title("交互界面-beta.v2.1")
    app = Application(master = root)
    root.mainloop()
    print('bye~')