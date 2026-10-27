"""
Tests whether semantic chunking loses answers because the embedding model only reads
the first 256 tokens of each chunk.

For every sampled question it finds the chunks of the gold article that contain the
answer, and measures how many tokens come before the end of the answer. If the answer
ends after the model's input limit, the embedding of that chunk never saw it.
Then it compares Recall@5 for questions whose answer is visible vs. not visible.

Needs run_experiment.py, dev-v1.1.json and results_main.csv in the same folder.
    python semantic_visibility.py --squad dev-v1.1.json --results results_main.csv
Rebuilding the semantic chunks takes about as long as that step in the main run.
"""
import argparse, json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import run_experiment as R

ap = argparse.ArgumentParser()
ap.add_argument("--squad", default="dev-v1.1.json")
ap.add_argument("--results", default="results_main.csv")
ap.add_argument("--n-questions", type=int, default=500)
ap.add_argument("--seed", type=int, default=42)
ap.add_argument("--embedder", choices=["minilm", "fake"], default="minilm")
ap.add_argument("--out", default="semantic_visibility.json")
a = ap.parse_args()

data = R.load_squad(a.squad)
docs, qs = R.build_corpus_and_questions(data, a.n_questions, a.seed)
emb = R.get_embedder(a.embedder)

if a.embedder == "fake":
    maxlen = 256
    count = lambda s: len(s.split())          # smoke test only
else:
    from sentence_transformers import SentenceTransformer
    st = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    maxlen = st.max_seq_length
    tok = st.tokenizer
    count = lambda s: len(tok(s, add_special_tokens=False)["input_ids"])
limit = maxlen - 2                              # room for the two special tokens
print("max_seq_length:", maxlen, " usable tokens:", limit)

chunks = {m: R.make_chunks(m, docs, emb, 500, 50) for m in ["fixed", "overlap", "semantic"]}
out = {"max_seq_length": maxlen}
for m, ch in chunks.items():
    lens = [count(c.page_content) for c in ch]
    out[f"{m}_chunks"] = len(ch)
    out[f"{m}_share_over_limit"] = float(np.mean([l > limit for l in lens]))
    out[f"{m}_median_tokens"] = float(np.median(lens))
    print(f"[{m}] chunks={len(ch)} mean_chars={np.mean([len(c.page_content) for c in ch]):.0f} "
          f"median_tokens={np.median(lens):.0f} share_over_limit={np.mean([l > limit for l in lens]):.3f}")
print("(main run semantic chunks were: 589, mean_len 2720; they should match)")

sem = chunks["semantic"]
by = {}
for c in sem:
    by.setdefault(c.metadata["title"], []).append(c.page_content)

def end_token(chunk, answers):
    best = None
    for ans in answers:
        i = chunk.find(ans)
        if i < 0:
            i = chunk.lower().find(ans.lower())
        if i >= 0:
            n = count(chunk[: i + len(ans)])
            best = n if best is None else min(best, n)
    return best

group = {}
for q in qs:
    golds = [R.norm(x) for x in q["answers"]]
    bearing = [t for t in by[q["title"]] if any(g and g in R.norm(t) for g in golds)]
    if not bearing:
        group[q["id"]] = "no_chunk_has_answer"
        continue
    pos = [end_token(t, q["answers"]) for t in bearing]
    known = [p for p in pos if p is not None]
    if any(p <= limit for p in known):
        group[q["id"]] = "visible"
    elif known and len(known) == len(pos):
        group[q["id"]] = "beyond_limit"
    else:
        group[q["id"]] = "unknown_position"

res = pd.read_csv(a.results)
res["group"] = res.id.map(group)
rows = {}
print("\nRecall@5 by whether the answer lies inside the embedding model's input window")
print(f"{'group':22s}{'n':>5s}{'semantic':>10s}{'fixed':>8s}{'overlap':>9s}")
for g in ["visible", "beyond_limit", "no_chunk_has_answer", "unknown_position"]:
    ids = [i for i, v in group.items() if v == g]
    if not ids:
        continue
    row = {"n": len(ids)}
    for m in ["semantic", "fixed", "overlap"]:
        d = res[(res.method == m) & (res.id.isin(ids))]
        row[m] = float(d["hit@5"].mean())
    rows[g] = row
    print(f"{g:22s}{row['n']:5d}{row['semantic']:10.3f}{row['fixed']:8.3f}{row['overlap']:9.3f}")
out["groups"] = rows
json.dump(out, open(a.out, "w"), indent=2)
print("\nsaved", a.out)
