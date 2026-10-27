"""
Chunking comparison for RAG on SQuAD v1.1 (dev).
Methods: fixed-size, fixed-size + overlap, semantic (LangChain SemanticChunker).
Metrics: Recall@k (k=1,3,5), Exact Match, token F1. Paired stats: exact McNemar.

Usage (real run):
    python run_experiment.py --n-questions 500 --embedder minilm
Usage (retrieval only, no answer generation):
    python run_experiment.py --n-questions 500 --embedder minilm --no-generate
"""
import argparse, collections, csv, json, os, random, re, string, sys, urllib.request
import importlib.metadata as md
import numpy as np
from scipy.stats import binomtest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS

SQUAD_URL = "https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json"
KS = (1, 3, 5)
METHODS = ["fixed", "overlap", "semantic"]


class FakeEmbeddings(Embeddings):
    """Hashing bag-of-words vectors. ONLY for smoke-testing the code, never for results."""
    def __init__(self, dim=256):
        self.dim = dim
    def _vec(self, text):
        v = np.zeros(self.dim, dtype="float32")
        for w in re.findall(r"\w+", text.lower()):
            v[hash(w) % self.dim] += 1.0
        n = np.linalg.norm(v)
        return (v / n if n else v).tolist()
    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]
    def embed_query(self, text):
        return self._vec(text)


def get_embedder(name):
    if name == "fake":
        return FakeEmbeddings()
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        encode_kwargs={"normalize_embeddings": True},
    )


def load_squad(path):
    if not os.path.exists(path):
        urllib.request.urlretrieve(SQUAD_URL, path)
    with open(path, encoding="utf-8") as f:
        return json.load(f)["data"]


def build_corpus_and_questions(data, n_questions, seed):
    docs, questions = [], []
    for art in data:
        text = "\n\n".join(p["context"] for p in art["paragraphs"])
        docs.append(Document(page_content=text, metadata={"title": art["title"]}))
        for p in art["paragraphs"]:
            for qa in p["qas"]:
                questions.append({
                    "id": qa["id"], "title": art["title"], "question": qa["question"],
                    "answers": [a["text"] for a in qa["answers"]],
                })
    rng = random.Random(seed)
    rng.shuffle(questions)
    return docs, questions[:n_questions]


def make_chunks(method, docs, embeddings, size, overlap):
    if method == "fixed":
        sp = CharacterTextSplitter(separator="", chunk_size=size, chunk_overlap=0)
        return sp.split_documents(docs)
    if method == "overlap":
        sp = CharacterTextSplitter(separator="", chunk_size=size, chunk_overlap=overlap)
        return sp.split_documents(docs)
    sp = SemanticChunker(embeddings, breakpoint_threshold_type="percentile",
                         breakpoint_threshold_amount=95)
    return sp.split_documents(docs)


def norm(s):
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def f1_score(pred, gold):
    p, g = norm(pred).split(), norm(gold).split()
    common = collections.Counter(p) & collections.Counter(g)
    same = sum(common.values())
    if not p or not g or same == 0:
        return float(p == g)
    prec, rec = same / len(p), same / len(g)
    return 2 * prec * rec / (prec + rec)


def em_f1(pred, golds):
    em = max(float(norm(pred) == norm(g)) for g in golds)
    f1 = max(f1_score(pred, g) for g in golds)
    return em, f1


def hit(retrieved, q):
    golds = [norm(a) for a in q["answers"]]
    return any(r.metadata["title"] == q["title"] and any(g and g in norm(r.page_content) for g in golds)
               for r in retrieved)


def load_generator():
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    name = "google/flan-t5-base"
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSeq2SeqLM.from_pretrained(name)
    model.eval()
    return tok, model


def generate(tok, model, question, chunks, gen_k, budget=0):
    ctx = "\n".join(c.page_content for c in chunks[:gen_k])
    if budget:
        ctx = ctx[:budget]
    prompt = ("Answer the question using only the context.\n\n"
              f"Context: {ctx}\n\nQuestion: {question}\nAnswer:")
    enc = tok(prompt, return_tensors="pt", truncation=True, max_length=512)
    truncated = len(tok(prompt)["input_ids"]) > 512
    out = model.generate(**enc, max_new_tokens=32, do_sample=False)
    return tok.decode(out[0], skip_special_tokens=True), truncated


def bootstrap_ci(x, n=2000, seed=0):
    x = np.asarray(x, dtype=float)
    rng = np.random.default_rng(seed)
    means = [rng.choice(x, size=len(x), replace=True).mean() for _ in range(n)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def mcnemar_exact(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    n01, n10 = int((~a & b).sum()), int((a & ~b).sum())
    if n01 + n10 == 0:
        return 1.0
    return float(binomtest(n01, n01 + n10, 0.5).pvalue)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-questions", type=int, default=500)
    ap.add_argument("--embedder", choices=["minilm", "fake"], default="minilm")
    ap.add_argument("--chunk-size", type=int, default=500)
    ap.add_argument("--overlap", type=int, default=50)
    ap.add_argument("--gen-k", type=int, default=3)
    ap.add_argument("--ctx-budget", type=int, default=0,
                    help="if >0, cut the prompt context to this many characters (robustness check)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--squad", default="dev-v1.1.json")
    ap.add_argument("--out", default="results.csv")
    ap.add_argument("--no-generate", action="store_true")
    args = ap.parse_args()

    print("versions:", {p: md.version(p) for p in
          ["langchain-text-splitters", "langchain-experimental", "langchain-community",
           "faiss-cpu", "numpy", "scipy"]}, "python", sys.version.split()[0])
    print("args:", vars(args))

    data = load_squad(args.squad)
    docs, questions = build_corpus_and_questions(data, args.n_questions, args.seed)
    print(f"articles={len(docs)}  questions_used={len(questions)}")

    emb = get_embedder(args.embedder)
    gen = None if args.no_generate else load_generator()
    rows, per_method = [], {m: {"hit%d" % k: [] for k in KS} | {"em": [], "f1": [], "trunc": [], "ctxchars5": []} for m in METHODS}

    for m in METHODS:
        chunks = make_chunks(m, docs, emb, args.chunk_size, args.overlap)
        lens = [len(c.page_content) for c in chunks]
        print(f"[{m}] chunks={len(chunks)} mean_len={np.mean(lens):.0f} "
              f"median={np.median(lens):.0f} max={max(lens)}")
        store = FAISS.from_documents(chunks, emb)
        for q in questions:
            ret = store.similarity_search(q["question"], k=max(KS))
            row = {"method": m, "id": q["id"]}
            ctx5 = sum(len(r.page_content) for r in ret[:5])
            row["ctx_chars@5"] = ctx5
            per_method[m]["ctxchars5"].append(ctx5)
            for k in KS:
                h = hit(ret[:k], q)
                row[f"hit@{k}"] = int(h)
                per_method[m][f"hit{k}"].append(int(h))
            if gen:
                pred, trunc = generate(*gen, q["question"], ret, args.gen_k, args.ctx_budget)
                em, f1 = em_f1(pred, q["answers"])
                row.update(pred=pred, em=em, f1=f1, truncated=int(trunc))
                per_method[m]["em"].append(em); per_method[m]["f1"].append(f1)
                per_method[m]["trunc"].append(int(trunc))
            rows.append(row)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in rows for k in r}))
        w.writeheader(); w.writerows(rows)

    print("\n=== SUMMARY (mean, 95% bootstrap CI) ===")
    for m in METHODS:
        parts = []
        for key in [f"hit{k}" for k in KS] + (["em", "f1"] if gen else []):
            x = per_method[m][key]
            lo, hi = bootstrap_ci(x)
            parts.append(f"{key}={np.mean(x):.3f} [{lo:.3f},{hi:.3f}]")
        parts.append(f"mean_ctx_chars@5={np.mean(per_method[m]['ctxchars5']):.0f}")
        if gen:
            parts.append(f"truncated={np.mean(per_method[m]['trunc']):.3f}")
        print(f"{m:9s} " + "  ".join(parts))

    print("\n=== Exact McNemar p-values (raw; apply Holm across the 3 pairs) ===")
    pairs = [("fixed", "overlap"), ("fixed", "semantic"), ("overlap", "semantic")]
    metrics = ["hit5"] + (["em"] if gen else [])
    for a, b in pairs:
        for key in metrics:
            p = mcnemar_exact(per_method[a][key], per_method[b][key])
            print(f"{a} vs {b} on {key}: p={p:.4f}")
    print(f"\nper-question results saved to {args.out}")


if __name__ == "__main__":
    main()
