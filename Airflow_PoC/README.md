# Airflow

它和luigi相同都是等幂的也就是任务结果是相同的，不会在，目标系统中创建重复的数据

注意，airflow不是流式数据的解决方案，常常用于处理实时数据批量处理数据流

有以下几点原则：

- 动态的：管道以代码形式进行配置，允许动态生成管道（和**luigi**的yield相同）
- 可扩展的：可以定义自己的操作符、执行程序并扩展库，使其适合环境的抽象级别
- 简明
- 可伸缩：具有模块化的体系结构，使用消息队列来协调任意数量的工作人员

由于这个项目过于庞大，我们直接进行PoC

## Airflow PoC

使用docker编排进行部署，建议是至少4G的内存

### Airflow API

使用@dag创建一个DAG，注意装饰的函数名会作为DAG的唯一标识符，它是任务之间具有依赖关系的任务的集合，在其中设置一些参数即可

使用@task装饰基于Python的函数创建任务，函数名是任务的唯一标识符，返回的值可以用于以后的任务

**注意：**调用本身会自动生成依赖项

多个dag可以重用修饰的任务，使用override修改task的id，然后用>>确定依赖关系还可以导入其它包的task在另一个dag文件中使用它

使用@task.docker来运行Python任务，如果在同一台计算机上创建一个单独的虚拟环境，可以使用@task,virtualenv

task可以使用dict类型来获得多个输出

可以在普通任务和经过修饰的任务之间添加依赖项

在修饰的任务和普通任务之间使用Xcoms，Xcoms是交叉通信，允许Tasks相互通信的机制，默认情况下Tasks是完全隔离的，并且可能运行在完全不同的机器上，它只适用于少量数据，不要传递大型值，其中包含一个key来对它进行标识

```python
# Pulls the return_value XCOM from "pushing_task"
value = task_instance.xcom_pull(task_ids='pushing_task')
# 此外还可以使用模板
SELECT * FROM {{ task_instance.xcom_pull(task_ids='foo', key='table_name') }}
```

可以自己本机配置、容器配置、K8S配置Xcoms后端

可以获取上下文变量

## GUIDE

### 向Dags中添加标记，并在UI中使用它进行过滤

在dag文件中可以传递添加到dag对象的标记列表

### 设置配置选项

第一次运行airflow会在工作目录下创建一个名为airflow.cfg的配置文件，此文件可以被编辑来更改任何设置。也可以通过AIRFLOW\__{SECTION}__{KEY}来创建一个环境变量，比如：

```shell
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=my_conn_string
```

### 设置数据库后端

可以考虑设置一个PostgreSQL、MySQL或者MSSQL的数据库后端，默认情况下Airflow使用的是SQLite，仅用于开发目的

Airflow本身是使用SQLAlchemy连接到数据库的，这需要配置数据库的URL，可以在[database]部分的选项sql_alchemy_conn设置；

### 使用Operators

一个operator表示单一的、理想的等幂任务，operator决定了dag实际执行的是什么

当我们谈论一个任务时，我们指的是DAG通用的执行单元；当我们谈论一个操作符时，指的是一个可重用的、预制的任务模板，它的逻辑是提前完成的，只需要提供一些参数

Jinja模板：使用{{}}在里面执行一系列操作

- BashOperator：使用这个在Bash Shell中执行命令，非零退出代码会产生Airflow异常，从而导致任务失败。如果希望任务结束时处于跳过状态，就可以使用exit 99退出
- BranchDateTimeOperator：使用这个将一个执行任务分到两个执行路径中，具体取决于执行日期或者时间是否在两个目标参数指定范围内，**对应luigi的某个东西**
- PythonOperator：使用它进行python的调用
- PythonVirtualenvOperator：使用它在新的python虚拟环境中执行Python调用
- ShortCircuitOperator：使用它可以控制满足条件或者获得真值时管道是否继续。这个条件和真值的计算是通过python_callable的输出完成的。如果返回真值，则允许管道继续运行，并将推送输出的XCom，如果输假值
- BranchDayOfWeekOperator：使用它可以根据工作日的值对工作流进行分流

### 交叉的DAG依赖关系

当两个DAG具有依赖关系时，值得将它们组合成一个DAG。但将所有相关的任务放在同一个DAG上有时是不合实际的，有几个原因，在这里不过多赘述

ExternalTaskSensor 可用于在不同的 DAG 之间建立这种依赖关系。当它与 ExternalTaskMarker 一起使用时，清除依赖任务也可以发生在不同的 DAG 之间。

#### ExternalTaskSensor

它使得DAG上的任务等待另一个DAG上的另一个任务以获得特定的执行日期。提供了一些选项来设置远程DAG上的Task是成功还是失败，通过allowed_states和failed_states实现

#### ExternalTaskMarker

使用它来让在每次parent_task` on `parent_dag被清除时，也应该清除指定的chiled

### 使用Timetables来定制DAG的调度

时间表必须是Timetable的子类，并应该注册为Airflow插件的一部分

在dag的参数配置中使用timetable参数即可设置所需的时间表

Airflow的调度程序遇到DAG需要调用两个方法来知道什么时候调度DAG的下一次运行：

- next_dagrun_info：调度程序使用这个函数了解时间表的常规日程安排，也就是说在实例中每个工作日都要有一个日程安排，在日程结束时运行
- infer_manual_data_interval：当DAG运行被手动触发时，调度程序使用这个函数来学习如何反向推断超出计划的运行时间间隔。该方法接受一个Datetime对象指示DAG何时被外部触发。

### 自定义UI

可以自定义状态颜色，需要`Create `airflow_local_settings.py` file and put in on `$PYTHONPATH` or to `$AIRFLOW_HOME/config` folder. (Airflow adds `$AIRFLOW_HOME/config` on `PYTHONPATH` when Airflow is initialized)`

可以自定义DAG用户界面标题和Airflow页面标题：在airflow.cfg文件里修改[webserver]部分

### 自定义Operator

可以通过继承BaseOperator来创建自定义的Operator，需要在子类中重写Constructor（定义Operator所需的参数，可以在dag文件中指定default_args）和Execute（当运行程序调用操作符时执行的代码，该方法包含Airflow上下文作为可用于读取配置值的参数）两个方法

如果自定义的Operator需要与外部服务进行通信，最好使用Hook实现通信，这种方式实现的逻辑可以被不同操作符中的其他用户重用。与对每个外部服务使用CustomServiceBaseOperator相比，这种方法提供了更好的解耦和对附加继承的利用；另一个考虑的因素是临时的状态，如果操作需要内存中的状态，那么该状态应该保留在操作符中而不是Hook中，这种方式服务Hook完全是无状态的，而且操作的整个逻辑都在Operator这一个地方里

Hook作为接口与DAG中的外部共享资源进行通信。不需要为每个任务创建连接，只需要从Hook中检索连接并利用它（我理解的是使用池化技术）

当操作符调用Hook对象的查询时，如果新连接不在就创建连接，Hook从Airflow后端检索用户名密码等认证参数，并将参数传递给hookbase

可以使用jinja模板化

可以自定义Sensor，Airflow为一种也输得操作符定义了一个原语，其目的是定期轮训某种状态，知道满足成功标准，可以扩展sensors.base重写poke方法来轮询你的外部状态并评估成功标准

### 创建自定义的@task装饰器

无

### 导出供Operator使用的动态环境变量

无

### 管理连接

connection对象用于存储连接到外部服务所需的凭据和其它信息，**连接可以通过环境变量、外部秘密后端、Airflow元数据库**存储

### 管理变量

变量是存储和检索任意内容或设置的一种通用方法，它作为简单的键值存储在Airflow中，可以从UI、代码或者CLI中列出、创建、更新和删除变量

可以在环境变量和元存储数据库中存储变量

### 使用反向代理运行Airflow

PS：正向代理是一个位于客户端和原始服务器之间的服务器，为了从原始服务器获得内容，客户端向代理发送了一个请求并且指定目标（原始服务器），然后代理向原始服务器转交请求并获得的内容返回给客户端，客户端才能使用正向代理；反向代理是充当web服务器网关的代理服务器，当你将请求发送到使用反向代理的web服务器时，它们将先转向反向代理，由该代理确定是将其路由到web服务器还是将其阻止

使用的反向代理有利端点设置的极大灵活性，具体配置可以文档

### 使用Systemd运行Airflow

Airflow可以与基于Systemd的系统集成，这样可以让监视守护进程变得容易，因为systemd可以在出现故障时重新启动守护进程

### 使用测试模式配置

Airflow有自己的一套测试模式配置选项，可以随时通过调用 airflow. configation.load _ test _ config ()来加载这些文件。请注意，此操作是不可逆的。

### 定义Operator额外链接

可以添加或重写指向现有Operator的链接

### 配置邮件

发送任务调度相关的邮件

### *动态的DAG生成

使用环境变量生成动态的DAG；用嵌入式元数据ALL_TASKS = ["task1", "task2", "task3"]；使用外部配置文件；使用 globals ()动态生成 DAG

## Airflow UI

### DAG视图

环境中有各种导入的DAG，为了过滤DAG可以在每个dag中添加标记

### 网格视图

横跨时间的条形图和DAG网格表示，上面是DAG运行时间的图表，下面是任务的实例

### 图表视图

### 日历视图

### 变量视图

允许您列出、创建、编辑或删除作业期间使用的变量的键值对。默认情况下，如果秘钥中包含任何单词(‘ password’、‘ secret’、‘ passwd’、‘ authority’、‘ api _ key’、‘ apikey’、‘ access _ token’)，变量的值将被隐藏，但可以配置为以明文显示

### 甘特图

允许您分析任务持续时间和重叠，可以快速识别瓶颈，以及大部分时间花费在哪些特定的DAG运行上

### 任务持续时间

过去N次运行中不同任务的持续时间

### 代码视图

可以透明地看到dag代码

## Concepts

### 架构描述

Airflow是一个平台，可以让您构建和运行工作流。工作流表示为DAG，并包含称为Tasks的各个工作不分，考虑了依赖关系和数据流。DAG指定任务之间的依赖关系，以及执行它们和运行重试的顺序，任务本身描述了要做什么，例如获取数据、运行分析、触发其他系统等

Airflow通常由：调度器（处理触发预定的工作流，并将任务提交给执行器运行）、执行器（处理正在运行的任务，在默认的Airflow赞庄重，这会在调度程序中运行所有内容，但大多数适合生产的执行程序实际上会将任务执行推送给worker）、网络服务器（提供了一个方便的用户界面来检查、触发和调试DAG和任务的行为）、DAG文件的文件夹（由调度程序和执行程序读取）、元数据库（由调度程序、执行程序和网络服务器用于存储状态）

![../_images/arch-diag-basic.png](http://apache-airflow-docs.s3-website.eu-central-1.amazonaws.com/docs/apache-airflow/latest/_images/arch-diag-basic.png)

大多数执行器可以引入某些其他组件来让他们和worker交流，比如消息队列

一个DAG包含一系列任务，其中有三种常见的任务类型（Operator、Sensor、Taskflow装饰的@task方法），这些实际上都是BaseOperator的子类

### DAGs

DAG是Airflow的核心概念，将Task收集在一起，用依赖关系和关系组织起来，说明它们应该如何运行

#### 声明DAG

- 使用上下文管理器，可以隐式地将DAG添加到其中的任何内容：

  ```python
  with DAG(
      "my_dag_name", start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
      schedule_interval="@daily", catchup=False
  ) as dag:
      op = EmptyOperator(task_id="task")
  ```

- 可以使用标准构造函数，将DAG传递给使用的任何operator

  ```python
  my_dag = DAG("my_dag_name", start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
               schedule_interval="@daily", catchup=False)
  op = EmptyOperator(task_id="task", dag=my_dag)
  ```

- 可以使用@dag装饰器将函数转换为DAG生成器

  ```python
  @dag(start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
       schedule_interval="@daily", catchup=False)
  def generate_dag():
      op = EmptyOperator(task_id="task")
  
  dag = generate_dag()
  ```

#### 任务依赖

Operator通常不会单独成为一个整体，它依赖于其它任务，而其它任务依赖于它。声明任务之间的这些依赖关系构成了DAG结构，有两种一个是使用<<和>>两个运算符，另一个是`set_upstream`和`set_downstream`方法

还可以使用cross_downstream实现相互依赖，也可以使用chain完车管依赖链

#### 加载DAG

Airflow从源文件中加载DAG，并在配置的DAG_FOLDER获取每个文件去执行它，但需要注意只会拉取最顶层的DAG实例对象

#### 运行DAG

当手动或者通过API或者通过API触发；或者在定义的时间表上，该时间表被定义为DAG的一部分

#### DAG任务

注意必须将每个Operator/Task分配给DAG才能运行，Airflow有很多计算DAG的方法无需显式传递：

- 如果在一个块中使用DAG声明Operator
- 如果在@dag装饰器中声明Operator
- 如果您将Operator置于具有DAG的Operator的上游或者下游

#### 默认参数

通常DAG的许多运算符需要相同的一组默认参数，可以在创建DAG时传递给DAG，不必为每个Operator单独指定默认参数，它会自动应用于关联的所有Operator

#### DAG装饰器

2.0版本之后有的

#### 控制流

- 可以使用分支来告诉DAG不要运行所有相关任务，而是选择一条或者多条路径向下运行。

#### DAG可视化

### 任务

任务是airflow中的基本执行单元

任务实例与每次运行时将DAG实例化为DAG Run的方式非常相似，任务实例的状态可能有：

- none：任务尚未排队等待执行（尚未满足其依赖关系）
- scheduled：调度程序已确定满足任务的依赖关系并且应该运行
- queued：任务已经分配给一个executor并且正在等待一个worker
- running：任务在worker上运行
- success：任务完成，没有错误
- shutdown：任务在运行时被外部请求关闭
- restarting：任务在运行时被外部请求重启
- failed：任务在执行过程中出错
- skipped：由于分支、LatestOnly或类似原因，任务被跳过
- upstream_failed：上有任务失败，触发规则说我们需要它
- up_for_retry：任务失败，但仍有重试尝试，将重新安排
- up_for_reschedule：任务是处于模式的传感器
- sensing：任务是智能传感器
- deferred：任务已推迟到触发器
- removed：自运行开始以来，任务已经从DAG中消失![../_images/task_lifecycle_diagram.png](http://apache-airflow-docs.s3-website.eu-central-1.amazonaws.com/docs/apache-airflow/latest/_images/task_lifecycle_diagram.png)

如果你希望任务具有最大运行时间，请将其`execution_timeout`属性设置`datetime.timedelta`为允许的最大运行时间

### 动态任务映射

动态任务映射允许工作流在运行时根据当前数据创建许多任务，而不是DAG作者需要事先知道有多少任务

比如for循环，调度程序可以根据先前任务的输出执行这个操作，也可以让任务对映射任务的收集输出进行操作

只允许将关键字参数传递给`expand()`.

一个映射任务的结果也可以用作下一个映射任务的输入。

`expand()`映射参数和未映射参数`partial()`

除了单个参数外，还可以传递多个参数进行扩展。这将产生创建“叉积”的效果，使用每个参数组合调用映射任务

### Sensor

Sensor是一种特殊类型的Operator。旨在等待某件事的发生，是基于时间的，等待一个文件或者等待一个外部事件，但它们所做的只是等到事情发生，然后成功，这样他们的下有任务就可以运行了，传感器有三种不同的运行模式：

- poke（默认的）Sensor在其整个运行时占用一个工作槽
- reschedule：传感器仅在检查时占用一个工作槽，并在检查之前休息一段设定的事件
- smart sensor：此传感器有一个集中式的版本，可以批量执行所有操作

### 可延迟的Operator和Trigger

这就是可延迟操作*符*的用武之地。可延迟操作符是这样一种操作符，当它知道它必须等待时，它能够暂停自身并释放工作者，并将恢复它的工作交给一个叫做*触发器*的东西。因此，当它被挂起（延迟）时，它不会占用一个工作槽，并且您的集群将在空闲的 Operator 或 Sensor 上浪费更少的资源。

Trigger是小的、异步的Python代码片段，旨在在单个Python进程中一起运行，因为它们是异步的，所以它们能够有效的共存

触发器从头开始设计为高度可用；如果您想运行高可用性设置，只需`triggerer`在多个主机上运行多个副本。很像`scheduler`，它们将自动与正确的锁定和 HA 共存。

[Kubernetes 执行器 — Airflow 文档 (apache-airflow-docs.s3-website.eu-central-1.amazonaws.com)](http://apache-airflow-docs.s3-website.eu-central-1.amazonaws.com/docs/apache-airflow/latest/executor/kubernetes.html)完美地契合公司当前框架

### 调度器

Airflow 调度程序监控所有任务和 DAG，然后在它们的依赖关系完成后触发任务实例。在幕后，调度程序启动一个子进程，该子进程监视并与指定 DAG 目录中的所有 DAG 保持同步。默认情况下，调度程序每分钟一次收集 DAG 解析结果并检查是否可以触发任何活动任务。

关于调度器性能[调度程序 — Airflow Documentation (apache-airflow-docs.s3-website.eu-central-1.amazonaws.com)](http://apache-airflow-docs.s3-website.eu-central-1.amazonaws.com/docs/apache-airflow/latest/concepts/scheduler.html)

### 注意业余优先权值

注意默认值是1不是0，有多种加权方法，上有的下游的和绝对的，**说实话这个地方要比luigi先进很多**

### Param

参数存储在模板上下文中，因此可以在模板中引用它们
