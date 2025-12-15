use "collections"

actor Main
  new create(env: Env) =>
    let pool = WorkerPool(3)
    pool.submit_task(5, {(result: U64)(env) =>
      env.out.print("Task result: " + result.string())
    })
    pool.submit_task(10, {(result: U64)(env) =>
      env.out.print("Task result: " + result.string())
    })
    pool.submit_task(7, {(result: U64)(env) =>
      env.out.print("Task result: " + result.string())
    })
    pool.submit_task(20, {(result: U64)(env) =>
      env.out.print("Task result: " + result.string())
    })

actor Worker
  be process(task: U64, callback: {(U64)} val) =>
    callback(task * 2)

actor WorkerPool
  let _workers: Array[Worker] val
  var _next_worker: USize = 0
  
  new create(num_workers: USize) =>
    let workers = recover iso Array[Worker] end
    for i in Range(0, num_workers) do
      workers.push(Worker)
    end
    _workers = consume workers
  
  be submit_task(task: U64, callback: {(U64)} val) =>
    try
      _workers(_next_worker)?.process(task, callback)
      _next_worker = (_next_worker + 1) % _workers.size()
    end
