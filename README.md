# EvaNIL
Silver standard dataset for large-scale NIL entity linking evaluation.

Built from existing Biomedical and Life Sciences corpora.

![Dataset generation schema](https://github.com/pedroruas18/EvaNIL/blob/main/images/evaNIL.pdf)

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
python src/dataset <partition>
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
python src/dataset chebi
```

Output: train.json, dev.json and test.json in ./dataset/chebi dir

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
python src/statistics.py chebi
```

Output:
```
Total number of documents: 97
Total number of annotations: 4091
Annotations per document: 42.175257731958766
Max number of annotations per document: 315
Min number of annotations per document: 2
3699 annotations (90.41799071131753 %) with 1 word
327 annotations (7.993155707650941 %) with 2 words
51 annotations (1.246638963578587 %) with 3 words
11 annotations (0.2688829137130286 %) with 4 words
2 annotations (0.048887802493277926 %) with 5 or more words
```


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
python src/baseline.py chebi
```
Output:
```
Total docs ( chebi ): 10
Total annotations ( chebi ): 358
Correct answers: 13
Accuracy ( chebi ): 3.6312849162011176

Partition runtime: 114.79057455062866 s

Total runtime: 114.79064726829529 s
```

Predicted answers for the annotations are outputted in the file "baseline_chebi_answers.csv" in ./results dir


To apply baseline model over all partitions of EvaNIL dataset:

```
python3 src/baseline.py all
```

