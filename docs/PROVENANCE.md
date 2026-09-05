# Provenance, privacy and attribution

## Original work

The thesis is authored by **Jingfan Xin**, supervised by **Jiaxin Mao**, at the Gaoling School of Artificial Intelligence, Renmin University of China. Its cover records completion in May 2024. The public title is an English description of the original Chinese thesis topic, not a claim of a separately published paper or peer-reviewed acceptance.

The source archive contains thesis drafts, a final thesis, a personal implementation directory, experimental exports, related software projects and administrative/participant materials. The selected implementation comes from `code/mycode`. Other folders were not merged merely because they were stored beside it.

## Version selection

The extracted implementation directory was compared with the two `mycode.zip` snapshots. The later ZIP contains the same 33 Python paths as the extracted tree; three files differ: the corpus extractor and two main prompt libraries. The extracted versions were selected and fingerprinted. The earlier root-level ZIP contains an older, smaller set of scripts, including a prompt-module name not present in the later tree. It was inspected, not indiscriminately merged.

The public source selection omits the older `simulator2.py`, a scratch `test.py`, three utility files, cached bytecode, IDE files and notebook outputs. A crawler in the personal folder exactly matches the copy in the adjacent `WebAgentFSM` tree; it is excluded rather than presented as original thesis implementation. The third-party projects themselves are not redistributed.

## Source records

- [source-manifest.json](../source-manifest.json) records the selected Python paths, original and published SHA-256 fingerprints, sizes and publication changes.
- [evidence-manifest.json](../evidence-manifest.json) identifies the final thesis, four data/output versions and retained numeric evaluation artifacts using English labels and fingerprints.
- `T01` is the final thesis. Relevant locations include printed pages 7–10 for collection/data, 11–18 for methods, 20–21 for result tables and 35–36 for discussion.
- `D01` is the 737-query reference export; `D02` is the 713-query input; `D03` is the standard cleaned output; `D04` is the indexed reference-query export.
- `R` entries identify saved numeric evaluation files. Only derived aggregate scores/counts are published, not their record-level arrays.

Fingerprints provide version traceability. They do not validate authorship of every line, data-collection consent, modelling correctness or an end-to-end reproduction. Local source paths remain in a private index outside the repository.

## Publication changes made in September 2026

1. Replaced hardcoded credentials and the private API endpoint with environment-variable configuration. Old credentials were not tested or published.
2. Removed embedded demonstration-session literals, including background attributes and example response text whose disclosure status was not established.
3. Removed comments and standalone explanatory/example strings from the selected code, including disabled credentials, scratch material and copied reference prose. Added English source headers and external documentation instead.
4. Preserved executable Chinese task and prompt strings. Translating them would change the historical experimental input.
5. Added English documentation, machine-readable aggregate tables, an explicitly synthetic offline preview and tests. These additions are dated 2026 and are not backdated thesis work.

No original file on the external source drive was modified. No model checkpoints, packages or large archives were copied into this repository.

## Excluded from the public repository

Participant names, email addresses, student numbers, profile exports, query/session records, audio, transcripts, screen captures, collected page content, databases, signed pages, administrative forms, thesis binaries and third-party literature/project bundles are excluded. Embedded examples are also withheld, even if they contain no direct name, because demographic/background combinations and verbatim session content may still be identifying.

The synthetic fixture is entirely invented for the review utilities. It is not a de-identified participant and must not be used as research evidence. There is no implicit permission to redistribute the original dataset or third-party material merely because this curated repository is public.

## Research references and software attribution

- The thesis uses a ReAct-inspired representation of reasons, actions and observations. See [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629).
- Its probabilistic-query discussion references prior user-query simulation research, including Breuer, Fuhr and Schaer's [Validating Simulations of User Query Variants](https://arxiv.org/abs/2201.07620). The separate reference implementation stored in the archive is not claimed as Jingfan's project.
- Semantic evaluation uses [BERTScore](https://github.com/Tiiiger/bert_score), with credit to its authors; lexical evaluation uses [NLTK](https://www.nltk.org/api/nltk.translate.bleu_score.html) and jieba.
- The archived annotation platform, ReAct, RUS-toolkit, UserSimulation, WebAgentFSM, YuLan-Rec and SimIIR directories are contextual/reference materials, not bundled original contributions in this release.

No blanket open-source licence is assigned to the original research archive or third-party assets. This is a public research portfolio with an explicit disclosure boundary, not a re-licensing of everything in the source folder.
