actor Main
  new create(env: Env) =>
    let result_0 = Counter.create().increment().get()
    let result_1 = Counter.create().increment().increment().get()
    env.out.print(result_0.string())
    env.out.print(result_1.string())

class Counter
  var _count: U64
  
  new iso create() =>
    _count = 0
  
  fun ref increment(): Counter ref =>
    _count = _count + 1
    this
  
  fun box get(): U64 =>
    _count