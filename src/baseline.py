import csv
import multiprocessing
import sys
import time
from functools import partial
from fuzzywuzzy import fuzz, process
from kbs import KnowledgeBase
from utils import retrieve_annotations

sys.path.append("./")


def find_best_candidate(kb_data, annotation):
    """Find best candidate in KB for given annotation based on string similarity (Fuzzy Wuzzy token sort ratio).

    Args
        kb_data (KnowledgeBase): instance of the referred class representing a given knowledge base
        annotation (tuple): has format (annotation text, gold label ID, direct ancestor ID, doc)
    
    Returns
        tuple with format ((annotation), top_candidate_id)
    """
    
    top_candidates = process.extract(annotation[0], \
                            kb_data.name_to_id.keys(), scorer=fuzz.token_sort_ratio, limit=2)

    top_candidate_text_1 = top_candidates[0][0]
    top_candidate_id_1 = kb_data.name_to_id[top_candidate_text_1]
        
    if top_candidate_id_1 == annotation[1]: #It is assumed the true disambiguation concept does not exist in KB
        top_candidate_text_2 = top_candidates[1][0]
        top_candidate_id = kb_data.name_to_id[top_candidate_text_2] #2nd best candidate is now the top candidate

    else:
        top_candidate_id = top_candidate_id_1    

    return (annotation, top_candidate_id)


def check_answers(model, partition, answers):
    """Checks correcteness of answers in chosen partition, outputs answer to file, and print out statistics.

    Args
        model (str): "baseline"
        partition (str): has value "hp", "medic", "ctd_anatomy", "ctd_chemicals", "chebi", "go_bp" or "all"
        answers (list): each answer has the format ((text, gold label, direct ancestor, doc), top_candidate_id)

    Returns
        outputs answers in .csv file
        correct_answers_partition_count (int): correct answers in partition
        annotations_partition_count (int): number of annotations in partition
        docs_in_partition_count (int): number of documents in partition
    """
    
    output_annotations = list()
    correct_answers_partition_count = int()
    annotations_partition_count = int()
    doc_unique = list()

    #output results in a csv file
    with open("./" + model + "_" + partition + "_answers.csv", "w", newline="") as out_file:
        
        out_writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        out_writer.writerow(["doc", "text", "gold label", "direct ancestor", "answer", "classification"])

        for annot in answers:

            if annot[0][3] not in doc_unique: #To count the number of docs
                doc_unique.append(annot[0][3])
            
            annotations_partition_count += 1

            if annot[0][2] == annot[1]:
                correct_answers_partition_count += 1
                classification = "1"

            else:
                classification = "0"
            
            out_writer.writerow([annot[0][3], annot[0][0], annot[0][1], annot[0][2], annot[1], classification])

        out_file.close()

    partition_accuracy = (correct_answers_partition_count/annotations_partition_count)*100
    docs_in_partition_count = len(doc_unique)

    print("------------\nTotal docs (", partition , "):", str(docs_in_partition_count),  \
         "\nTotal annotations (", partition, "):", str(annotations_partition_count), \
         "\nCorrect answers:", str(correct_answers_partition_count), \
         "\nAccuracy (", partition, "):", str(partition_accuracy))

    return correct_answers_partition_count, annotations_partition_count, docs_in_partition_count
    

def baseline_model(partition):
    """Applies baseline model based on string matching over EvaNIL dataset.
    
    Arg
        partition (str): has value "hp", "medic", "ctd_anatomy", "ctd_chemicals", "chebi", "go_bp" or "all"

    Returns
        prints results for the entire dataset (if "all" selected)
    """

    begin_time = time.time()
    total_valid_annotations = int()
    total_correct_answers = int()
    total_docs_count = int()

    if partition != "all":
        partitions = [partition]
    
    else:
        #partitions = ["hp", "chebi", "go_bp", "medic", "ctd_anatomy", "ctd_chemicals"]
        partitions = ["medic", "ctd_anatomy", "ctd_chemicals"]
    for partition in partitions:
        kb_data = KnowledgeBase(partition)
        part_annotations = retrieve_annotations(partition, test=True) #get annotations only from test set
        annotations_partition_count= int()
        correct_answers_partition_count = int()
        valid_annotations = list()
        
        if partition == "ctd_anatomy" or partition == "ctd_chemicals":
            kb_data.load_tsv(partition)
        
        else:
            kb_data.load_obo(partition)
        
        for doc in part_annotations: #Only consider annotations with 1 or 2 words
            
            for annotation in part_annotations[doc]:
                annotations_words = annotation[0].split(" ")
                    
                if len(annotations_words) == 1 or len(annotations_words) == 2: 
                    annotations_partition_count += 1 
                    valid_annotations.append((annotation[0],annotation[3], annotation[4], doc)) 
        
        partial_func = partial(find_best_candidate, kb_data)
        
        with multiprocessing.Pool(processes=15) as pool:
            top_candidates = pool.map(partial_func, valid_annotations)

        correct_answers_partition_count, annotations_partition_count, \
            docs_in_partition_count = check_answers("baseline", partition, top_candidates)

        total_correct_answers += correct_answers_partition_count
        total_valid_annotations += annotations_partition_count
        total_docs_count += docs_in_partition_count
        print("\nPartition runtime:", str(time.time()-begin_time), "s")
    
    if partition == "all":
        global_accuracy = (total_correct_answers/total_valid_annotations)*100
        print("Total docs EvaNIL:", str(total_docs_count),\
            "\nAccuracy (global):", str(global_accuracy))
    
    print("\nTotal runtime:", str(time.time()-begin_time), "s")


if __name__ == "__main__":
    baseline_model(sys.argv[1])