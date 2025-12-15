actor Main
  new create(env: Env) =>
    let result_0 = apply([as U64: 1; 2; 3; 4; 5])
    let result_1 = apply([as U64:])
    let result_2 = apply([as U64: 100])
    env.out.print(result_0.string())
    env.out.print(result_1.string())
    env.out.print(result_2.string())

  fun apply(arr: Array[U64] val): U64 =>
    var sum: U64 = 0
    for value in arr.values() do
      sum = sum + value
    end
    sum