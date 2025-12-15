use "collections"

actor Main
  new create(env: Env) =>
    let buffer = Buffer(env)
    let consumer = Consumer(env)
    let producer = Producer
    producer.produce(buffer, consumer, 10)
    producer.produce(buffer, consumer, 20)
    producer.produce(buffer, consumer, 30)
    producer.produce(buffer, consumer, 40)

actor Buffer
  let _env: Env
  let _data: Array[U64] = Array[U64]
  
  new create(env: Env) =>
    _env = env
  
  be add(item: U64, consumer: Consumer tag) =>
    _data.push(item)
    _env.out.print("Buffer added: " + item.string())
    try
      let value = _data.shift()?
      consumer.receive(value)
    end

actor Producer
  be produce(buffer: Buffer tag, consumer: Consumer tag, item: U64) =>
    buffer.add(item, consumer)

actor Consumer
  let _env: Env
  
  new create(env: Env) =>
    _env = env
  
  be receive(item: U64) =>
    _env.out.print("Consumer received: " + item.string())