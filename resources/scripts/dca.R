library(edgeR)
coverages = read.csv("./test/coverages.csv", sep="\t", row.names=1)
totals = read.csv("./test/totals.csv", sep="\t", row.names=1)
experimental_design = read.csv("./test/experimental_design.csv", sep="\t", row.names=1)
colnames(experimental_design) <- c("group")

## Step 1: load data in edgeR
# NOTE: the column lib.size containss the absolute coverage for a given sample across genes and it is used to normalise samples by 
# their depth of coverage, this will be a confounding factor for our analysis if used as expected
# we will use a constant lib.size with the average of depth of coverage across all samples and genes
dgelist = DGEList(coverages, group = t(experimental_design), lib.size = rep(mean(totals$X0), length(colnames(coverages))))

## Step 2: filtering genes with very low expression as these are irrelevant in DGE. In our case we will skip this step

## Step 3: normalise by RNA composition, so highly expressed genes do not shadow others.
# NOTE: other fancy normalisations by sample specific GC content and gene length are not applied
dgelist <- calcNormFactors(dgelist)

## Step 4: estimate dispersions calculates pseudo counts after adjusting by library size
# NOTE: as we fixed the library size to a constant across all samples pseudo counts should be equal to original counts...
dgelist <- estimateCommonDisp(dgelist)

## Step 5: Performs Fisher exact test
et = exactTest(dgelist)

## Step 6: Returns results ordered by significance and adjusts for multiple tests
# `logFC` is the fold change between the groups after applying a log transformation
# `logCPM` is the counts per million between the groups after applying a log transformation, useful to discard genes with very low values
# `PValue` is the p-value of the Fisher exact test
# `FDR` is the FDR adjusted p-value
topTags(et, adjust.method = "fdr")





