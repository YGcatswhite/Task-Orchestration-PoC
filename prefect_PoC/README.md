# Prefect

![img](https://pic2.zhimg.com/80/v2-a7d3f09697e2ecabcbf19a70f1b972a5_1440w.jpg)

**对于流的定义和使用非常灵活**

Prefect独特的混合执行模型可以让代码和数据完全私密，同时可以充分利用弱冠的编排服务

当注册工作流的时候，代码会安全地存储在基础设施中。工作流元数据被发送到Prefect Cloud以进行调度和编排。Prefect Agent在用户的部署架构中运行，负责启动和监控工作流运行。Agent向Prefect Cloud API发送请求来更新工作流运行元数据。

Agent负责启动和监控工作流运行。Prefect 支持多种不同的代理类型，用于在不同平台上进行部署：

- 本地代理作为本地进程执行工作流
- Docker代理在Docker容器中执行工作流
- K8S代理将工作流作为K8S作业执行
- AES ECS：ECS代理将工作流运行作为AWS ECS任务执行

## Home

在Prefect 工作流中你可以使用本地代码，你可以选择要向编排的API中注册的工作流代码中的哪些单个元素；工作流可以包括在运行时确定执行路径的逻辑，使用本地狗仔和Prefect构造均可以；可以随时修改工作流，可以使用自定义运行时参数运行工作流和任务、随时更改计划、执行临时运行，甚至生成流运行以相应运行时条件或者流事件

### 基本编排

使用装饰函数，可以在失败时重试它们

可以通过更改流的task_runner，使用DaskTaskRunner，将自动提交以Dask.distributed集群上并行运行

可以进行异步并发：

## 入门

### 安装

```python
pip install -U "prefect>=2.0b"
pip install -U "prefect==2.0b8"
pip install git+https://github.com/PrefectHQ/prefect@orion
```

### 教程

和airflow很像，流是用装饰器装饰的Python函数@flow，任务是用装饰器装饰的函数@task

**在流中定义流，这个特点留意一下**

异步函数也可以和Prefect一起使用，其它框架中没有提供类似需求

#### 任务依赖

wait_for

#### 流程执行

可以有任务执行者，通过任务执行器的概念公开此功能，并行执行DaskTaskRunner（它`DaskTaskRunner`会自动创建一个本地 Dask 集群，然后立即开始并行执行所有任务。使用的工作人员数量取决于您机器上的内核数量），使用async和await就可以进行异步运行



## 概念

### Flow

流是唯一可以交互、显示和运行的Prefect抽象，流是工作流逻辑的容器，允许用户预期工作流状态进行交互与推断

流就像函数，可以接受输入、执行工作并返回输出

流有以下参数：

| 争论                  | 描述                                                         |
| :-------------------- | :----------------------------------------------------------- |
| `description`         | 流的可选字符串描述。如果未提供，将从装饰函数的文档字符串中提取描述。 |
| `name`                | 流的可选名称。如果未提供，则将从函数中推断名称。             |
| `retries`             | 在流运行失败时重试的可选次数。                               |
| `retry_delay_seconds` | 在失败后重试流之前等待的可选秒数。这仅适用于`retries`非零值。 |
| `task_runner`         | 用于在流中执行任务的[任务](https://orion-docs.prefect.io/concepts/task-runners/)运行器。如果未提供，`ConcurrentTaskRunner`将使用。 |
| `timeout_seconds`     | 可选的秒数，指示流的最大运行时间。如果流超过此运行时间，它将被标记为失败。流程执行可能会继续，直到调用下一个任务。 |
| `validate_parameters` | 指示传递给流的参数是否由 Pydantic 验证的布尔值。默认为`True`。 |
| `version`             | 流的可选版本字符串。如果未提供，我们将尝试创建一个版本字符串作为包含包装函数的文件的哈希。如果找不到文件，则版本将为空。 |

当在另一个流的执行中调用流函数时，将创建子流运行。主要流程是父流程，子流运行的行为类似于正常的流运行。在后端运行的流程有完整的表示，就好像它被单独调用一样。当子流启动时，它将创建一个新的任务运行器，并且子流中的任务将提交给它。子流完成后，任务运行器将关闭。

#### Task

如果任何一行代码失败，整个任务都会失败，必须从头开始重试。这可以通过将代码拆分为多个相关任务来避免。

| 争论                | 描述                                                         |
| :------------------ | :----------------------------------------------------------- |
| 姓名                | 任务的可选名称。如果未提供，则将从函数名称推断名称。         |
| 描述                | 任务的可选字符串描述。                                       |
| 标签                | 与此任务的运行相关联的一组可选标签。`prefect.tags`这些标签与任务运行时上下文定义的任何标签组合在一起。 |
| cache_key_fn        | 一个可选的可调用对象，给定任务运行上下文和调用参数，生成一个字符串键。如果密钥与先前的已完成状态匹配，则将恢复该状态结果，而不是再次运行任务。 |
| 缓存过期            | 一个可选的时间量，指示该任务的缓存状态应该可以恢复多长时间；如果未提供，缓存状态将永远不会过期。 |
| 重试                | 重试任务运行失败的可选次数。                                 |
| retry_delay_seconds | 失败后重试任务之前等待的可选秒数。这仅适用于`retries`非零值。 |
| 版本                | 一个可选字符串，指定此任务定义的版本。                       |

缓存是指任务运行反映完成状态而不实际运行定义任务的代码的能力。这使您可以有效地重用每次流运行时运行成本可能很高的任务的结果，或者如果任务的输入没有更改，则重用缓存的结果。

#### State

状态是包含有关特定任务运行或流运行状态信息的丰富对象。虽然不需要知道使用Prefect的状态的详细信息，但是可以利用它为工作流赋予能力

#### Flow Runner

流运行器负责为与部署相关的流运行创建和监控基础架构，流运行器只能与部署一起使用，当你通过自己调用流直接运行流时，需要对流执行的环境

流运行器特定于流将在其中运行的环境。Prefect 目前提供以下流运行器：

- [`UniversalFlowRunner`](https://orion-docs.prefect.io/api-ref/prefect/flow-runners/#prefect.flow_runners.UniversalFlowRunner)包含其他流运行器使用的配置选项。您不应直接使用此流运行器。
- [`SubprocessFlowRunner`](https://orion-docs.prefect.io/api-ref/prefect/flow-runners/#prefect.flow_runners.SubprocessFlowRunner)在本地子流程中运行流程。
- [`DockerFlowRunner`](https://orion-docs.prefect.io/api-ref/prefect/flow-runners/#prefect.flow_runners.DockerFlowRunner)在 Docker 容器中运行。
- [`KubernetesFlowRunner`](https://orion-docs.prefect.io/api-ref/prefect/flow-runners/#prefect.flow_runners.KubernetesFlowRunner)在 Kubernetes 作业中运行流程。

要使用流运行器，要把流运行器放到部署规范中（deployment specification）

#### Task Runner

Prefect 目前提供以下内置任务运行器：

- [`ConcurrentTaskRunner`](https://orion-docs.prefect.io/api-ref/prefect/task-runners/#prefect.task_runners.ConcurrentTaskRunner)并发运行任务，允许在 IO 阻塞时切换任务。同步任务将提交到由`anyio`.
- [`SequentialTaskRunner`](https://orion-docs.prefect.io/api-ref/prefect/task-runners/#prefect.task_runners.SequentialTaskRunner)按顺序运行任务。

prefect-dask是分布式并发？可以添加现有集群

#### 部署

API跟踪所有Prefect流程运行，API不需要实现注册流。使用Prefect可以在本地或者远程环境中调用流，并对其进行跟踪，部署能够让你计划流运行、告诉Prefect API在哪里可以找到流代码、包流代码和配置、为过滤工作队列和UI中的流运行分配标签、从API或UI创建临时流运行

要创建部署，需要：

1. 从将执行的工作流程的流程和任务代码开始
2. 如果在代码中定义部署，创建一个部署规范，其中包含用于基于该流代码创建部署的设置
3. 使用部署规范，通过API在Prefect数据库中创建部署对象
4. 在创建或更新部署的时候，流代码将持久保存到存储位置，API服务器的默认存储或部署规范中指定的存储位置

要运行部署需要：

1. Prefect通过工作队列和代理创建适当的流运行程序实例
2. 流运行器为流运行提供任何必要的执行环境
3. 刘云兴从存储中检索流代码
4. 流运行器从基础设施开启prefect.engine，它执行流程运行代码
5. Orion编排引擎监控流运行状态，在Prefect Cloud或Prefect API服务器中报告运行状态和日志消息

部署规范也可以用 YAML 编写，并引用流的位置而不是流对象

一个部署规范文件或流定义可以包括多个部署规范，每个部署规范代表一个流的不同部署的设置。给定流程的每个部署规范都必须有一个唯一的名称——Orion 不支持 flow_name/deployment_name 的重复实例。但是，您可以在单个部署文件中包含多个不同流的部署规范。

#### 存储

存储允许配置部署的流代码、任务结果和六节过的持久化方式，如果没有配置其它存储，Prefect使用默认的临时本地存储

本地存储适用于许多本地流程和任务运行场景，但是要是用Docker或K8S运行流，必须设置远程存储，比如S3、Google云存储或者Azure Blob存储

#### 块

块是Prefect的一个原语，可以存储配置并提供与外部系统交互的接口，使用块可以安全地存储凭证，来使用AWS、Github、Slack或你想与Prefect编排的任何其他系统等服务进行身份验证。块还公开了方法，这些方法提供了针对外部系统执行操作的预构建功能。块可用于从S3存储桶下载数据或将数据上传到S3存储桶，从数据库查询数据或将数据写入数据库，或者向Slack通道发送消息

块是Block基类的子类，可以像普通类一样被实例化和使用，例如要实例化一个存储JSON值的块，使用下面的JSON块：

```python
from prefect.blocks.system import JSON

json_block = JSON(value={"the_answer": 42})

# 如果稍后需要检索此 JSON 值以在流或任务中使用，我们可以使用.save()块上的方法将值存储在 Orion DB 中以供稍后检索：
json_block.save(name="life-the-universe-everything")
# 保存存储在 JSON 块中的值时给出的名称可用于稍后在流或任务运行期间检索值时：
from prefect import flow
from prefect.blocks.system import JSON

@flow
def what_is_the_answer():
    json_block = JSON.load("life-the-universe-everything")
    print(json_block.value["the_answer"])

what_is_the_answer() # 42
```

要创建自定义的块，定义一个包含子类的类Block。Block基类建立在Pydantic的基础上，因此可以用BaseModel自定义块：

```python
from prefect.blocks.core import Block

class Cube(Block):
    edge_length_inches: float

from prefect.blocks.core import Block

class Cube(Block):
    edge_length_inches: float

    def get_volume(self):
        return self.edge_length_inches**3

    def get_surface_area(self):
        return 6 * self.edge_length_inches**2
    
from prefect import flow

rubiks_cube = Cube(edge_length_inches=2.25)
rubiks_cube.save("rubiks-cube")

@flow
def calculate_cube_surface_area(cube_name):
    cube = Cube.load(cube_name)
    print(cube.get_surface_area())

calculate_cube_surface_area("rubiks-cube") # 30.375
```

#### 文件系统

文件系统是一个允许从路径读取和写入数据的对象。Prefect提供了两种内置的文件系统类型，覆盖了广泛的用例：

1. LocalFileSystem
2. RemoteFileSystem

#### 工作队列和代理

工作队列和代理将Prefect Orion服务器的编排环境与用户的执行环境连接起来。工作队列定义要完成的工作，代理轮询特定工作队列以获取新的工作，需要：

1. 在服务器上创建一个工作队列，工作队列为符合其过滤条件的部署收集计划运行
2. 在执行环境中运行代理，代理轮询特定工作队列以获取新工作，从服务器获取计划工作，并将其部署来执行

要运行协调部署，必须配置至少一个工作队列和代理

工作队列组织代理可以选择执行的工作，工作队列配置决定了将要进行哪些工作；工作队列包含来自与队列条件匹配的任何部署的计划运行，标准可以包括部署、标签、流。

这些标准可以随时修改，为特定队列请求工作的代理进程只会看到匹配的运行

#### 时间表

Prefect 支持多种类型的计划，涵盖广泛的用例并提供大量定制：

- [`CronSchedule`](https://orion-docs.prefect.io/concepts/schedules/#cronschedule)最适合已经熟悉`cron`在其他系统中使用的用户。
- [`IntervalSchedule`](https://orion-docs.prefect.io/concepts/schedules/#intervalschedule)最适合需要以与绝对时间无关的一致节奏运行的部署。
- [`RRuleSchedule`](https://orion-docs.prefect.io/concepts/schedules/#rruleschedule)最适合依赖日历逻辑进行简单重复计划、不定期间隔、排除或每月调整的部署。

创建时间表可以通过将schedule参数包括在部署的部署规范中创建计划，要导入要使用的计划类，然后schedule使用该类的实例设置参数；如果有更改计划，则会删除尚未开始的先前计划的流程运行，并创建新的计划流程运行来反映新计划；要删除流部署的所有计划运行，需要更新不带schedule参数的部署

##### 定时计划

CronSchedule根据提供cron字符串创建新的流程来运行

##### 间隔时间表

一个`IntervalSchedule`创建的新流以秒为单位定期运行。间隔是从可选的`anchor_date`