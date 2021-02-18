# EvaNIL
Silver standard dataset for large-scale NIL entity linking evaluation.

Built from existing Biomedical and Life Sciences corpora.

![Dataset generation schema](https://github.com/pedroruas18/EvaNIL/blob/main/evaNIL.png)

## Setup environment

Dockerfile includes the commands to setup a Docker image with the appropriate environment.


## Retrieve necessary data
To download the required knowledge base and corpora files:

```
./download_data.sh
```


## Build the dataset

To build a given partition of the dataset:

```
python src/dataset.py <partition>
```

Arg
- partition: the selected partition to build.

Options:
- "medic" (CTD-MEDIC)
- "ctd_anatomy" (CTD-Anatomy)
- "ctd_chemicals" (CTD-Chemicals)
- "chebi" (ChEBI)
- "go_bp" (GO-Biological Process)
- "hp" (HPO)

Example:

```
python src/dataset.py hp
```

Output: train.json, dev.json and test.json in ./evanil/hp dir

See [sample file](https://github.com/pedroruas18/EvaNIL/blob/main/sample.json).

## Statistics

To get dataset statistics:
```
python src/statistics.py <partition>
```

Arg
- partition: the selected partition to build.

Options:
- "medic" (CTD-MEDIC)
- "ctd_anatomy" (CTD-Anatomy)
- "ctd_chemicals" (CTD-Chemicals)
- "chebi" (ChEBI)
- "go_bp" (GO-Biological Process)
- "hp" (HPO)

Example:
```
python src/statistics.py hp
```

Output:
```
Total number of documents: 3173
Total number of annotations: 13741
Annotations per document: 4.330601953986763
Max number of annotations per document: 52
Min number of annotations per document: 1
8503 annotations (61.880503602357905 %) with 1 word
2664 annotations (19.387235281275018 %) with 2 words
801 annotations (5.829270067680663 %) with 3 words
155 annotations (1.1280110617858963 %) with 4 words
38 annotations (0.27654464740557455 %) with 5 or more words
```

See [statistics for the entire dataset](https://github.com/pedroruas18/EvaNIL/blob/main/stats.csv).

## Baseline model
The baseline model is based on string matching and uses python [fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/).

To apply the baseline model over the built dataset:

```
python src/baseline.py <partition>
```
Arg
- partition: the selected partition to build.

Options:
- "medic" (CTD-MEDIC)
- "ctd_anatomy" (CTD-Anatomy)
- "ctd_chemicals" (CTD-Chemicals)
- "chebi" (ChEBI)
- "go_bp" (GO-Biological Process)
- "hp" (HPO)
- "all"

Example:
```
python src/baseline.py hp
```
Output:
```
Total docs ( hp ): 314 
Total annotations ( hp ): 1270 
Correct answers: 18 
Accuracy ( hp ): 1.4173228346456692

Partition runtime: 31.075466632843018 s

Total runtime: 31.075491189956665 s
```

Predicted answers for the annotations are outputted in the file "baseline_hp_answers.csv".


To apply baseline model over all partitions of EvaNIL dataset:

```
python3 src/baseline.py all
```
See [results for the entire dataset](https://github.com/pedroruas18/EvaNIL/blob/main/baseline_results.csv).

## Python Multiprocessing
The functions used to parse documents from the PubMed DS corpus and to find the best candidate in the baseline model were adapted to allow parallel processing using the Pool class from [Python Multiprocessing package](https://docs.python.org/3/library/multiprocessing.html). 

For example, the task of finding the best candidate in the knowledge base for all entities followed a map-reduce architecture: the input was distributed to 20 cores and then the output was collected, being returned in a list. In the graph, we can observe the runtime of original baseline model vs the implementation using Multiprocess when applied to the test set of the split 1 of MEDIC partition:

![Runtime](https://github.com/pedroruas18/EvaNIL/blob/main/chart.png)

