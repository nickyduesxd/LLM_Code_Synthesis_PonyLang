actor Main
  new create(env: Env) =>
    let counter = CounterActor
    counter.increment(5)
    counter.increment(10)
    counter.increment(3)
    counter.get_value({(value: U64)(env) =>
      env.out.print("Counter value: " + value.string())
    })

actor CounterActor
  var _count: U64 = 0
  
  be increment(amount: U64) =>
    _count = _count + amount
  
  be get_value(callback: {(U64)} val) =>
    callback(_count)