# Conversational Uptake
This repository contains data for the paper: 

Demszky, D., Liu, J., Mancenido, Z., Cohen, J., Hill, H., Jurafsky, D., & Hashimoto, T. (2021). [Measuring Conversational Uptake: A Case Study on Student-Teacher Interactions](https://arxiv.org/pdf/2106.03873.pdf). In _Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics (ACL)_.

```
@inproceedings{demszky2021measuring,
  title={{Measuring Conversational Uptake: A Case Study on Student-Teacher Interactions}},
  author={Demszky, Dorottya and Liu, Jing and Mancenido, Zid and Cohen, Julie and Hill, Heather and Jurafsky, Dan and Hashimoto, Tatsunori},
   booktitle = {Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics (ACL)},
  year={2021}
}
```

## Annotated Uptake Dataset

The annotated dataset contains a sample of **2246 exchanges** extracted from a dataset of anonymized 4-5th grade US elementary math classroom transcripts collected by the [National Center for Teacher Effectiveness (NCTE)](https://cepr.harvard.edu/ncte) in New England schools between 2010-2013. These exchanges are turns by students (with at least 5 words), followed by teacher turns in a classroom conversation. 

The exchanges are annotated by thirteen experts in math instruction (former and current math teachers and trained raters for classroom observation protocols). The coding instrument can be viewed [here](https://docs.google.com/document/d/1UGAXW3H-bV1m0PWcDM7aGcRgkdrY-fovcPstB4YphvA/edit?usp=sharing).

Each exchange is coded for three items:
* `student_on_task`: Whether the student utterance is on task (related to math). This is a binary variable: either 0 (off task) or 1 (on task).
* `teacher_on_task`: Whether the teacher utterance is on task (related to math). This is a binary variable: either 0 (off task) or 1 (on task).
* `uptake`: Degree of uptake, or in other words, the extent to which the teacher demonstrates that they have heard the student by building on their contribution. This could take values 0 (low), 1 (mid), 2 (high).

The data is in the comma-separated file `data/uptake_dataset.csv`.

The file includes the following columns:

* `obs_id`: Observation ID, mappable to unique transcripts in the NCTE dataset.
* `exchange_idx`: ID of the exchange within the transcript.
* `student_text`: Student utterance.
* `teacher_text`: Teacher utterance (following the utterance in `student_text`).
* `student_on_task`: Average rating for `student_on_task` across the three raters.
* `student_on_task_majority`: The majority rating for `student_on_task` across the three raters.
* `student_on_task_num_agree`: Number of raters who agree on the `student_on_task` code.
* `student_on_task_zscore`: Average rating for `student_on_task`, after z-scoring the ratings for each rater.
* `teacher_on_task`: Average rating for `teacher_on_task` across the three raters.
* `teacher_on_task_majority`: The majority rating for `teacher_on_task` across the three raters.
* `teacher_on_task_num_agree`: Number of raters who agree on the `teacher_on_task` code.
* `teacher_on_task_zscore`: Average rating for `teacher_on_task`, after z-scoring the ratings for each rater.
* `uptake`: Average rating for `uptake` across the three raters.
* `uptake_majority`: The majority rating for `uptake` across the three raters. Value is None if there is no majority label (no agreement between any of the raters).
* `uptake_num_agree`: Number of raters who agree on the `uptake` code.
* `uptake_zscore`: Average rating for `uptake`, after z-scoring the ratings for each rater. *We use this item for our main evaluations*.

Each example can be **uniquely identified with the combination of the `obs_id` and `exchange_idx` columns**.

## Pre-Trained Model

Please email Dora (ddemszky@stanford.edu) to request the pre-trained uptake model (~880MB). In your email, please include your name, affiliation, short project description (1-2 sentences), list of names on your research team who will be working with the checkpoint, and the following:

```
I am requesting this checkpoint for my own research and it will be only used by me and my research team. My research team agrees to the following restrictions by requesting this model:
1. We will not use this model for commercial purposes.
2. We will not attempt to recover any of the training / fine-tuning data from the model.
3. We will not share or distribute this model in any way with outside of the research team and the project indicated in this email.
```

## Running inference

Please follow the following steps to run inference with the pre-trained model:
1. Install requirements `$ pip install -r requirements.txt`. Currently the Pytorch version is for a CPU, so if you're running this on a GPU, you'll probably want to update the Pytorch (and maybe transformer) installation so that it works on a GPU.
2. Download and unzip the model checkpoint -- see above.
3. Put all your data into a single csv file. There should be a column indicating the utterance from speaker A and the utterance from speaker B, and the model will predict to what extent speaker B's utterance takes up speaker A's utterance. See the `data/uptake_annotations.csv` file for an example, where speaker A = `student_text` and speaker B = `teacher_text`.
4. You can inference like this: `$ python run_inference.py --data_file data/uptake_data.csv --speakerA student_text --speakerB teacher_text --output_col uptake_predictions --output predictions/uptake_data_predictions.csv`

**Notes**
* Make sure there are no empty string or NaNs in your data.
* The uptake model will only predict scores for utterance pairs where the first utterance is at least *5 tokens* long.
