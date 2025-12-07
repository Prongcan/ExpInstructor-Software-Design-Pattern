# 重构报告：引入并发型 Active Object 模式

## 1\. 模式定义 (Pattern Definition)

[cite_start]**Active Object（主动对象模式）** 是一种并发设计模式，其核心定义是：**将方法的“调用”（Invocation）与方法的“执行”（Execution）解耦** [cite: 66, 67]。

在传统的被动对象（Passive Object）中，方法的调用和执行发生在同一个线程中，调用者必须等待方法执行完毕才能继续（同步阻塞）。而在 Active Object 模式中：

  * **调用**发生在客户端线程，通过代理（Proxy）将请求封装成对象放入队列，立即返回一个 `Future`（未来结果的凭证）。
  * **执行**发生在独立的服务端线程（Worker Thread），调度器（Scheduler）从队列中取出请求并执行。

该模式主要包含六个组件：*Client（客户端）、Proxy（代理）、Scheduler（调度器）、Activation Queue（任务队列）、Servant（实际执行者）、Future（结果凭证）。*

## 2\. 重构动机与痛点 (Motivation & Problem Statement)

在重构前的 `ExpInstructor` 项目中，知识检索模块存在明显的\*\*同步阻塞（Synchronous Blocking）\*\*问题：

  * **现状：** Agent 在执行 `search_similar_node_and_edge` 工具时，直接通过 `requests.post` 调用外部 FastAPI 服务。
  * **代码位置：** 原 `ins_model.py` 或 Agent 工具定义处。
  * **问题：** 1.  **主线程阻塞：** 图数据库检索和 LLM 重排序是高耗时操作（代码中设置了 `timeout=3000` 秒）。在等待 HTTP 响应期间，整个 Agent 的主线程完全处于“假死”状态，无法处理心跳检测、用户中断或UI更新。
    2\.  **缺乏流量控制：** 如果 Agent 逻辑变得复杂（例如并行思考或多步推理），短时间内发起大量 HTTP 请求可能会瞬间压垮后端的检索服务，缺乏统一的排队和限流机制。

## 3\. 修改理念与实施 (Refactoring Philosophy & Implementation)

我们引入 `RetrievalActiveObject` 类来实现异步化改造。

### 3.1 核心理念：以“消息”代替“直接调用”

我们将原本直接的函数调用（Function Call）转化为消息传递（Message Passing）。Client 不再直接操作 HTTP 连接，而是向 Active Object 提交一个“检索任务书”。

### 3.2 角色映射 (Role Mapping)

我们在 `Evaluation_feasibility/retrieval_active_object.py` 中实现了以下结构：

| Active Object 角色 | 项目中的实现 | 职责说明 |
| :--- | :--- | :--- |
| **Proxy (代理)** | `RetrievalActiveObject.submit_task()` | 接收 Agent 的查询请求，封装成 Task 对象，**立即返回** `Future`，不阻塞主线程。 |
| **Activation Queue (队列)** | `self._queue (queue.Queue)` | 线程安全的缓冲区，存储待处理的检索请求，实现生产者-消费者模型。 |
| **Scheduler (调度器)** | `_run_loop()` | 运行在后台守护线程（Daemon Thread），不断从队列中取出请求。 |
| **Servant (执行者)** | `_execute_request()` | 包含原有的 `requests.post` 逻辑。它在后台线程中真正执行耗时的网络 I/O。 |
| **Future (凭证)** | `concurrent.futures.Future` | 连接主线程与后台线程的桥梁。主线程持有它，等待后台线程填入结果或异常。 |

### 3.3 代码对比 (Code Comparison)

**Before (Blocking I/O):**

```python
# 旧代码：主线程卡死
def search_tool(query):
    # 这一行执行时，整个程序暂停，直到服务器响应
    response = requests.post(URL, json={...}) 
    return response.json()
```

**After (Active Object Pattern):**

```python
# 新代码：调用与执行分离
def search_tool(query):
    # 1. Invocation: 瞬间完成，请求入队
    future = active_object.submit_task(query)
    
    # ... 在复杂的 Agent 中，这里可以执行其他并行逻辑 ...
    
    # 2. Future Wait: 显式等待结果，此时网络请求已在后台线程处理
    return future.result() 
```

## 4\. 收益总结 (Benefits)

1.  **响应性提升 (Improved Responsiveness)：** 即使后端检索服务响应缓慢，Agent 的主控制流在提交任务阶段也不会被阻塞。这为未来扩展“流式输出”或“并行工具调用”打下了基础。
2.  **资源管理与流控 (Resource Management)：** 通过 `Activation Queue`，我们隐式地实现了流量削峰。无论 Agent 发起请求的频率多高，后台的 HTTP 请求都会按照 Worker 线程的处理能力有序执行，避免了对外部 API 的 DDoS 攻击。
3.  **解耦 (Decoupling)：** 客户端（Agent）不再需要知道底层的 HTTP 连接细节（如超时重试、连接池管理），这些都被封装在 Active Object 内部，提高了代码的可维护性。

-----

### 💡 如何在 PPT 或报告中使用这段文字：

1.  **在 UML 类图中：** 画出一个包含 `Client`, `RetrievalActiveObject` (包含 `Queue` 和 `Thread`), 和 `Future` 的框图。
2.  **在序列图（Sequence Diagram）中：** 展示 `Client` 调用 `submit_task` -\> 获得 `Future` -\> (时间流逝) -\> `WorkerThread` 完成任务 -\> `Client` 调用 `future.result()` 获取数据。这能直观地展示“时间差”，体现并发特性。