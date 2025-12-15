actor Main
  new create(env: Env) =>
    let result_0 = StringBuffer.create("\"\"").append("Hello")
    let result_1 = StringBuffer.create("A").append("B").append("C")
    env.out.print(result_0.string())
    env.out.print(result_1.string())

  class val StringBuffer
    let _data: String val
    
    new val create(s: String val = "") =>
      _data = s
    
    fun val append(s: String val): StringBuffer val =>
      StringBuffer.create(_data + s)
    
    fun val string(): String val =>
      _data