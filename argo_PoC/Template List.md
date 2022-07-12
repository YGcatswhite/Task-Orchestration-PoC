# Template List

| 多变的                     | 描述                               |
| :------------------------- | :--------------------------------- |
| `inputs.parameters.<NAME>` | 模板的输入参数                     |
| `inputs.parameters`        | 模板的所有输入参数作为 JSON 字符串 |
| `inputs.artifacts.<NAME>`  | 将工件输入到模板                   |

### 步骤模板

| 多变的                                       | 描述                                                         |
| :------------------------------------------- | :----------------------------------------------------------- |
| `steps.<STEPNAME>.id`                        | 容器步骤的唯一 ID                                            |
| `steps.<STEPNAME>.ip`                        | 前一个守护程序容器步骤的 IP 地址                             |
| `steps.<STEPNAME>.status`                    | 任何先前步骤的阶段状态                                       |
| `steps.<STEPNAME>.exitCode`                  | 任何先前脚本或容器步骤的退出代码                             |
| `steps.<STEPNAME>.startedAt`                 | 步骤开始时的时间戳                                           |
| `steps.<STEPNAME>.finishedAt`                | 步骤完成时的时间戳                                           |
| `steps.<STEPNAME>.outputs.result`            | 任何先前容器或脚本步骤的输出结果                             |
| `steps.<STEPNAME>.outputs.parameters`        | 当上一步使用`withItems`or`withParams`时，这包含每个调用的输出参数映射的 JSON 数组 |
| `steps.<STEPNAME>.outputs.parameters.<NAME>` | 任何先前步骤的输出参数。当上一步使用`withItems`or`withParams`时，这包含每个调用的输出参数值的 JSON 数组 |
| `steps.<STEPNAME>.outputs.artifacts.<NAME>`  | 任何先前步骤的输出工件                                       |

### DAY 模板

| 多变的                                       | 描述                                                         |
| :------------------------------------------- | :----------------------------------------------------------- |
| `tasks.<TASKNAME>.id`                        | 容器任务的唯一 ID                                            |
| `tasks.<TASKNAME>.ip`                        | 前一个守护程序容器任务的 IP 地址                             |
| `tasks.<TASKNAME>.status`                    | 任何先前任务的阶段状态                                       |
| `tasks.<TASKNAME>.exitCode`                  | 任何先前脚本或容器任务的退出代码                             |
| `tasks.<TASKNAME>.startedAt`                 | 任务开始的时间戳                                             |
| `tasks.<TASKNAME>.finishedAt`                | 任务完成的时间戳                                             |
| `tasks.<TASKNAME>.outputs.result`            | 任何先前容器或脚本任务的输出结果                             |
| `tasks.<TASKNAME>.outputs.parameters`        | 当上一个任务使用`withItems`or`withParams`时，它包含每个调用的输出参数映射的 JSON 数组 |
| `tasks.<TASKNAME>.outputs.parameters.<NAME>` | 任何先前任务的输出参数。当上一个任务使用`withItems`or`withParams`时，它包含每个调用的输出参数值的 JSON 数组 |
| `tasks.<TASKNAME>.outputs.artifacts.<NAME>`  | 任何先前任务的输出工件                                       |

### HTTP 模板

> 从 v3.3 开始

仅适用于`successCondition`

| 多变的                | 描述                              |
| :-------------------- | :-------------------------------- |
| `request.method`      | 请求方法 ( `string`)              |
| `request.url`         | 请求网址 ( `string`)              |
| `request.body`        | 请求正文 ( `string`)              |
| `request.headers`     | 请求标头 ( `map[string][]string`) |
| `response.statusCode` | 响应状态码 ( `int`)               |
| `response.body`       | 响应正文 ( `string`)              |
| `response.headers`    | 响应标头 ( `map[string][]string`) |

### `RetryStrategy`

使用 中的`expression`字段时`retryStrategy`，可以使用特殊变量。

| 多变的               | 描述                             |
| :------------------- | :------------------------------- |
| `lastRetry.exitCode` | 上次重试的退出码                 |
| `lastRetry.Status`   | 上次重试的状态                   |
| `lastRetry.Duration` | 上次重试的持续时间（以秒为单位） |

注意：这些变量评估为字符串类型。如果使用高级表达式，请将它们转换为 int 值 ( `expression: "{{=asInt(lastRetry.exitCode) >= 2}}"`) 或将它们与字符串值进行比较 ( `expression: "{{=lastRetry.exitCode != '2'}}"`)。

### 容器/脚本模板

| 多变的                           | 描述                                         |
| :------------------------------- | :------------------------------------------- |
| `pod.name`                       | 容器/脚本的 Pod 名称                         |
| `retries`                        | `retryStrategy`如果指定了容器/脚本的重试次数 |
| `inputs.artifacts.<NAME>.path`   | 输入工件的本地路径                           |
| `outputs.artifacts.<NAME>.path`  | 输出工件的本地路径                           |
| `outputs.parameters.<NAME>.path` | 输出参数的本地路径                           |

### 循环 ( `withItems`/ `withParam`)

| 多变的             | 描述                   |
| :----------------- | :--------------------- |
| `item`             | 列表中项目的值         |
| `item.<FIELDNAME>` | 地图列表中项目的字段值 |

### 指标

在 a 中发出自定义指标时`template`，可以使用特殊变量来允许对当前步骤进行自我引用。

| 多变的                           | 描述                                                         |
| :------------------------------- | :----------------------------------------------------------- |
| `status`                         | 度量发射模板的阶段状态                                       |
| `duration`                       | 指标发射模板的持续时间（以秒为单位）（仅适用于`Template`级别指标，供`Workflow`级别使用`workflow.duration`） |
| `exitCode`                       | 指标发射模板的退出代码                                       |
| `inputs.parameters.<NAME>`       | 度量发射模板的输入参数                                       |
| `outputs.parameters.<NAME>`      | 度量发射模板的输出参数                                       |
| `outputs.result`                 | 度量发射模板的输出结果                                       |
| `resourcesDuration.{cpu,memory}` | **以秒为单位的**资源持续时间。必须是`resourcesDuration.cpu`或之一`resourcesDuration.memory`（如果可用）。有关详细信息，请参阅[资源持续时间](https://argoproj.github.io/argo-workflows/resource-duration/)文档。 |

### 实时指标

一些变量可以实时发出（而不是仅在步骤/任务完成时发出）。要实时发出这些变量，请在`realtime: true`下面设置`gauge`（注意：只有 Gauge 指标允许实时变量发出）。当前可用于实时发射的指标：

对于`Workflow`级别指标：

- `workflow.duration`

对于`Template`级别指标：

- `duration`

### 全局

| 多变的                                      | 描述                                                         |
| :------------------------------------------ | :----------------------------------------------------------- |
| `workflow.name`                             | 工作流名称                                                   |
| `workflow.namespace`                        | 工作流命名空间                                               |
| `workflow.serviceAccountName`               | 工作流服务帐户名称                                           |
| `workflow.uid`                              | 工作流 UID。用于设置对资源或唯一工件位置的所有权引用         |
| `workflow.parameters.<NAME>`                | 工作流的输入参数                                             |
| `workflow.parameters`                       | 工作流的所有输入参数作为 JSON 字符串                         |
| `workflow.outputs.parameters.<NAME>`        | 工作流中的全局参数                                           |
| `workflow.outputs.artifacts.<NAME>`         | 工作流中的全局工件                                           |
| `workflow.annotations.<NAME>`               | 工作流注释                                                   |
| `workflow.labels.<NAME>`                    | 工作流标签                                                   |
| `workflow.creationTimestamp`                | RFC 3339 格式的工作流创建时间戳（例如`2018-08-23T05:42:49Z`） |
| `workflow.creationTimestamp.<STRFTIMECHAR>` | [`strftime`](http://strftime.org/)使用格式字符格式化的创建时间戳。 |
| `workflow.creationTimestamp.RFC3339`        | RFC 3339 格式的创建时间戳。                                  |
| `workflow.priority`                         | 工作流优先级                                                 |
| `workflow.duration`                         | 工作流程持续时间估计，可能与实际持续时间相差几秒钟           |
| `workflow.scheduledTime`                    | RFC 3339 格式的计划运行时（仅适用于`CronWorkflow`）          |

### 退出处理

| 多变的              | 描述                                                         |
| :------------------ | :----------------------------------------------------------- |
| `workflow.status`   | 工作流状态。之一：`Succeeded`, `Failed`,`Error`              |
| `workflow.failures` | JSON 对象列表，其中包含有关在执行期间失败或出错的节点的信息。可用字段：`displayName`、`message`、`templateName`、`phase`、`podName`和`finishedAt`。 |