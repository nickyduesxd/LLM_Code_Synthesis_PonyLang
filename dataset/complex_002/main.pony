actor Main
  new create(env: Env) =>
    let coordinator = TestCoordinator(env)
    coordinator.run()

actor TestCoordinator
  let _env: Env
  
  new create(env: Env) =>
    _env = env
  
  be run() =>
    test1()
  
  be test1() =>
    _env.out.print("Test 1: Deposit increases balance")
    let account = Account("Alice", 1000)
    account.get_balance({(balance: U64)(env = _env, self: TestCoordinator tag = this) =>
      env.out.print("Alice's initial balance: " + balance.string())
      account.deposit(500)
      account.get_balance({(balance2: U64)(env, self) =>
        env.out.print("Alice's balance after deposit of 500: " + balance2.string())
        self.test2()
      })
    })
  
  be test2() =>
    _env.out.print("\nTest 2: Withdraw decreases balance if sufficient funds")
    let account = Account("Bob", 800)
    account.get_balance({(balance: U64)(env = _env, self: TestCoordinator tag = this) =>
      env.out.print("Bob's initial balance: " + balance.string())
      account.withdraw(300, {(success: Bool)(env, self, account) =>
        if success then
          env.out.print("Withdrawal of 300 successful")
        else
          env.out.print("Withdrawal failed")
        end
        account.get_balance({(balance2: U64)(env, self, account) =>
          env.out.print("Bob's balance after withdrawal: " + balance2.string())
          account.withdraw(1000, {(success2: Bool)(env, self, account) =>
            if success2 then
              env.out.print("Withdrawal of 1000 successful")
            else
              env.out.print("Withdrawal of 1000 failed - insufficient funds")
            end
            account.get_balance({(balance3: U64)(env, self) =>
              env.out.print("Bob's balance after failed withdrawal: " + balance3.string())
              self.test3()
            })
          })
        })
      })
    })
  
  be test3() =>
    _env.out.print("\nTest 3: Transfer moves money safely between accounts")
    let charlie = Account("Charlie", 1000)
    let diana = Account("Diana", 500)
    
    charlie.get_balance({(balance1: U64)(env = _env, self: TestCoordinator tag = this, charlie, diana) =>
      env.out.print("Charlie's initial balance: " + balance1.string())
      diana.get_balance({(balance2: U64)(env, self, charlie, diana) =>
        env.out.print("Diana's initial balance: " + balance2.string())
        charlie.transfer(400, diana, {(success: Bool)(env, self, charlie, diana) =>
          if success then
            env.out.print("Transfer of 400 from Charlie to Diana successful")
          else
            env.out.print("Transfer failed")
          end
          charlie.get_balance({(balance3: U64)(env, charlie, diana) =>
            env.out.print("Charlie's balance after transfer: " + balance3.string())
            diana.get_balance({(balance4: U64)(env, charlie, diana) =>
              env.out.print("Diana's balance after transfer: " + balance4.string())
              charlie.transfer(1000, diana, {(success2: Bool)(env) =>
                if success2 then
                  env.out.print("Transfer of 1000 successful")
                else
                  env.out.print("Transfer of 1000 failed - insufficient funds")
                end
              })
            })
          })
        })
      })
    })

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
  
  be get_balance(callback: {(U64)} val) =>
    callback(_balance)
  
  be transfer(amount: U64, to: Account tag, callback: {(Bool)} val) =>
    if _balance >= amount then
      _balance = _balance - amount
      to.deposit(amount)
      callback(true)
    else
      callback(false)
    end