package main

import (
  "os"
  "fmt"
  "sort"
  "plugin"
  "io/ioutil"
  "encoding/json"
  . "example.com/D33pBlue/ProofOfEvolution/dna"
  "example.com/D33pBlue/ProofOfEvolution/ga"
)


type Problem interface {
	Initialize(path string)
  New()DNA
}

func startMiner(problDna DNA,x int64,chOut,chIn chan ga.Packet){
  ga.RunGA(problDna,ga.RandConf(x,500,50),chOut,chIn)
}

func execGAOnMiners(problDna DNA,miners int64,coop bool,outFile string){
  chOut := make(chan ga.Packet)
  address := make(map[int64]chan ga.Packet)
  var i int64
  for i=0;i<miners;i++{
    chIn := make(chan ga.Packet)
    address[i] = chIn
    go startMiner(problDna,i,chOut,chIn)
  }
  var best ga.Population
  var toShare ga.Population
  i = miners
  for ;i>0;{
    pk := <-chOut
    best = append(best,pk.Solution)
    if coop{
      toShare = append(toShare,pk.Solution)
    }
    if pk.End {
      fmt.Printf("Final fit: %f\n",pk.Solution.Fitness)
      i -= 1
    }else{
      if coop{
        if len(toShare)==int(miners){
          sort.Sort(toShare)
          fmt.Println("Sharing..")
          for _,v := range address{
            toSend := new(ga.Packet)
            toSend.Shared = toShare.DeepCopy()
            v <- *toSend
          }
          toShare = toShare[:0]
        }
      }else{
        toSend := new(ga.Packet)
        address[pk.Solution.Conf.Miner] <- *toSend
      }
    }
  }
  best_of_all := best[0]
  for j:=0;j<len(best);j++{
    if ga.Optimum(best[j].Fitness,best_of_all.Fitness){
      best_of_all = best[j]
    }
  }
  fmt.Println("\n config: ")
  fmt.Println(best_of_all.Conf)
  fmt.Printf("Best fitness: %f\n",best_of_all.Fitness)
  data, err := json.Marshal(best)
  if err != nil {
    fmt.Println(err)
  } else {
    err = ioutil.WriteFile(outFile, data, 0644)
  }
}

func main(){
  var tp string = os.Args[1]
  var plugname string = os.Args[2]
  var path string = os.Args[3]
  fmt.Println(tp,plugname,path)
  files, err := ioutil.ReadDir(path)
  if err != nil {panic(err)}
  var pnames []string
  for _, f := range files {
    name := f.Name()
    if len(name)>5 && name[len(name)-5:]==".json"{
      pnames = append(pnames,name[:len(name)-5])
    }
  }
  for i:=0;i<len(pnames);i++{
    pname := pnames[i]
    fmt.Println("Process",pname)
    plug, err := plugin.Open("./definitions/"+plugname+".so")
  	if err != nil {panic(err)}
  	definition, err := plug.Lookup("Definition")
  	if err != nil {panic(err)}
    var problem Problem
  	problem, ok := definition.(Problem)
    if !ok {
      panic("The module does not implement Problem interface")
    }
    problem.Initialize(path+pname+".json")
    problDna := problem.New()
    outfile := path+"res500/"+tp+"_"+pname+".json"
    execGAOnMiners(problDna,500,tp=="coop",outfile)
  }
}
