"""
Example 1: Basic Factorial Function
Category: Basic Syntax
Demonstrates: Recursion, primitive functions
"""
primitive Factorial
  fun apply(n: U64): U64 =>
    if n <= 1 then
      1
    else
      n * apply(n - 1)
    end

actor Main
  new create(env: Env) =>
    env.out.print("Factorial of 5: " + Factorial(5).string())
    // Output: 120

"""
Example 2: Immutable String Builder
Category: Reference Capabilities
Demonstrates: val capability, immutability
"""
class val StringBuffer
  let _data: String val
  
  new val create(s: String val = "") =>
    _data = s
  
  fun val append(s: String val): StringBuffer val =>
    StringBuffer(_data + s)
  
  fun val string(): String val =>
    _data

actor Main
  new create(env: Env) =>
    let buffer = StringBuffer("Hello")
    let buffer2 = buffer.append(" World")
    env.out.print(buffer2.string())
    // Output: Hello World

"""
Example 3: Counter Actor
Category: Actor Concurrency
Demonstrates: Actor, behaviors, message passing, callbacks
"""
actor Counter
  var _count: U64 = 0
  
  be increment() =>
    _count = _count + 1
  
  be get_value(callback: {(U64)} val) =>
    callback(_count)

actor Main
  new create(env: Env) =>
    let counter = Counter
    
    // Increment 5 times
    counter.increment()
    counter.increment()
    counter.increment()
    counter.increment()
    counter.increment()
    
    // Get the value
    counter.get_value(
      {(value: U64)(env) =>
        env.out.print("Count: " + value.string())
      } val
    )

"""
Example 4: Isolated Counter (Sendable)
Category: Reference Capabilities
Demonstrates: iso capability, safe sharing between actors
"""
class iso Counter
  var _count: U64
  
  new iso create() =>
    _count = 0
  
  fun ref increment() =>
    _count = _count + 1
  
  fun box get(): U64 =>
    _count

actor Worker
  be process(counter: Counter iso) =>
    counter.increment()
    // Can send counter to another actor since it's iso

actor Main
  new create(env: Env) =>
    let counter = recover iso Counter end
    env.out.print("Initial: " + counter.get().string())

"""
Example 5: Producer-Consumer Pattern
Category: Complex Systems
Demonstrates: Multiple actors, message passing, buffer
"""
actor Buffer
  let _data: Array[U64] = Array[U64]
  
  be add(item: U64) =>
    _data.push(item)
  
  be get(consumer: Consumer tag) =>
    try
      let item = _data.shift()?
      consumer.receive(item)
    end

actor Producer
  be produce(buffer: Buffer tag, item: U64) =>
    buffer.add(item)

actor Consumer
  let _env: Env
  
  new create(env: Env) =>
    _env = env
  
  be receive(item: U64) =>
    _env.out.print("Consumed: " + item.string())

actor Main
  new create(env: Env) =>
    let buffer = Buffer
    let producer = Producer
    let consumer = Consumer(env)
    
    // Produce items
    producer.produce(buffer, 10)
    producer.produce(buffer, 20)
    producer.produce(buffer, 30)
    
    // Consume items
    buffer.get(consumer)
    buffer.get(consumer)
    buffer.get(consumer)

"""
Example 6: Bank Account with Safe Transfers
Category: Complex Systems
Demonstrates: Actor state management, callbacks, transactions
"""
actor Account
  var _balance: U64
  let _id: String val
  
  new create(id: String val, initial_balance: U64) =>
    _id = id
    _balance = initial_balance
  
  be deposit(amount: U64) =>
    _balance = _balance + amount
  
  be withdraw(amount: U64, callback: {(Bool)} val) =>
    if _balance >= amount then
      _balance = _balance - amount
      callback(true)
    else
      callback(false)
    end
  
  be get_balance(callback: {(String val, U64)} val) =>
    callback(_id, _balance)
  
  be transfer(amount: U64, to: Account tag, callback: {(Bool)} val) =>
    if _balance >= amount then
      _balance = _balance - amount
      to.deposit(amount)
      callback(true)
    else
      callback(false)
    end

actor Main
  new create(env: Env) =>
    let alice = Account("Alice", 1000)
    let bob = Account("Bob", 500)
    
    // Transfer money
    alice.transfer(200, bob, 
      {(success: Bool)(env) =>
        if success then
          env.out.print("Transfer successful")
        else
          env.out.print("Transfer failed")
        end
      } val
    )
    
    // Check balances
    alice.get_balance(
      {(id: String val, balance: U64)(env) =>
        env.out.print(id + " balance: " + balance.string())
      } val
    )

"""
Example 7: Worker Pool Pattern
Category: Complex Systems
Demonstrates: Multiple actors, task distribution, round-robin
"""
actor Worker
  let _id: USize
  let _env: Env
  
  new create(id: USize, env: Env) =>
    _id = id
    _env = env
  
  be process(task: U64) =>
    // Simulate work
    _env.out.print("Worker " + _id.string() + " processing task " + task.string())
    let result = task * 2
    _env.out.print("Worker " + _id.string() + " result: " + result.string())

actor WorkerPool
  let _workers: Array[Worker] val
  var _next_worker: USize = 0
  
  new create(num_workers: USize, env: Env) =>
    let workers = recover iso Array[Worker] end
    for i in Range(0, num_workers) do
      workers.push(Worker(i, env))
    end
    _workers = consume workers
  
  be submit_task(task: U64) =>
    try
      _workers(_next_worker)?.process(task)
      _next_worker = (_next_worker + 1) % _workers.size()
    end

actor Main
  new create(env: Env) =>
    let pool = WorkerPool(3, env)
    
    // Submit tasks
    for i in Range[U64](0, 10) do
      pool.submit_task(i)
    end

"""
Example 8: Reference Capability Conversions
Category: Reference Capabilities
Demonstrates: recover blocks, capability transitions
"""
class ref MutableBox
  var _value: U64
  
  new ref create(value: U64) =>
    _value = value
  
  fun ref set(value: U64) =>
    _value = value
  
  fun box get(): U64 =>
    _value

actor Main
  new create(env: Env) =>
    // Create mutable box
    let box1 = MutableBox(10)
    
    // Convert to iso using recover
    let box2: MutableBox iso = recover iso
      let temp = MutableBox(20)
      temp
    end
    
    // Convert iso to val
    let box3: MutableBox val = consume box2
    
    env.out.print("Value: " + box3.get().string())
