import time
import threading
from FeiQ.Util.LogHelp import logger

#任务基类
class Task:
    taskname:str = ''
    deadline:int = 0 #任务执行时间，0的时候直接执行
    key:str = '' #任务关键字
    __IsCanExecute = False #延时任务设置立即执行

    execute_handler = None #任务执行函数

    #当超过当前时间的时候设置为可以执行,如果外界设置立即执行的情况下也需要执行
    def IsCanExecute(self):
        return self.__IsCanExecute or time.time() * 1000 >= self.deadline

    # 设置可以执行了
    def SetCanExecute(self):
        self.__IsCanExecute = True
        self.deadline += 1000 * 60 * 60 #防止刚好差一点时间被执行错了

    # 是立即执行的任务还是到期执行的任务
    # iWaitMillsecond = 0，线程空闲立即执行
    # iWaitMillsecond > 0，等待这些时间后执行
    def __init__(self, taskkey='', iWaitMillsecond=0,taskname=''):
        self.taskname = taskname
        self.key = taskkey
        if iWaitMillsecond == 0:
            self.SetCanExecute()
        self.deadline = time.time() * 1000 + iWaitMillsecond

    #是否是相关任务
    def IsReleateTask(self, strKey):
        return self.key.startswith(strKey)

    def __str__(self):
        return self.taskname + '@' +self.key

    def Execute(self):
        try:
            if self.execute_handler is not None:
                self.execute_handler()
        except Exception as ex:
            logger.debug(ex)

#到期执行一种任务，如果提前执行的情况，执行另外一种任务
class SwitchTask(Task):
    before_handler = None
    afert_handler = None
    # 是立即执行的任务还是到期执行的任务
    # iWaitMillsecond = 0，线程空闲立即执行
    # iWaitMillsecond > 0，等待这些时间后执行
    def __init__(self, taskkey='', iWaitMillsecond=0, taskname=''):
        Task.__init__(self, taskkey, iWaitMillsecond, taskname)

    #到期前执行一个，如果到期执行另外一个
    def Execute(self):
        try:
            nowTime = time.time() * 1000
            if self.before_handler is not None and  nowTime < self.deadline:
                self.before_handler()
            else:
                self.afert_handler()
        except Exception as ex:
            logger.debug(ex)

class TaskManager:
    CollectionLock:threading.Lock = threading.Lock()  # 容器锁
    ListTask = []  # 任务列表
    condition = threading.Condition()  # 线程使用的任务信号量
    ThreadCount = 5  # 线程数量
    StopThread = False  # 是否停止任务队列
    ThreadWaitMs = 50  # 线程执行时，等待信号量的时间

    LstThread = []  # 任务线程

    def __init__(self, iThreadCount = 5, iThreadWaitMs = 50):
        if iThreadWaitMs < 50: # 线程执行时，等待信号量的时间
            self.ThreadWaitMs = 50
        else:
            self.ThreadWaitMs = iThreadWaitMs

        if iThreadCount < 1 or iThreadCount > 20: # 线程数量
            self.ThreadCount = 5
        else:
            self.ThreadCount = iThreadCount

        self.CollectionLock: threading.Lock = threading.Lock()  # 容器锁
        self.ListTask = []  # 任务列表
        self.condition = threading.Condition()  # 线程使用的任务信号量
        Stop = False  # 是否停止任务队列

        LstThread = []  # 任务线程

        for x in range(self.ThreadCount):
            t = threading.Thread(target=self.thread_func, name='任务执行线程 ' + str(x+1))
            t.setDaemon(True)
            t.start()
            self.LstThread.append(t)

    #结束任务
    def Stop(self):
        self.StopThread = True
        for x in self.LstThread:
            x.join()

    #获取一个任务
    def __PeekTask(self):
        tk = None
        timeout = True
        if self.CollectionLock.acquire(timeout = 0.01):
            tk = next((x for x in self.ListTask if x.IsCanExecute()), None)
            if tk is not None:
                self.ListTask.remove(tk)

            self.CollectionLock.release()
            timeout = False

        return tk, timeout

    #移除不需要执行的任务
    def EraseReleateTask(self, strKey):
        if self.CollectionLock.acquire():
            ret = [x for x in self.ListTask if x.IsReleateTask(strKey)]
            for x in ret:
                self.ListTask.remove(x)

            self.CollectionLock.release()

    #设置这些任务可以直接执行
    def SetReleateTaskRun(self, strKey):
        bHasTask = False
        if self.CollectionLock.acquire():
            ret = [x for x in self.ListTask if x.IsReleateTask(strKey)]
            bHasTask = len(ret) > 0
            for x in ret:
                x.SetCanExecute()

            self.CollectionLock.release()

        if bHasTask:
            self.condition.acquire()
            self.condition.notify()
            self.condition.release()
    #线程函数
    def thread_func(self):
        logger.debug('任务线程启动')

        while not self.StopThread:
            tk, timeout = self.__PeekTask()
            if tk is not None:
                tk.Execute()
            elif timeout:
                continue
            elif self.condition.acquire():
                #等待一段时间后直接重新开始
                if self.condition.wait(self.ThreadWaitMs / 1000.0):
                    self.condition.release()
        logger.debug('线程结束')

    #添加一个任务
    def AppendTask(self,task):
        if self.CollectionLock.acquire():
            self.ListTask.append(task)
            self.CollectionLock.release()

        self.condition.acquire()
        self.condition.notify()
        self.condition.release()

    #批量添加任务
    def BatchAppendTask(self, lsttask):
        if len(lsttask) < 1:
            return
        if self.CollectionLock.acquire():
            for x in lsttask:
                self.ListTask.append(x)
            self.CollectionLock.release()

        self.condition.acquire()
        self.condition.notify(len(lsttask))
        self.condition.release()

    # 创建延时任务
    def CreateDelayTask(self, func, iDelayMillsecond, taskname="", taskKey=""):
        tk = Task(taskKey, iDelayMillsecond, taskname)

        tk.execute_handler = func

        self.AppendTask(tk)

    #创建一个立即执行的任务
    def CreateImmediatelyTask(self, func, taskname="",  taskKey=""):
        self.CreateDelayTask(func, 0, taskname, taskKey)

    #批量创建延时任务
    def BatchCreateDelayTask(self, func, taskKey, taskname, iStartDelay, iDelayStep, iCount):
        if iCount < 1:
            return

        arrTask = []
        for x in range(iCount):
            t= Task(taskKey, iStartDelay + x * iDelayStep, taskname + '_' + str(x))
            t.execute_handler = func
            arrTask.append(t)

        self.BatchAppendTask(arrTask)

    #创建开关任务
    def CreateSwitchTask(self,before_func,afert_func,taskKey, iDelayMillsecond, taskname=""):
        task = SwitchTask(taskKey, iDelayMillsecond, taskname)
        task.before_handler = before_func
        task.afert_handler = afert_func

        self.AppendTask(task)


#TaskInstance = TaskManager()