actor Main
  new create(env: Env) =>
    let result_0 = apply(0)
    let result_1 = apply(1)
    let result_5 = apply(10)
    let result_15 = apply(15)
    env.out.print(result_0.string())
    env.out.print(result_1.string())
    env.out.print(result_5.string())
    env.out.print(result_15.string())

  fun apply(n: U64): U64 =>
    if n <= 1 then
      n    
    else      
      var a: U64 = 0
      var b: U64 = 1
      var i: U64 = 2
      while i <= n do
        let temp = a + b       
        a = b     
        b = temp       
        i = i + 1      
        end      
      b    
    end