package main

import(
  "math/rand"
  "io/ioutil"
  "encoding/json"
  . "example.com/D33pBlue/ProofOfEvolution/dna"
)

type Problem struct{
  TourSize int
  DistanceMatrix [][]float64
  OptDistance float64
}

var problem Problem

type TSP struct{
  Data []int
}

type definition string

func (s definition)Initialize(path string){
  dat, err := ioutil.ReadFile(path)
  if err != nil { panic(err) }
  err = json.Unmarshal([]byte(dat), &problem)
  if err != nil { panic(err) }
}

func build()*TSP{
  var tsp *TSP = new(TSP)
  for i:=0;i<problem.TourSize;i++{
    tsp.Data = append(tsp.Data,i)
  }
  return tsp
}

func (s definition)New()DNA{
  return build()
}

func (self *TSP)Generate(prng *rand.Rand) DNA{
  tsp := build()
  prng.Shuffle(len(tsp.Data),func(i,j int){tsp.Data[i],tsp.Data[j]=tsp.Data[j],tsp.Data[i]})
  return tsp
}

func (self *TSP)Mutate(prng *rand.Rand) DNA{
  i := prng.Intn(len(self.Data))
  j := prng.Intn(len(self.Data))
  for ;i==j && len(self.Data)>1;{
    j = prng.Intn(len(self.Data))
  }
  self.Data[i],self.Data[j] = self.Data[j],self.Data[i]
  return self
}

func (self *TSP)Crossover(ind2 DNA,prng *rand.Rand) DNA{
  var second *TSP = ind2.(*TSP)
  j := prng.Intn(len(self.Data))
  var rem []int
  for i:=0;i<len(self.Data);i++{
    n := self.Data[i]
    var used bool = false
    for k:=0;k<j && !used;k++{
      if second.Data[k]==n{
        used = true
      }
    }
    if !used{
      rem = append(rem,n)
    }
  }
  for i:=0;i<j;i++{
    self.Data[i] = second.Data[i]
  }
  for i:=0;i<len(rem);i++{
    self.Data[j+i] = rem[i]
  }
  return self
}

func (self *TSP)Evaluate() float64{
  var dist float64 = 0.0
  for i:=1;i<len(self.Data);i++{
    n1,n2 := self.Data[i-1],self.Data[i]
    dist += problem.DistanceMatrix[n1][n2]
  }
  dist += problem.DistanceMatrix[self.Data[len(self.Data)-1]][self.Data[0]]
  return dist
}

func (self *TSP)DeepCopy() DNA{
  k := build()
  for el := range self.Data{
    k.Data[el] = self.Data[el]
  }
  return k
}

func (self *TSP)HasToMinimize() bool{
  return true
}


var Definition definition
