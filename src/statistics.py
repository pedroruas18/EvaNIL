import json
import os
import sys
from utils import retrieve_annotations

sys.path.append("./")


def get_corpus_statistics(annotations):
    """Calculate and output the corpus statistics.

    Args
        annotations (dict): has format {file_id: [(annotation_str, start_pos, end_pos, hp_id, direct_ancestor)]}
    
    Returns
        Prints out statistics of chosen partition, e.g. Total number of documents , annotations, etc.
    """
    
    annotations_count = int()
    #doc_count = len(annotations.keys())
    doc_count = 0
    total_annot = int()
    unique_annot_count = int()
    max_annotations_count = int()
    min_annotations_count = int(100)
    word_1 = int()
    word_2 = int()
    word_3 = int()
    word_4 = int()
    word_5_more = int()

    for doc in annotations:
        doc_count += 1
        annotations_count += len(annotations[doc])
        added_annotations = list()

        if len(annotations[doc]) > max_annotations_count:
            max_annotations_count = len(annotations[doc])
            
        if len(annotations[doc]) < min_annotations_count:
            min_annotations_count = len(annotations[doc])

        for annotation in annotations[doc]:
            total_annot += 1
            
            if annotation[1] not in added_annotations:
                added_annotations.append(annotation[1])
                unique_annot_count += 1
                annotations_words = annotation[0].split(" ")
                
                if len(annotations_words) == 1:
                    word_1 += 1
                
                elif len(annotations_words) == 2:
                    word_2 += 1
                
                elif len(annotations_words) == 3:
                    word_3 += 1

                elif len(annotations_words) == 4:
                    word_4 += 1

                elif len(annotations_words) >= 5:
                    word_5_more += 1
        
    stats = "Total number of documents: " + str(doc_count) + "\n" \
            + "Total number of annotations: " + str(annotations_count) + "\n" \
            + "Annotations per document: " + str(float(annotations_count/doc_count)) + "\n" \
            + "Max number of annotations per document: " + str(max_annotations_count) + "\n" \
            + "Min number of annotations per document: " + str(min_annotations_count) + "\n" \
            + str(word_1) + " annotations (" + str(float(word_1/annotations_count)*100) + " %) with 1 word\n" \
            + str(word_2) + " annotations (" + str(float(word_2/annotations_count)*100) + " %) with 2 words\n" \
            + str(word_3) + " annotations (" + str(float(word_3/annotations_count)*100) + " %) with 3 words\n" \
            + str(word_4) + " annotations (" + str(float(word_4/annotations_count)*100) + " %) with 4 words\n" \
            + str(word_5_more) + " annotations (" + str(float(word_5_more/annotations_count)*100) \
            + " %) with 5 or more words"

    print(stats)


if __name__ == "__main__":
    get_corpus_statistics(retrieve_annotations(sys.argv[1], test=False))
    