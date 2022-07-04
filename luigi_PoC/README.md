## Luigi

[Tasks — Luigi 2.8.13 documentation](https://luigi.readthedocs.io/en/latest/tasks.html)

好处：

- 在典型的部署场景中，上面的 Luigi 编排定义以及 Pypark 处理代码将被打包到部署包中，例如容器映像。处理代码不必用 Python 实现，任何程序都可以打包到映像中并从 Luigi 运行。
- 可以设置依赖来确定任务顺序
- --local-scheduler标志告诉luigi要不要连接到中央调度器，这样做是为了开始和为了开发的目的，当开始将东西投入生产时，建议运行中央调度程序服务器。除了提供锁以便同一任务不会同事由多个进程运行以外，还提供了当前工作流非常好的可视化

构建工作流（两个基本模块Task和Target，都是抽象类，Parameter用于控制如何运行Task）：

- Target： Target类对应于一个文件或者某些检查点（数据库的一些条目）。Target唯一需要实现的方法是exists方法，当且仅当Target存在时才返回True；luigi有提供的支持各种文件系统的工具箱；这些target的大多数都是类似文件系统的，localTarget等会映射到本地驱动的文件，还包装了底层操作，使其成为原子操作。都实现了open方法
- Task：主要用于完成计算。实现一些方法来改变它的行为，最明显的就是run、output、requires；Task会消耗其它Task创建的Target，它们通常也输出Target；需要使用requires方法定义Task之间的依赖关系每个任务使用output方法定义输出。此外还有一个input方法为每个Task依赖项返回相应的Target类
- Parameter：对于某种类型的正在运行的作业，希望允许某种形式的参数化，比如每晚运行一个Hadoop就需要将日期作为类的参数
- 使用task、target、parameter表达任意依赖关系，不需要使用笨拙的DSL配置

### Task

一个Task可以是这样的：

![Task breakdown](https://luigi.readthedocs.io/en/latest/_images/task_breakdown.png)

- requires方法：指定对其它Task对象的依赖项，这些对象甚至可能属于同一个类，返回值可以是同一个类，也可以是包装在字典、列表、元组里的其它任务；requires方法不能返回Target对象，有一个简单的Target可以在output里被返回
- output方法：返回一个或者多个Target对象，可以以任何方便的方式把它们包装起来返回，建议只返回一个Target，如果返回多个原子性将会丢失，除非Task本身可以确保每个Target都是自动创建的
- Run方法：在使用requires和run时，luigi将所有内容分为两个阶段。首先它计算出任务之间所有的依赖关系，然后运行所有内容，input用requires里的output替换；这里需要注意：如果要写入二进制文件，luigi会根据院子读写方式自动去掉b标志，为了编写二进制文件，应该在调用localtarget时使用format=nop
- input方法：就是requires的一个包装器，返回相应的Target对象，而不是Task对象
- 动态依赖：可以提供动态依赖机制，需要在run方法中生成另一个task，当前的task会被挂起，并运行另一个任务，还可以生成任务列表。有一定的限制，每次产生一个新任务，task的run放啊会从台开始恢复，你需要保证你的run方法是等幂的
- 任务状态跟踪：对于长时间运行或者远程任务，可以在命令行或者日志中查看状态信息，还可以在中央调度冲虚中查看状态信息，luigi实现了动态状态消息、进度条和可能指向外部监控系统的跟踪URL，使用run的回调set_tracking_url来设置这个信息
- 事件和回调：有一个内置的事件系统，允许你注册对事件的回调，从自己的任务中触发它们。可以连接到一些预定义的事件并创建自己的事件。每个事件句柄都绑定到一个Task类中，并且只能从该类或者子类中触发，允许你毫不费力地订阅来自特定类的事件
- 可以有任务优先级：调度程序从满足所有依赖项的所有任务集合中决定下一个运行哪个任务。默认情况下，这种选择十分随意，对于大多数工作流和情况都很好；可以使用priority属性对优先级进行控制，luigi中依赖关系优先
- 命名空间：为了避免名称冲突，并能够拥有任务的标识符，id只存在于实例级别上
- 会有实例缓存

### Parameter

参数相当于为每个Task创建一个构造函数

- 可以使用命令解析器
- 实例缓存：任务是由类名和参数值唯一标识的
- 不重要的参数：使用无关紧要的参数创建的任务具有相同签名但是是不同的实例
- 参数可见性：可以使用ParameterVisibility配置参数可见性
- 参数类型：DateParameter，DateIntervalParameter，Intparameter，FloatParameter，由于pythom不是静态语言，可以简单使用Parameter父类，使用诸如 DateParameter 之类的子类的原因是 Luigi 需要知道它的类型以进行命令行交互。这就是为什么它知道如何将命令行中提供的字符串转换为相应的类型(即 datetime.date 而不是字符串)。
- 参数解析顺序：按照以下顺序解析：首先是传递给构造函数的任何值，或命令号上设置的任务级别值——然后是命令行上设置的任何值——任何配置选项——提供给参数的任何默认值

### 运行中的Luigi

运行的首要方法是使用命令行

另一种方法是使用luigi.interface模块中的luigi.build方法

### 使用luigi的中央调度器

集中式调度器有两个用途：确保同一任务的两个实例不同时运行和提供所有正在发生的事情可视化

在luigi.cfg中指定record_task_history = True来查看任务历史记录

### 执行模型

- worker和task执行：最重要的方面是没有执行转移，在运行luigi工作流时，工作人员安排所有任务，执行流程中的任务；这个方案的好处是调试容易，因为所有的执行都发生在过程中。它让部署成为非事件。在开发期间，我们通常从命令行运行luigi工作流，在部署时，可以使用crontab或者任何其它调度程序触发它；缺点是不能随意可伸缩，luigi的调度程序让同一作业不会由多个worker同时执行
- Schedule：一个客户端只有在单线程中央调度程序允许的情况下才启动任务的run方法
- Trigger：luigi不包括自己的触发器，必须依赖于外部调度器来实际触发工作流（crontab）

### Luigi的模式

- 代码重用：luigi的优点是它非常容易依赖于其它仓库中定义的任务，在执行路径中使用分叉也很简单，其中一个任务的输出可能是多个其它任务的输入，目前是不支持中间输出的语义的，这意味着所有输出都会无限期持久化，缺点是有很多中间结果，一种解决方案是把这些中间文件放在一个特殊目录里，并是用某种特定的垃圾收集来清理它们
- 触发很多任务：可以在多个依赖链末尾添加虚拟Task，这个简单的Task不做任何事情，但会调用一堆其它任务，每次调用时，luigi将执行尽可能多的挂起作业，需要使用WrapperTask来代替通常的Task，因为这个任务本身不会产生任何输出，因此需要一种方法来指示它何时完成
- 触发重复性任务：需要在requires方法中添加一个循环，来产生与self.date之前几天的依赖关系，可以使用RangeDailyBase
- 高效的触发重复性任务：使用RangeDaily
- 回填任务：希望在一个时间间隔内对其重新计算
- 具有范围的传播参数
- 将多个参数值批处理为单个运行：将多个作业作为一个批处理一起运行比单独运行快，在这种情况下可以在其构造函数中使用batch_method标记某些参数，告诉工作者如何组合多个值。一种常用的方法是简单地运行最大值。这对于在运行较新数据时覆盖较旧数据的任务非常有用，可以通过将batch_method设置为max来实现；限制批处理的大小只需要设置max_batch_size
- 定期覆盖相同数据源的任务
- 避免对单个文件进行并发写入
- 减少运行任务的资源：在调度时，luigi调度程序需要知道任务运行后可能具有的最大资源消耗，在run方法中减少小号的资源量是有益的，在这种情况下已经可以调度等待该特定资源的不同任务
- 监视任务管道：提供了通知，可以使用事件来设置延迟监视
- 原子写问题
- 向任务发送消息：中央调度程序可以将消息发送到特定的任务。当正在运行的任务接收消息时，它可以访问多处理。存储传入消息的队列对象

### API

#### luigi.Task

是所有luigi任务的基本类，是luigi的基本工作单元，包含必须在子类中实现的方法有run、requires、output

其中在Register元类中有一些属性：priority、disabled、resources=[]（任务使用的资源）、worker_timeout（默认值为None，run函数超时的最大秒数）、max_batch_size（作为批处理一起运行的最大任务数）、batchable（如果此实例可以作为批处理的一部分运行为true，默认情况下如果有任何批处理参数就是true）、retry_count、disable_hard_timeout、disable_window_seconds、owner_email（重写此命令可以向任务所有者发送其他错误邮件）、方法event_handler（用于添加事件处理程序的装饰器）、trigger_event（触发器，该触发器调用与此类关联的所有指定事件）、accepts_messages（用于配置可以接收哪些计划程序消息，如果为false则此任务不接受任何消息，如果为true就接受所有消息）、task_module（返回导入哪个Python模块来获得此类的访问权限）、task_namespace

......

### 设计和局限性

见文档[Design and limitations — Luigi 2.8.13 documentation](https://luigi.readthedocs.io/en/latest/design_and_limitations.html)