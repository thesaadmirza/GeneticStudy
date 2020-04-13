package state

import (
  "testing"
  "math/big"
)

func TestStateNew(t *testing.T){
  s := New()
  n := s.NumOperations()
  if big.NewInt(0).Cmp(&n)!=0{
    t.Errorf("NumOperations not initialized properly")
  }
}


func TestInc(t *testing.T){
  s := New()
  for i:=0;i<10;i++{
    s.IncOperations(1)
  }
  n := s.NumOperations()
  if big.NewInt(10).Cmp(&n)!=0{
    t.Errorf("operations not incremented properly")
  }
}
