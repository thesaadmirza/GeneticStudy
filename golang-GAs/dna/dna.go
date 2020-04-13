package dna

import(
  "math/rand"
)

type DNA interface {
  Generate(prng *rand.Rand) DNA
  Mutate(prng *rand.Rand) DNA
  Crossover(ind2 DNA,prng *rand.Rand) DNA
  Evaluate() float64
  DeepCopy() DNA
  HasToMinimize() bool
}
