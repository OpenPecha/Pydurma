# README

## Project description

Pydurma is a fast and modular collation engine that:
- uses a very fast collation mechanism ([diff-match-patch](https://github.com/google/diff-match-patch) instead of [Needleman-Wunsch](https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm))
- makes it easy to define language-specific tokenization and normalization, necessary for languages like Tibetan
- keeps track of the character position in the original files (even XML files where markup is removed in normalization)
- has a configurable engine to select the best reading, based on reading frequency among versions, OCR confidence index, language-specific knowledge, etc.

It does not:
- use any non-tabular (graph) representation (à la CollateX)
- implement reajustments of alignment based on the distance between tokens (à la CollateX)
- detect [transpositions](http://multiversiondocs.blogspot.com/2008/10/transpositions.html)

It does not yet:
- use subword tokenizers à la [sentencepiece](https://github.com/google/sentencepiece), potentially more robust on dirty (OCR) data than those based on linguistic features (spaces punctuation, etc.)
- allow configurable token distance function based on language-specific knowledge (graphical distance, phonetic distance) to reajust alignment (à la CollateX' `near_match=True` option)
- implement STAR algorithm to find the best "base" between different editions
- have a clearly defined export format for the collated text or critical apparatus

We intend Pydurma to be used in large scale projects to automate:
- merging different OCR outputs of the same images, selecting the best version of each of them
- creating an edition that averages all other editions automatically

The name Pydurma is a combination of:
- *Python*
- *Pedurma* དཔེ་བསྡུར་མ།, Tibetan for critical or diplomatic edition

### Note on possible workflows based on Pydurma

While Pydurma can be used in a classical [Lachmann](https://en.wikipedia.org/wiki/Karl_Lachmann)ian critical edition process, its innovative design allows it to automate the process of variant selection.

Using this automated selection directly can easily be gasped at, but we want to defend this concept. The type of editions Pydurma can produce:
- are fully automatic and thus uncritical (*uncritical editions*?), but can be produced on a large scale (*industrial editions*?)
- do not try to reproduce one variant in particular as their base (in that sense are not *diplomatic editions*, perhaps *undiplomatic editions*?)
- are intended to be similar to the concept of *vulgate* ("a commonly accepted text or reading" [MW](https://www.merriam-webster.com/dictionary/vulgate))
- can be regenerated from different inputs (improved OCR, more versions, etc.) giving a different output, and are thus temporary (or at least, not meant to be definitive)
- optimize measurable linguistic soundness
- as a result, are a good base for an AI-ready corpus

A workflow using Pydurma can work on a very large scale with minimal human intervention, which we hope can be a game changer for under-resourced literary traditions like the Tibetan tradition.

## Pydurma workflow

Pydurma operates in three steps:

- Preprocessing
- Collation
- Variant Selection

Here is that process:

### Preprocessing

![image](https://user-images.githubusercontent.com/51434640/218644335-7b74e48e-649a-45e4-9441-b550b6e70825.png)

### Collation

![image](https://user-images.githubusercontent.com/51434640/218644409-14e73234-bdda-4ae6-aa15-6a9fce600889.png)

### Variant Selection

![image](https://user-images.githubusercontent.com/51434640/218644467-a2c487d5-8313-4940-b640-78bc2258e78c.png)

## Previous work:

### text alignment

- [text_alignment_tool](https://gitlab.com/sofer_mahir/text_alignment_tool)
- [CollateX](https://collatex.net/about/)
- [MEDITE](http://www-poleia.lip6.fr/~ganascia/Medite_Project)
- [Juxta](https://wiki.digitalclassicist.org/Juxta) ([sources](https://github.com/performant-software/juxta-service), uses [difflib](https://github.com/java-diff-utils/java-diff-utils))
- [hypercollate](https://github.com/HuygensING/hyper-collate)
- [helayo](https://github.com/chchch/sanskrit-alignment) ([paper](https://joss.theoj.org/papers/10.21105/joss.04022))
- [Versioning Machine](http://v-machine.org/)
- [nmergec](http://digitalvariants.blogspot.com/2014/05/merging-multi-version-texts-mark-2.html) ("en-merge-see")

### OCR merging

- [ocromore](https://github.com/UB-Mannheim/ocromore)
- This was also done by Oliver Hellwig apparently, research to be one

### See also

- [Sequence Alignment (Wikipedia)](https://en.wikipedia.org/wiki/Sequence_alignment)
- [MSA: Multiple Sequence Alignment (Wikipedia)](https://en.wikipedia.org/wiki/Multiple_sequence_alignment)
- [Smith–Waterman algorithm](https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm)
- [Needleman–Wunsch algorithm](https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm)
- [Spencer 2004](http://dx.doi.org/10.1007/s10579-004-8682-1): Spencer M., Howe and Christopher J., 2004. Collating Texts Using Progressive Multiple Alignment. Computers and the Humanities. 38/2004, 253–270.

## Need help?

- File an [issue](https://github.com/buda-base/Pydurma/issues/new)
- Join our [Discord](https://discord.com/invite/7GFpPFSTeA) and ask us there

## Terms of use

Pydurma is licensed under the [Apache license](/LICENSE.md).

## Acknowledgements and citation

Pydurma is a creation of:
- the [Buddhist Digital Resource Center](https://www.bdrc.io/)
- [OpenPecha](https://github.com/OpenPecha/)

The intended use of Pydurma at the Buddhist Digital Resource Center was presented at the *Digital Humanities Workshop & Symposium* organized in January 2023 at the University of Hamburg (see [summary of the symposium](https://www.kc-tbts.uni-hamburg.de/events/2023-01-14-dh-symposium-completed.html), slide selection available [here](https://drive.google.com/file/d/11WI8v-2mJVBqf2g5GOGCIIjwu1truISb/view?usp=sharing)).

```bibtex
@software{
  Roux_Pydurma_2023,
  author = {Roux, Elie AND Tenzin Kaldan},
  title = {{Pydurma}},
  url = {https://github.com/openpecha/pydurma},
  version = {0.1.0}
}
```

@software{Roux_Pydurma_2023,author = {Roux, Elie and },month = jan,title = {{Pydurma}},url = {https://github.com/openpecha/pydurma},version = {0.1.0},year = {2023}}