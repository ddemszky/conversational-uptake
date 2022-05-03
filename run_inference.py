"""Author: Dora Demszky

Predict uptake scores for utterance pairs, by running inference with an existing model checkpoint.

Usage:

python run_inference.py --data_file data/uptake_data.csv --speakerA student_text --speakerB teacher_text --output_col uptake_predictions --output predictions/uptake_data_predictions.csv

"""

from argparse import ArgumentParser
import string
import re
from scipy.special import softmax
import pandas as pd

from utils import clean_str, clean_str_nopunct
import torch
from transformers import BertTokenizer
from utils import MultiHeadModel, BertInputBuilder

punct_chars = list((set(string.punctuation) | {'’', '‘', '–', '—', '~', '|', '“', '”', '…', "'", "`", '_'}))
punct_chars.sort()
punctuation = ''.join(punct_chars)
replace = re.compile('[%s]' % re.escape(punctuation))


def get_num_words(text):
    if not isinstance(text, str):
        print("%s is not a string" % text)
    text = replace.sub(' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    text = re.sub(r'\[.+\]', " ", text)
    return len(text.split())


def get_clean_text(text, remove_punct=False):
    if remove_punct:
        return clean_str_nopunct(text)
    return clean_str(text)


def get_prediction(model, instance, device):
    instance["attention_mask"] = [[1] * len(instance["input_ids"])]
    for key in ["input_ids", "token_type_ids", "attention_mask"]:
        instance[key] = torch.tensor(instance[key]).unsqueeze(0)  # Batch size = 1
        instance[key].to(device)

    output = model(input_ids=instance["input_ids"],
                   attention_mask=instance["attention_mask"],
                   token_type_ids=instance["token_type_ids"],
                   return_pooler_output=False)
    return output

def get_uptake_score(utterances, speakerA, speakerB, model, device, input_builder, max_length):

    textA = get_clean_text(utterances[speakerA], remove_punct=False)
    textB = get_clean_text(utterances[speakerB], remove_punct=False)

    instance = input_builder.build_inputs([textA], textB,
                                          max_length=max_length,
                                          input_str=True)
    output = get_prediction(model, instance, device)
    uptake_score = softmax(output["nsp_logits"][0].tolist())[1]
    return uptake_score


def main():
    parser = ArgumentParser()
    parser.add_argument("--data_file", type=str, default="", help="Path or url of the dataset (csv).")
    parser.add_argument("--speakerA", type=str, default="speakerA", help="Column indicating speaker A.")
    parser.add_argument("--speakerB", type=str, default="speakerB", help="Column indicating speaker B (uptake is calculated for this speaker).")
    parser.add_argument("--model_checkpoint", type=str,
                        default="checkpoints/Feb25_09-02-16_combined_education_dataset_02252021.json_6.25e-05_hist1_cand4_bert-base-uncased_ne1_nsp1",
                        help="Path, url or short name of the model")
    parser.add_argument("--output_col", type=str, default="uptake_predictions",
                        help="Name of column for storing predictions.")
    parser.add_argument("--output", type=str, default="",
                        help="Filename for storing predictions.")
    parser.add_argument("--max_length", type=int, default=120, help="Maximum input sequence length")
    parser.add_argument("--student_min_words", type=int, default=5, help="Maximum input sequence length")
    args = parser.parse_args()


    print("Loading models...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    input_builder = BertInputBuilder(tokenizer=tokenizer)
    uptake_model = MultiHeadModel.from_pretrained(args.model_checkpoint, head2size={"nsp": 2})
    uptake_model.to(device)

    utterances = pd.read_csv(args.data_file)
    print("EXAMPLES")
    for i, row in utterances.head().iterrows():
        print("speaker A: %s" % row[args.speakerA])
        print("speaker B: %s" % row[args.speakerB])
        print("----")

    print("Running inference on %d examples..." % len(utterances))
    uptake_model.eval()
    uptake_scores = []
    with torch.no_grad():
        for i, utt in utterances.iterrows():
            prev_num_words = get_num_words(utt[args.speakerA])
            if prev_num_words < args.student_min_words:
                uptake_scores.append(None)
                continue
            uptake_score = get_uptake_score(utterances=utt,
                             speakerA=args.speakerA,
                             speakerB=args.speakerB,
                             model=uptake_model,
                             device=device,
                             input_builder=input_builder,
                             max_length=args.max_length)
            uptake_scores.append(uptake_score)

    utterances[args.output_col] = uptake_scores
    utterances.to_csv(args.output, index=False)




if __name__ == "__main__":
    main()