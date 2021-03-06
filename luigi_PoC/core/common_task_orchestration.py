import luigi
import datetime
import time

'''
1、支持任务状态跟踪，8082对应有GUI
2、支持事件和回调，见注解部分
'''


class TaskA(luigi.Task):
    """
    独立的任务，看能否运行
    """
    date = luigi.DateParameter()

    def run(self):
        with self.output().open('w') as output:
            print("I\'m Task A! Lonely working")
            output.write("I\'m Task A! Lonely working")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))

    def output(self):
        return MemoryTarget()


class TaskB(luigi.Task):
    """
    任务B，初代父节点之一
    """
    date = luigi.DateParameter()

    def run(self):
        with self.output().open('w') as output:
            print("I\'m Task B! Working")
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

    def run(self):
        with self.output().open('w') as output:
            print("I\'m Task C! Working")
            output.write("I\'m Task C! Working")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))

    def output(self):
        return luigi.LocalTarget('taskC.txt')


class TaskD(luigi.Task):
    """
    任务D，依赖任务B
    """
    date = luigi.DateParameter()

    def run(self):
        with self.input().open('r') as in_file:
            for line in in_file:
                print("D reading dependencies: " + line)
        with self.output().open('w') as output:
            print("I\'m Task D! Working")
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

    def run(self):
        for t in self.input():
            with t.open('r') as in_file:
                for line in in_file:
                    print("E reading dependencies: " + line)
        with self.output().open('w') as output:
            print("I\'m Task E! Working")
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

    def run(self):
        with self.input().open('r') as in_file:
            for line in in_file:
                print("F reading dependencies: " + line)
        with self.output().open('w') as output:
            print("I\'m Task F! Working")
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
            print("I\'m Task G! Working")
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
            print("I\'m Task H! Working")
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
            print("I\'m Task I! Working")
            output.write("I\'m Task I! Working")
            print(self.date.strftime("%Y-%m-%d"))
            output.write(self.date.strftime("%Y-%m-%d"))
        # time.sleep(100)

    def output(self):
        return luigi.LocalTarget('taskI.txt')

    def requires(self):
        return [TaskG(self.date), TaskH(self.date)]


@TaskA.event_handler(luigi.Event.SUCCESS)
def task_success(task:TaskA):
    print("任务A成功了！")


if __name__ == "__main__":
    delta = datetime.timedelta(days=3)
    time_arg = datetime.date.today() - delta
    luigi.build([TaskA(time_arg), TaskB(time_arg), TaskC(time_arg), TaskD(time_arg), TaskE(time_arg), TaskF(time_arg),
                 TaskG(time_arg), TaskH(time_arg), TaskI(time_arg)])
