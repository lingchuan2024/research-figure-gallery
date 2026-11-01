"""Generate deterministic, explicitly synthetic data. No external downloads."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import csv
import numpy as np
from gallerylib import ROOT, METHODS, TOOLS

def write(folder, name, records):
    with (folder / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=20261101)
    p.add_argument("--questions", type=int, default=100)
    p.add_argument("--output-dir", type=Path, default=ROOT / "data" / "demo")
    args = p.parse_args()
    if args.questions < 10:
        p.error("--questions must be at least 10")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    n = args.questions
    difficulty = rng.normal(size=n)
    success_latent = rng.random(n)
    metrics, calls, actions, context = [], [], [], []
    for mi, method in enumerate(METHODS):
        for qi in range(n):
            qid = f"Q{qi+1:03d}"
            turns = int(np.clip(np.exp(3.65 + .40*difficulty[qi] - .14*mi + rng.normal(0,.35)), 5, 100))
            inputs = int(np.exp(14.35 + .58*difficulty[qi] - .13*mi + rng.normal(0,.20)))
            output = int(max(1500, turns*rng.normal(190,25)))
            visible = int(rng.random() < np.clip(.67 + .04*mi - .09*difficulty[qi], .12,.97))
            located = int(visible and rng.random() < .91)
            correct = int(success_latent[qi] < np.clip(.22 + .47*located + .025*mi, .05,.94))
            first_visible = int(rng.integers(1, max(2,min(turns,25)))) if visible else ""
            seconds = float(min(3600, turns*rng.uniform(20,48)))
            stop = "Completed" if correct else ("Turn limit" if turns == 100 else ("Timeout" if seconds >= 3600 else "Completed"))
            outcome = "Correct" if correct else ("No final" if stop != "Completed" else ("Abstain" if rng.random()<.15 else "Wrong answer"))
            probabilities = [[.16,.68,.16,0],[.20,.56,.24,0],[.19,.49,.32,0],[.18,.38,.24,.20]][mi]
            sequence = []
            for turn in range(1,turns+1):
                tool = str(rng.choice(TOOLS,p=probabilities)) if turn > 1 else "search"
                sequence.append(tool)
                actions.append(dict(question_id=qid,method=method,turn=turn,tool=tool))
            for tool in TOOLS:
                count = sequence.count(tool)
                # For this demo only: 100 visible characters per search/rerank response.
                chars = count*100 if tool in {"search","rerank"} else int(count*rng.uniform(350,2100))
                calls.append(dict(question_id=qid,method=method,tool=tool,calls=count,returned_chars=chars))
            score_calls = sequence.count("search")*2 if method == "Auto rerank" else sequence.count("rerank")
            passages = score_calls * (1000 if method == "Auto rerank" else 350)
            rr_tokens = int(passages*rng.uniform(110,160))
            rr_gpu_seconds = passages / 220
            cached = int(inputs*.18)
            metrics.append(dict(question_id=qid,method=method,main_input_tokens=inputs,main_uncached_tokens=inputs-cached,main_cached_tokens=cached,main_output_tokens=output,reranker_input_tokens=rr_tokens,rerank_events=score_calls,scored_passages=passages,rerank_gpu_seconds=round(rr_gpu_seconds,6),turns=turns,wall_seconds=round(seconds,6),correct=correct,outcome=outcome,stop_reason=stop,gold_in_pool=max(visible,int(rng.random()<.85)),gold_shown=visible,gold_located=located,first_visible_turn=first_visible))
            weights = np.linspace(.6,1.4,turns)*(1+.10*rng.random(turns))
            token_steps = np.floor(inputs*weights/weights.sum()).astype(int)
            token_steps[-1] += inputs-token_steps.sum()
            for turn,token_count in enumerate(token_steps,1):
                context.append(dict(question_id=qid,method=method,turn=turn,input_tokens=int(token_count)))
    ranks=[]
    for i in range(8*n):
        present = rng.random() > .12
        before = int(np.clip(np.exp(rng.normal(3.0,1.6)),1,1000)) if present else ""
        after = int(np.clip(before*np.exp(rng.normal(-.6,1.2)),1,1000)) if present else ""
        ranks.append(dict(snapshot_id=f"S{i+1:04d}",question_id=f"Q{i%n+1:03d}",in_candidates=int(present),before_rank=before,after_rank=after))
    query=[]
    for i in range(min(24,n)):
        a=float(rng.beta(3,3));b=float(np.clip(a+rng.normal(.07,.11),0,1))
        query.append(dict(question_id=f"Q{i+1:03d}",search_ndcg=round(a,6),rerank_ndcg=round(b,6)))
    budgets=[]
    for mi,m in enumerate(METHODS):
        for budget in [10,20,40,60,100]:
            for qi in range(n):
                prob=float(np.clip(.16+(.44+.035*mi)*(1-np.exp(-budget/(32-3*mi)))-.06*difficulty[qi],.03,.97))
                budgets.append(dict(question_id=f"Q{qi+1:03d}",method=m,budget=budget,correct=int(success_latent[qi]<prob),cost_units=round(budget*(1.0 if mi!=2 else 1.25),3)))
    abl=[]
    agent=[m for m in metrics if m['method']=='Agent rerank']
    for vi,variant in enumerate(["Full system","Search query","Head snippet","BM25 order","Fixed scope","Fixed schedule"]):
        for row in agent:
            c=row['correct']
            if vi and rng.random()<(.04+.025*vi):c=1-c
            abl.append(dict(question_id=row['question_id'],variant=variant,correct=c))
    timeline=[]
    sequence=[("Baseline",[(1,'search',0),(2,'bash',0),(4,'bash',0),(6,'search',0),(8,'bash',0),(10,'read',0),(13,'bash',0),(16,'read',1),(19,'answer',0)]),("Agent rerank",[(1,'search',0),(2,'rerank',1),(3,'read',1),(5,'answer',0)])]
    for method,events in sequence:
        for turn,tool,evidence in events:timeline.append(dict(case_id='DEMO-CASE',method=method,turn=turn,tool=tool,evidence=evidence))
    for name,data in [('questions.csv',metrics),('tool_calls.csv',calls),('actions.csv',actions),('context.csv',context),('ranks.csv',ranks),('query_pairs.csv',query),('budget_runs.csv',budgets),('ablations.csv',abl),('timeline.csv',timeline)]:write(args.output_dir,name,data)
    print(f"Generated 9 synthetic tables for {n} questions, seed={args.seed}")

if __name__ == '__main__':main()
