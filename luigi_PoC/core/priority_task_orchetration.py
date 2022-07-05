import luigi
import datetime
import time

'''
1、支持设定优先级，优先级没有层次之分，父节点优先级会被子节点优先级提升，父节点的优先级永远大于子节点
2、支持动态绑定依赖的任务
3、Namespaces, families and ids，前两者属于类，最后一个属于实例，会有参数相同的实例化缓存
4、参数解析顺序（Parameter）：一、传递给构造函数的任何值，或命令行上设置的任务级别值(应用于实例级别)；二、命令行上设置的任何值(应用于类级别)；三、配置选项（类级别）；四、提供给参数的任何默认值（类级别）
'''


class TaskA(luigi.Task):
    """
    独立的任务，看能否运行
    """
    date = luigi.DateParameter()

    @property
    def priority(self):
        if self.date > datetime.date.today() - datetime.timedelta(days=10):
            return 500
        else:
            return 20

    def run(self):
        with self.output().open('w') as output:
            print("I\'m Task A! Lonely working")
            output.write(f"I\'m Task A! Lonely working, priority={self.priority}")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))

    def output(self):
        return luigi.LocalTarget('taskA.txt')


class TaskB(luigi.Task):
    """
    任务B，初代父节点之一
    """
    date = luigi.DateParameter()

    @property
    def priority(self):
        if self.date > datetime.date.today() - datetime.timedelta(days=10):
            return 10
        else:
            return 110

    def run(self):
        with self.output().open('w') as output:
            print(f"I\'m Task B! Working, priority={self.priority}")
            output.write("I\'m Task B! Working")
            print()
            output.write(self.date.strftime("%Y-%m-%d"))
        # time.sleep(100)

    def output(self):
        return luigi.LocalTarget('taskB.txt')


class TaskC(luigi.Task):
    """
    任务C，初代父节点之一
    """
    date = luigi.DateParameter()

    # 动态设定优先级
    @property
    def priority(self):
        if self.date > datetime.date.today()-datetime.timedelta(days=10):
            return 100
        else:
            return 20

    def run(self):
        with self.output().open('w') as output:
            print(f"I\'m Task C! Working, priority={self.priority}")
            output.write("I\'m Task C! Working")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))

    def output(self):
        return luigi.LocalTarget('taskC.txt')


class TaskDDependendyNumOne(luigi.Task):
    priority = 200

    def run(self):
        with self.output().open('w') as output:
            output.write("123")
        print("D\'s dependency one!")

    def output(self):
        return luigi.LocalTarget('taskDep1.txt')


class TaskD(luigi.Task):
    """
    任务D，依赖任务B
    """
    date = luigi.DateParameter()
    priority = 20

    def run(self):
        other_target=yield TaskDDependendyNumOne()
        with self.input().open('r') as in_file:
            for line in in_file:
                print("D reading dependencies: " + line)
        with self.output().open('w') as output:
            print(f"I\'m Task D! Working, priority={self.priority}")
            output.write("I\'m Task D! Working")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))

    def output(self):
        return luigi.LocalTarget('taskD.txt')

    def requires(self):
        return TaskB(self.date)


class TaskE(luigi.Task):
    """
    任务E，依赖任务B C
    """
    date = luigi.DateParameter()
    priority = 90

    def run(self):
        for t in self.input():
            with t.open('r') as in_file:
                for line in in_file:
                    print("E reading dependencies: " + line)
        with self.output().open('w') as output:
            print(f"I\'m Task E! Working, priority={self.priority}")
            output.write("I\'m Task E! Working")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))

    def output(self):
        return luigi.LocalTarget('taskE.txt')

    def requires(self):
        return [TaskB(self.date), TaskC(self.date)]


class TaskF(luigi.Task):
    """
    任务F，依赖任务C
    """
    date = luigi.DateParameter()
    priority = 100

    def run(self):
        with self.input().open('r') as in_file:
            for line in in_file:
                print("F reading dependencies: " + line)
        with self.output().open('w') as output:
            print(f"I\'m Task F! Working, priority={self.priority}")
            output.write("I\'m Task F! Working")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))

    def output(self):
        return luigi.LocalTarget('taskF.txt')

    def requires(self):
        return TaskC(self.date)


class TaskG(luigi.Task):
    """
    任务G，依赖任务D
    """
    date = luigi.DateParameter()

    def run(self):
        with self.input().open('r') as in_file:
            for line in in_file:
                print("G reading dependencies: " + line)
        with self.output().open('w') as output:
            print(f"I\'m Task G! Working, priority={self.priority}")
            output.write("I\'m Task G! Working")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))

    def output(self):
        return luigi.LocalTarget('taskG.txt')

    def requires(self):
        return TaskD(self.date)


class TaskH(luigi.Task):
    """
    任务H，依赖任务D E F
    """
    date = luigi.DateParameter()

    def run(self):
        for t in self.input():
            with t.open('r') as in_file:
                for line in in_file:
                    print("H reading dependencies: " + line)
        with self.output().open('w') as output:
            print(f"I\'m Task H! Working, priority={self.priority}")
            output.write("I\'m Task H! Working")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))

    def output(self):
        return luigi.LocalTarget('taskH.txt')

    def requires(self):
        return [TaskD(self.date), TaskE(self.date), TaskF(self.date)]


class TaskI(luigi.Task):
    """
    任务I，依赖任务G H
    """
    date = luigi.DateParameter()

    def run(self):
        for t in self.input():
            with t.open('r') as in_file:
                for line in in_file:
                    print("I reading dependencies: " + line)
        with self.output().open('w') as output:
            print(f"I\'m Task I! Working, priority={self.priority}")
            output.write("I\'m Task I! Working")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))
        # time.sleep(100)

    def output(self):
        return luigi.LocalTarget('taskI.txt')

    def requires(self):
        return [TaskG(self.date), TaskH(self.date)]




if __name__ == "__main__":
    delta = datetime.timedelta(days=3)
    time_arg = datetime.date.today() - delta
    # luigid命令启动调度后台和GUI
    # 也可以使用命令行构建任务，luigi --module core TaskI --date datetime.date.today()-datetime.timedelta(days=3) --local-scheduler
    luigi.build([TaskA(time_arg), TaskB(time_arg), TaskC(time_arg), TaskD(time_arg), TaskE(time_arg), TaskF(time_arg),
                 TaskG(time_arg), TaskH(time_arg), TaskI(time_arg)])
