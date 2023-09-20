# *winterreise_rt*: a subset of Schubert Winterreise Dataset(SWD) for real-time lyrics alignment

## About
*winterreise_rt* is a subset of the [Schubert Winterreise Dataset (SWD)](https://zenodo.org/record/4122060) [1] for the purpose of real-time lyrics alignment.
The Schubert Winterreise Dataset(SWD) dataset is a collection of resources of Schubert’s song cycle for voice and piano ‘Winterreise’, one of the most-performed pieces within the classical music repertoire.
It includes symbolic scores, lyrics, midi, and nine audio recordings, two of which are publicly accessible. 
While the SWD dataset is structured for evaluating tasks such as automated music transcription or musicological structure analysis, it also provides excellent data for evaluating real-time music alignment tasks.
The dataset provides different performance versions of the same song by different singers along with annotations.
We cast the Schubert Winterreise Dataset(SWD) into *winterreise_rt*, a subset that enables the benchmark evaluation of real-time lyrics alignment models.
While the original dataset used the singer's name as the identifier for each performance version, we used *ref* (as a reference audio) and *target* (as a target audio) as identifiers.

## Dataset

This repo contains the code for reconstructing *winterreise_rt* from the original SWD dataset.
The main adjustments are the following:

- Out of the two publicly available versions of the recording, we renamed *HU33* as the *ref*, *SC06* as the *target*.
- When the key of the *ref* and *target* audio was mismatched, the *target* audio was transposed to match the *ref*. 
- The loudness was also normalized based on the maximum RMS value of the *ref* audio. 
- Only vocal notes were retained from the original note annotations and the rest were filtered out to evaluate timing of each note mapped to lyrics.

Data including the musicxml, midi, and lyrics are still included in the *winterreise_rt* dataset, although they may not directly used for the evaluating the real-time lyrics alignment model.

## Additional Data [(Download Link)](https://github.com/laurenceyoon/winterreise_rt/releases/tag/0.0.1)

Based on our proposed system of real-time lyrics alignment, we also provide the following additional data:

- *score* audio: MIDI-synthesized audio from the musicxml score.
- *score* annotation: Voice note-level annotation of the *score* audio.

These data are optional for evaluating real-time lyrics alignment models in general but may play a supporting role depending on the implementation and application. 
In particular, they may be helpful if the real-time lyrics alignment model borrows from a method from real-time audio-to-score alignment, or *score following*.

---

## Environment Setting

Tested on Python 3.10 & Mamaforge

```bash
# if you have mamba installed
$ mamba env create -f environment.yml

# if you have conda installed
$ conda env create -f environment.yml

# activate the environment
$ mamba activate wrt  # or conda activate wrt
```

## Usage

```bash
# download the winterreise dataset (v2.0)
$ wget "https://zenodo.org/record/5139893/files/Schubert_Winterreise_Dataset_v2-0.zip?download=1" -O winterreise.zip
$ unzip winterreise -d winterreise
$ rm -r winterreise.zip

# reconstruct the winterreise_rt dataset
$ python reconstruct.py --src ./winterreise --dest ./winterreise_rt
```

## References

[1] Weiß, Christof, Frank Zalkow, Vlora Arifi-Müller, Meinard Müller, Hendrik Vincent Koops, Anja Volk, and Harald G. Grohganz. "Schubert Winterreise dataset: A multimodal scenario for music analysis." Journal on Computing and Cultural Heritage (JOCCH) 14, no. 2 (2021): 1-18.

## Acknowledgement

The tutorial code of this repository is mainly referenced from [Synctoolbox](https://github.com/meinardmueller/synctoolbox).
