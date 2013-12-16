jarsize.counts <- read.csv('data/project_counters_jarsize.csv',
                           header=TRUE)

for (i in names(jarsize.counts)[4:length(colnames(jarsize.counts))]) {
  cor.result = cor.test(jarsize.counts$jarsize, jarsize.counts[[i]])
  cor.result$data.name = paste("jarsize", "and", i)
  print(cor.result)
}
