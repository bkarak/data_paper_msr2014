# Calculates pairwise correlations from the data in
# data/bug_correlation_counters.csv, which is produced
# by bug_correlation_tab.py

library(ellipse)

bug.counts <- read.csv("data/bug_correlation_counters.csv")

bug.counts$SECURITY_HIGH <- bug.counts$SECURITY_HIGH + bug.counts$MALICIOUS_CODE

bug.counts$MALICIOUS_CODE <- NULL

bug.counts$TOTAL_MALICIOUS_CODE <- NULL
bug.counts$TOTAL_SECURITY_HIGH <- NULL
bug.counts$TOTAL_SECURITY_LOW <- NULL
bug.counts$TOTAL_STYLE <- NULL
bug.counts$TOTAL_BAD_PRACTICE <- NULL
bug.counts$TOTAL_CORRECTNESS <- NULL
bug.counts$TOTAL_MT_CORRECTNESS <- NULL
bug.counts$TOTAL_PERFORMANCE <- NULL
bug.counts$TOTAL_I18N <- NULL
bug.counts$TOTAL_EXPERIMENTAL <- NULL

for (i in (2:(ncol(bug.counts) - 1))) {
  for (j in ((i + 1):(ncol(bug.counts) - 1))) {
    print(paste(colnames(bug.counts)[i], ":", colnames(bug.counts[j])))
    print(cor.test(bug.counts[, i], bug.counts[, j]))
  }
}

ctab <- cor(bug.counts[,-1], method="pearson", use="pairwise.complete.obs")
png('corrplot.png')
colorfun <- colorRamp(c("#ff0000","white","#3366CC"), space="Lab")
plotcorr(ctab, col=rgb(colorfun((ctab+1)/2), maxColorValue=255))
dev.off()
ctab
