import luigi

class TaskA(luigi.Task):
    """
    独立的任务，看能否运行
    """
    date=luigi.DateParameter()

    def run(self):
        with self.output().open('w') as output:
            output.write("I\'m Task A! Lonely working")

    def output(self):
        return luigi.LocalTarget('taskA.txt')