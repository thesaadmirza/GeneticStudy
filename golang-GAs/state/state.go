package state

import (
  "math/big"
)

type State struct{
  operations *big.Int
}

func New() *State {
  var s *State = new(State)
  s.operations = big.NewInt(0)
  return s
}

func (self *State) NumOperations() big.Int {
  return *self.operations
}

func (self *State) IncOperations(n int64) {
  if n>0{
      self.operations.Add(self.operations,big.NewInt(n))
  }
}
