actor Main
  new create(env: Env) =>
    try
      let result_0 = ReadOnlyArray.create([as U64: 1; 2; 3]).apply(0)?
      let result_1 = ReadOnlyArray.create([as U64: 5; 10; 15]).size()
      env.out.print(result_0.string())
      env.out.print(result_1.string())
    end

class box ReadOnlyArray
  let _data: Array[U64] val
  
  new box create(data: Array[U64] val) =>
    _data = data
  
  fun box apply(i: USize): U64 ? =>
    _data(i)?
  
  fun box size(): USize =>
    _data.size()