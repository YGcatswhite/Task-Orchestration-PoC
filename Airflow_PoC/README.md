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
