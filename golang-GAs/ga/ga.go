package ga

import (
  "sort"
  "fmt"
  "math/rand"
  . "example.com/D33pBlue/ProofOfEvolution/dna"
)

type Config struct{
  Miner int64
  Gen int
  Step int
  NPop int
  Pcross float64
  Pmut float64
  Mu int
  Lambda int
  Verbose int
}

func DefConf(x int64,gen,step int)*Config{
  conf := new(Config)
  conf.Miner = x
  conf.Gen = gen
  conf.Step = step
  conf.NPop = 600
  conf.Pcross = 0.7
  conf.Pmut = 0.3
  conf.Mu = 200
  conf.Lambda = 300
  conf.Verbose = 1
  return conf
}

func RandConf(x int64,gen,step int)*Config{
  var prng *rand.Rand = rand.New(rand.NewSource(99))
  prng.Seed(x)
  conf := new(Config)
  conf.Miner = x
  conf.Gen = gen
  conf.Step = step
  conf.NPop = prng.Intn(600)+100
  conf.Pcross = prng.Float64()+0.0001
  conf.Pmut = prng.Float64()+0.0001
  conf.Mu = prng.Intn(350)+50
  conf.Lambda = prng.Intn(350)+50
  conf.Verbose = 1
  return conf
}

type Sol struct{
  Individual DNA
  Fitness float64
  IsEval bool
  Conf Config
  Gen int
}

func (self Sol)DeepCopy()Sol {
  sol := new(Sol)
  sol.Individual = self.Individual.DeepCopy()
  sol.Fitness = self.Fitness
  sol.IsEval = self.IsEval
  sol.Conf = self.Conf
  sol.Gen = self.Gen
  return *sol
}

func (self *Sol)eval(){
  self.Fitness = self.Individual.Evaluate()
  self.IsEval = true
}

type Comp func(float64,float64)bool
func Maximize(s1,s2 float64) bool{
  return s1 > s2
}
func Minimize(s1,s2 float64) bool{
  return s1 < s2
}

var Optimum Comp = Minimize

type Population []Sol

func (a Population) Len() int { return len(a) }
func (a Population) Swap(i, j int){ a[i], a[j] = a[j], a[i] }
func (a Population) Less(i, j int) bool {
  if !a[i].IsEval{
    a[i].eval()
  }
  if !a[j].IsEval{
    a[j].eval()
  }
  return Optimum(a[i].Fitness,a[j].Fitness)
}

func (pop Population)eval() Sol  {
  best := pop[0]
  for i:=0;i<pop.Len();i++{
    pop[i].eval()
    if Optimum(pop[i].Fitness,best.Fitness){
      best = pop[i]
    }
  }
  return best
}

func (self Population)reset(){
  for i:=0; i<self.Len(); i++{
    self[i].IsEval = false
  }
}

func (self Population)DeepCopy()(pop Population){
  for i:=0;i<len(self);i++{
    pop = append(pop,self[i].DeepCopy())
  }
  return
}

func generatePopulation(n int,dna DNA,prng *rand.Rand) (pop Population){
  for i:=0; i<n; i++{
    sol := new(Sol)
    sol.Individual = dna.Generate(prng)
    sol.Fitness = 9999999999999
    sol.IsEval = false
    sol.eval()
    pop = append(pop,*sol)
  }
  return
}

func selectStd(pop Population,n int) (selected Population) {
  if len(pop)<=n{
    return pop
  }
  sort.Sort(pop)
  for i:=0; i<n-1; i++ {
    selected = append(selected,pop[i])
  }
  return
}

func offspring(pop Population,n int,pcross,pmut float64,prng *rand.Rand)(off Population){
  off = append(off,pop[0])
  for i:=0;i<n;i++{
    j := prng.Intn(len(pop))
    var ind Sol = *new(Sol)
    ind.Individual = pop[j].Individual.DeepCopy()
    ind.IsEval = false
    if prng.Float64()<pcross{
      ind2 := pop[prng.Intn(len(pop))]
      ind.Individual = ind.Individual.Crossover(ind2.Individual,prng)
      ind.IsEval = false
    }
    if prng.Float64()<pmut{
      ind.Individual = ind.Individual.Mutate(prng)
      ind.IsEval = false
    }
    off = append(off,ind)
  }
  return
}

type Packet struct{
  Solution Sol
  End bool
  Shared Population
}

func RunGA(dna DNA,conf *Config,chOut,chIn chan Packet){// (Population,Sol) {
  if dna.HasToMinimize(){Optimum = Minimize
  }else{Optimum = Maximize}
  var prng *rand.Rand = rand.New(rand.NewSource(99))
  prng.Seed(conf.Miner)
  var population Population = generatePopulation(conf.NPop,dna,prng)
  var bestOfAll Sol = population[0]
  bestOfAll.eval()
  for epoch:=0; epoch<conf.Gen; epoch++{
    population.reset()
    population = selectStd(population,conf.Mu)
    population = offspring(population,conf.Lambda,conf.Pcross,conf.Pmut,prng)
    best := population.eval()
    if Optimum(best.Fitness,bestOfAll.Fitness){
      bestOfAll = best
    }
    if conf.Verbose==2 {
      fmt.Printf("[%d]gen %d best fit: %f\n",conf.Miner,epoch,best.Fitness)
    }
    if epoch%conf.Step==0{
      if conf.Verbose==1{
        fmt.Printf("[%d,%d,%f]",conf.Miner,epoch,bestOfAll.Fitness)
      }
      bestOfAll.Conf = *conf
      bestOfAll.Gen = epoch
      pk := new(Packet)
      pk.Solution = bestOfAll
      pk.End = false
      chOut <- *pk
      pk2 := <- chIn
      for ii:=0;ii<len(pk2.Shared);ii++{
        ss := pk2.Shared[ii]
        ss.Conf = *conf
        population = append(population,ss)
      }
    }
  }
  // sort.Sort(population)
  bestOfAll.Conf = *conf
  bestOfAll.Gen = conf.Gen
  pk := new(Packet)
  pk.Solution = bestOfAll
  pk.End = true
  chOut <- *pk
  // return population,bestOfAll
}
