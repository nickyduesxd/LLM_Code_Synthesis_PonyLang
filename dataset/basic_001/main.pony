actor Main
  new create(env: Env) =>
    let result_0 = apply(0)
    let result_1 = apply(1)
    let result_5 = apply(5)
    let result_10 = apply(10)
    env.out.print(result_0.string())
    env.out.print(result_1.string())
    env.out.print(result_5.string())
    env.out.print(result_10.string())
  
  fun apply(n: U64): U64 =>
    if n <= 1 then 
        1    
    else 
        n * apply(n - 1)
    end