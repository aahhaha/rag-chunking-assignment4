# Final Defence Speaking Script

Target duration 10 minutes. Rehearse aloud and adjust to your pace.

## Slide 1 Chunking and Context Limits

My project examines how document chunking affects a retrieval augmented question answering system. The system first searches for evidence and then generates an answer. I compare fixed, overlapping and semantic chunks using compact models that can run locally. The main result is that overlap improves retrieval, while its improvement in exact answers is less certain. The semantic configuration performs poorly when its long chunks meet small input windows. I will explain the experiment, the statistical evidence and the limits of this conclusion. The manuscript builds on my earlier course experiments rather than claiming that I collected a new benchmark for the final project.

## Slide 2 Research Question and Contribution

Imagine a book that cannot fit on a reader's desk. We cut it into cards, find relevant cards and give a few to the reader. Cutting at the wrong place can separate an answer from its explanation. My research question asks how much three cutting strategies change retrieval and answer accuracy under one shared pipeline. The contribution is a paired comparison with saved question outputs and a diagnosis of context length problems. I do not propose a new chunking algorithm. I also do not claim that one method is always best across every model or dataset.

## Slide 3 Related Research

The closest study is Qu and colleagues. They found that semantic chunking did not give consistent gains across their tested retrieval tasks. Kiss and colleagues obtained positive results with a different Max-Min semantic algorithm. These findings are not necessarily contradictory, because the algorithms, datasets and answer tasks differ. My study examines a narrower compact-model setting. It makes the embedding and generation windows explicit and reports a matched context-cap check. This is the gap I address. It is not a claim that no previous researcher has compared chunking methods.

## Slide 4 Data and Pipeline

The dataset is SQuAD version 1.1 development data. The retrieval collection contains 48 Wikipedia articles. I select 500 questions with seed 42 and evaluate the same IDs under every method. MiniLM creates normalised vectors and FAISS performs exact search. I retrieve five chunks for evaluation, but pass only the first three to FLAN-T5-base. The generator uses greedy decoding, a 512-token input limit and at most 32 new tokens. A retrieval hit requires an answer string in the correct article. This makes the metric transparent, but it does not prove that the entire supporting statement reaches the generator.

## Slide 5 Three Chunking Methods

Fixed chunks contain up to 500 characters with no overlap. The overlap condition uses the same size and repeats 50 characters at each boundary. The semantic condition splits at large changes between sentence embeddings using a 95th-percentile threshold. That threshold is not 95 percent answer accuracy. Fixed produces 3,235 chunks, overlap 3,585 and semantic only 589. Semantic chunks average 2,720 characters, much longer than the other conditions. The methods share models and nominal limits, but the effective amount of usable text differs. That distinction is central to the interpretation.

## Slide 6 Main Results

Overlap has the highest observed Recall at five, 81.8 percent, compared with 75.2 for fixed and 66.4 for semantic. These correspond to 409, 376 and 332 successful questions out of 500. Exact Match is 58.0, 54.8 and 1.4 percent. F1 gives partial credit for overlapping words, so it is higher than Exact Match. The large semantic gap between retrieval and answers shows why the stages need separate evaluation. A retrieved full string can contain the answer even when the generator later receives an incomplete input. The manuscript reports uncertainty intervals alongside these point estimates.

## Slide 7 Paired Statistical Evidence

Because the methods answer the same questions, I use paired analysis. For retrieval, overlap succeeds alone on 58 questions and fixed alone on 25. The net gain is 33 questions, or 6.6 percentage points. The paired bootstrap interval is 3.0 to 10.0 points and Holm adjusted p is 0.0008. McNemar tests binary disagreements, while bootstrap estimates uncertainty by resampling saved questions. Holm accounts for the three comparisons within each metric. For Exact Match, p is 0.1332 and the difference interval includes zero. I therefore cannot confidently claim an answer accuracy advantage, and I do not interpret this as proof of equivalence.

## Slide 8 Error Analysis and Input Limits

There are two length problems. MiniLM represents at most 256 tokens, with about 254 available for text. A long chunk may contain the answer beyond that visible portion. Later, the generator prompt combines three chunks before placing the question at the end. Its 512-token limit can remove useful text or the question. Semantic prompts are truncated in 478 out of 500 cases. Among wrong semantic answers, 477 are assigned first to truncation. One truncated prompt still gives a correct exact answer, which explains the different counts. The categories describe observed outcomes rather than proven causes for each individual prediction.

## Slide 9 Matched Context Check

I added an exploratory context cap after observing the truncation problem. It keeps only the first 1,500 context characters before tokenisation. The fair comparison uses the same 300 questions in both runs. Semantic Exact Match rises from 1.33 percent, four correct answers, to 24.67 percent, 74 correct answers. The paired improvement is 23.33 points with an interval from 18.33 to 28.33. Fixed drops by one point and overlap is unchanged. Tokenizer truncation falls to zero, but the character cap still removes text. This supports the importance of prompt construction without isolating semantic boundaries or validating the setting on unseen questions.

## Slide 10 Limitations

The main threat is unequal effective input length. Semantic changes both boundaries and chunk length, so the whole gap cannot be assigned to meaning preservation alone. The experiment uses one English dataset, one encoder, one generator and one shuffle. String containment can accept irrelevant answer occurrences, and Exact Match can penalise acceptable wording. Questions from the same articles are related, so question bootstrap intervals may understate some uncertainty. The extra checks were chosen after seeing the results. Future work should freeze the protocol, apply token caps before indexing, preserve the question and evaluate untouched data with additional models.

## Slide 11 Reproducibility

Every main question has saved method, ID, prediction and metric fields. The analysis aligns IDs, regenerates summaries and checks the matched subset. A later full inference rerun produced the same 1,500 prediction strings and per-item numeric outcomes. It took about 64.8 minutes in the existing local environment. Codex operated that rerun on my computer, as disclosed. It is not an independent human replication or a clean installation of the complete model pipeline. A separate clean environment check validated saved-output analysis. The README explains the distinction and gives a fast command to rebuild every Results table and figure.

## Slide 12 Conclusion and Journal Fit

My conclusion is conditional. Overlap improves retrieval in this compact pipeline, while its Exact Match advantage remains uncertain. The semantic hypothesis is not supported under this configuration. The diagnostic result is that chunking must be evaluated together with the input limits of the models that use the chunks. Discover Computing is the primary target because it publishes semantic chunking and RAG pipeline evaluations. Its Scopus source record and official source list show active coverage. Discover Artificial Intelligence is the backup. Journal submission is voluntary after the course and publication is not guaranteed. I can now show the saved rows behind a result or explain the statistical tests.