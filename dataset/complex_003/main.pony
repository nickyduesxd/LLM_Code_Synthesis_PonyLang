actor Main
  new create(env: Env) =>
    let num_nodes: USize = 5
    let coordinator = Coordinator(num_nodes, env)
    let node1 = CounterNode
    let node2 = CounterNode
    let node3 = CounterNode
    let node4 = CounterNode
    let node5 = CounterNode
    node1.increment()
    node1.increment()
    node1.increment()  // 3
    node2.increment()
    node2.increment()
    node2.increment()
    node2.increment()
    node2.increment()  // 5
    node3.increment()
    node3.increment()  // 2
    node4.increment()
    node4.increment()
    node4.increment()
    node4.increment()  // 4
    node5.increment()  // 1
    node1.get_count(coordinator)
    node2.get_count(coordinator)
    node3.get_count(coordinator)
    node4.get_count(coordinator)
    node5.get_count(coordinator)
    coordinator.get_total({(total: U64)(env) =>
      env.out.print("Total count from all nodes: " + total.string())
    })

actor CounterNode
  var _count: U64 = 0
  
  be increment() =>
    _count = _count + 1
  
  be get_count(coordinator: Coordinator tag) =>
    coordinator.receive_count(_count)

actor Coordinator
  let _env: Env
  var _total: U64 = 0
  var _responses: USize = 0
  let _expected: USize
  
  new create(expected_nodes: USize, env: Env) =>
    _expected = expected_nodes
    _env = env
  
  be receive_count(count: U64) =>
    _total = _total + count
    _responses = _responses + 1
    _env.out.print("Received count: " + count.string() + " (Response " + _responses.string() + "/" + _expected.string() + ")")
  
  be get_total(callback: {(U64)} val) =>
    if _responses == _expected then
      callback(_total)
    else
      _env.out.print("Waiting for all responses (" + _responses.string() + "/" + _expected.string() + ")")
    end
