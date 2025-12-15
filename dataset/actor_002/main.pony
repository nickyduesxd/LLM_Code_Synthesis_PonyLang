actor Main
  new create(env: Env) =>
    let echo = EchoActor
    echo.echo("Hello, Pony!", {(msg: String val)(env) =>
      env.out.print("Echoed: " + msg)
    })
    echo.echo("Testing actor communication", {(msg: String val)(env) =>
      env.out.print("Received: " + msg)
    })
    echo.echo("Third message", {(msg: String val)(env) =>
      env.out.print("Got back: " + msg)
    })


actor EchoActor
  be echo(msg: String val, callback: {(String val)} val) =>
    callback(msg)