package main

import (
  "fmt"
  "math/rand"
  "example.com/D33pBlue/ProofOfEvolution/ga"
  "example.com/D33pBlue/ProofOfEvolution/knapsack"
)

func main(){
  rand.Seed(42)
  fmt.Println("proof of evolution")
  knap := knapsack.New()
  if knap.HasToMinimize(){
    ga.Optimum = ga.Minimize
  }else{
    ga.Optimum = ga.Maximize
  }
  ga.Epochs = 10
  pop,best := ga.RunGA(knap,true)
  fmt.Println(len(pop))
  fmt.Println(best.Individual)
  fmt.Println(best.Fitness)
}
