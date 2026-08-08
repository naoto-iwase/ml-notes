# Figure Triage

This file records the source-figure audit for the bilingual *Agent Harness Optimization* book. The Japanese book is the canonical triage location; every retained figure is mirrored byte-for-byte into the English book. `_figure_manifest.md` is the generated asset inventory, while this file records editorial and rights decisions.

## Audit protocol

- Fetched 23 arXiv source bundles from `references.bib` into `/tmp/arxiv_figures/<id>/`.
- Parsed figure environments, captions, labels, and surrounding TeX.
- Visually inspected rendered candidates rather than deciding from filenames alone.
- Compared candidates against the current prose, tables, and five existing book figures.
- Verified reuse terms from each official arXiv record. An arXiv non-exclusive distribution license was treated as **not** granting downstream republication rights.
- Selected no figure merely to satisfy a count. A figure was retained only when it added information that prose or a compact table conveyed less clearly.

During the audit, `wang2026compound` was found to point to unrelated communications paper arXiv:2606.01455. The bibliography and source bundle were corrected to *Do Agent Optimizers Compound?*, arXiv:2607.14004, before the final decision below.

## Retained figures

| Chapter | Paper and figure | File | Decision rationale | Rights and modifications |
|---|---|---|---|---|
| 編集対象 | ExpeL Figure 1 | `images/expel-persistent-memory.png` | Shows the otherwise hard-to-express distinction between offline insight extraction, experience retrieval, and reuse on later tasks. | CC BY 4.0; original PNG rescaled by the browser only. |
| 探索と進化 | DGM Figure 3 | `images/dgm-archive-progress.png` | Connects the branching archive to the non-monotone lineage that reaches the final best agent; this is more informative than another generic optimizer loop. | CC BY 4.0; the two source panels were rasterized, combined in the paper's original left-to-right arrangement, and whitespace-cropped. |
| Optimizerの独立評価 | HarnessOpt-Bench Figure 1 | `images/harnessopt-heldout-architecture.png` | Makes the trusted boundary concrete: editable agent code, development traces, aggregate validation feedback, sealed test, metered model calls, and isolated execution. | CC BY 4.0; source PDF rasterized without cropping or content changes. |

## Per-paper decisions

| arXiv / key | Strongest inspected candidates | Decision | Reason |
|---|---|---|---|
| 2211.01910 / `zhou2023ape` | Figures 7 and 17: search budget and cross-model transfer | Reject / rights hold | Both are informative, but the arXiv record grants only the non-exclusive distribution license. Their claims are already stated with text and equations. |
| 2309.03409 / `yang2024opro` | Figures 11 and 12: train/validation curves and OPRO–EvoPrompt comparison | Reject | CC0 permits reuse, but Figure 11 covers only two settings and Figure 12 is method-specific. Neither adds enough beyond the held-out and controlled-comparison discussion. |
| 2309.08532 / `guo2024evoprompt` | Figure 2: LLM implementation of differential evolution | Reject / rights hold | Mechanistically useful but overlaps the search-operator taxonomy; the arXiv license is not a reuse grant. |
| 2507.19457 / `agrawal2026gepa` | Figures 1, 3, 16, and 17: efficiency, optimizer loop, validation gap, deployed prompt size | Reject / rights hold | Strong candidates, but only the arXiv non-exclusive distribution license was available. The book retains the claims in prose and tables rather than reproducing the figures. |
| 2410.10762 / `zhang2025aflow` | Figures 2 and 3 | Reject / rights hold | The useful figures duplicate the existing `aflow-mcts.png` and `aflow-pareto.png`; the arXiv record also lacks a downstream reuse license. |
| 2408.08435 / `hu2025adas` | Figure 1: archive-driven Meta Agent Search | Reject | CC BY 4.0 permits reuse, but the loop is generic and overlaps the retained DGM archive figure. |
| 2410.06153 / `shang2025agentsquare` | Figures 2 and 3: modular search and recombination | Reject | CC BY 4.0 permits reuse, but the panels are dense at book width and repeat the module/evolution table. |
| 2308.10144 / `zhao2024expel` | Figure 1: experiential learning pipeline | **Keep** | Unique visual account of persistent cross-task experience and insight reuse. |
| 2303.11366 / `shinn2023reflexion` | Figure 2: Reflexion loop | Reject as duplicate | CC BY 4.0 permits reuse, but `reflexion-loop.png` already covers the same mechanism in Part I. |
| 2504.15257 / `gao2025flowreasoner` | Boundary/training diagrams | Reject | Query-local workflow generation is a scope-boundary example rather than a persistent-artifact core method; no downstream reuse license was verified. |
| 2505.22954 / `zhang2026dgm` | Figures 3, 4, and appendix Figure 6 | **Keep Figure 3 only** | Figure 3 uniquely links archive branching to improvement lineage. Figure 4 would overrepresent one paper, and Figure 6 is an implementation detail. |
| 2603.28052 / `lee2026metaharness` | Figures 2, 3, and appendix Figure 7 | Reject | CC BY 4.0 permits reuse, but these recent-preprint diagrams largely repeat the edit-surface and failure-feedback prose. |
| 2608.02276 / `shao2026harnessr1` | Figures 2, 3, and 4(b) | Reject as duplicate | CC BY 4.0 permits reuse, but existing `harness-r1-first-error.png` and `harness-r1-heldout.png` already carry the relevant mechanism and evaluation claims. |
| 2507.21046 / `gao2026selfevolving` | Survey taxonomy figures | Reject | CC BY 4.0 permits reuse, but the dense overview is broader than this book's scope and duplicates its taxonomy tables. |
| 2603.22386 / `yue2026workflow` | Survey workflow taxonomy | Reject / rights hold | Generic overview with no unique split, transfer, regression, cost, or safety evidence; only the non-exclusive distribution license was verified. |
| 2402.07927 / `sahoo2024promptengineering` | Prompt-engineering survey overview | Reject | CC BY 4.0 permits reuse, but the broad taxonomy adds no information beyond the prompt-edit discussion. |
| 2607.12227 / `wang2026rethinking` | Matched-budget framework and held-out comparison | Reject | CC BY 4.0 permits reuse, but this recent preprint's protocol is already summarized in the evaluation tables, and HarnessOpt Figure 1 gives a clearer trusted-boundary diagram. |
| 2605.22505 / `tong2026priority` | Priority-ranking versus optimizer-performance correlation | Reject | CC BY-NC-ND 4.0 does not permit adaptation; the plot is also a diagnostic from a work in progress rather than a general benchmark design. |
| 2608.06301 / `ursekar2026harnessopt` | Figure 1 and cost/gain plots | **Keep Figure 1 only** | Figure 1 directly visualizes the sealed evaluation contract. The result plots are recent, task-specific, and unnecessary for the book's protocol argument. |
| 2310.11324 / `sclar2024spurious` | Model-ranking reversal and prompt-format spread | Reject | CC BY 4.0 permits reuse, but the main plot has a difficult conditional-probability axis and is not self-explanatory at normal reading speed. |
| 2404.13076 / `panickssery2024selfpreference` | Self-recognition versus self-preference correlation | Reject | CC BY 4.0 permits reuse, but the evaluator-bias claim is clearer in prose and the plot would introduce model-specific detail without changing the recommendation. |
| 2406.13352 / `debenedetti2024agentdojo` | Utility versus attack-success Pareto comparison | Reject / rights hold | Directly relevant to safety, but the arXiv record provides only the non-exclusive distribution license. The book retains the separate utility/safety requirement in prose. |
| 2607.14004 / `wang2026compound` | Four phase-wise pass-rate bar charts | Reject / rights hold | The corrected source has simple task-specific bars that are compactly summarized in prose. The arXiv record provides only the non-exclusive distribution license. |

## Chapter-level completion

| Chapter | Sources inspected | Final decision |
|---|---|---|
| Index | Three survey source bundles and current cover figures | No new figure; survey taxonomies are broader and denser than the book's scoped outline. |
| 最適化対象 | Reflexion, DGM, Harness-R1 | Retain existing Part I figures; no additional figure. |
| 探索空間 | AFlow, ADAS, DGM | Retain existing AFlow/DGM figures; no duplicate. |
| 失敗から Harness を改善する | Reflexion, GEPA, Harness-R1 | Retain existing first-error figure; GEPA is on rights hold. |
| 改善の評価 | AFlow, GEPA, DGM, Harness-R1 | Retain existing held-out/Pareto figures; no additional result grid. |
| 最適化ループ | APE, OPRO, GEPA, ADAS, AgentSquare, surveys | No new figure; role decomposition and update loop are clearer in the chapter's table/equations. |
| 編集対象 | ExpeL, Reflexion, AgentSquare, ADAS, DGM, Meta-Harness, Harness-R1 | Add ExpeL Figure 1 only. |
| 実行結果と失敗分析 | OPRO, GEPA, ExpeL, Meta-Harness, Harness-R1 | No new figure; existing first-error evidence and the feedback table are sufficient. |
| 探索と進化 | APE, OPRO, EvoPrompt, GEPA, AFlow, ADAS, AgentSquare, DGM | Add DGM Figure 3 only. |
| Editor と学習型 Optimizer | FlowReasoner, Harness-R1, Priority Ranking | No new figure; boundary and learned-editor distinctions are clearer in the chapter's tables. |
| タスク分割 | OPRO, Harness-R1, Rethinking Evaluation, HarnessOpt-Bench | No additional figure; the HarnessOpt architecture is used once in the independent-optimizer-evaluation chapter. |
| Target・Environment 間の汎化 | APE, OPRO, ADAS, AgentSquare, DGM, Harness-R1, Sclar | No new figure; candidate plots were either on rights hold, too dense, or duplicative. |
| 回帰・コスト・安全性 | GEPA, AFlow, AgentSquare, DGM, Harness-R1, self-preference, AgentDojo, Do Agent Optimizers Compound? | No new figure; safety candidate is on rights hold and phase results are clearer in prose. |
| Optimizerの独立評価 | Rethinking Evaluation, Priority Ranking, HarnessOpt-Bench, Sclar | Add HarnessOpt-Bench Figure 1 only; retain explicit preprint caveat in surrounding text. |
