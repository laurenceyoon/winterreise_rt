# winterreise_rt: A subset of Schubert Winterreise Dataset(SWD) for real-time lyrics alignment

## About
*winterreise_rt* is a subset of the [Schubert Winterreise Dataset (SWD)](https://zenodo.org/record/4122060) [1] for the purpose of real-time lyrics alignment.
The Schubert Winterreise Dataset(SWD) dataset is a collection of resources of Schubert’s song cycle for voice and piano ‘Winterreise’, one of the most-performed pieces within the classical music repertoire.
It includes symbolic scores, lyrics, midi, and nine audio recordings, two of which are publicly accessible. 
While the SWD dataset is structured for evaluating tasks such as automated music transcription or musicological structure analysis, it also provides excellent data for evaluating real-time music alignment tasks.
The dataset provides different performance versions of the same song by different singers along with annotations.
We cast the Schubert Winterreise Dataset(SWD) into *winterreise_rt*, a subset that enables the benchmark evaluation of real-time lyrics alignment models.

## Dataset

This repo contains the code for reconstructing *winterreise_rt* from the original SWD dataset.
The main adjustments are the following:

- Out of the two publicly available versions of the recording, we renamed *HU33* as the *ref*, *SC06* as the *target*.
- When the key of the *ref* and *target* audio was mismatched, the *target* audio was transposed to match the *ref*. 
- The loudness was also normalized based on the maximum RMS value of the *ref* audio. 
- Only vocal notes were retained from the original note annotations and the rest were filtered out to evaluate timing of each note mapped to lyrics.

Data including the musicxml, midi, and lyrics are still included in the *winterreise_rt* dataset, although they may not directly used for the evaluating the real-time lyrics alignment model.

## Additional Data

Based on our proposed system of real-time lyrics alignment, we also provide the following additional data:

- *score* audio: MIDI-synthesized audio from the musicxml score.
- *score* annotation: Voice note-level annotation of the *score* audio.

## References

[1] Weiß, Christof, Frank Zalkow, Vlora Arifi-Müller, Meinard Müller, Hendrik Vincent Koops, Anja Volk, and Harald G. Grohganz. "Schubert Winterreise dataset: A multimodal scenario for music analysis." Journal on Computing and Cultural Heritage (JOCCH) 14, no. 2 (2021): 1-18.

## Acknowledgement

The tutorial code of this repository is mainly referenced from [Synctoolbox](https://github.com/meinardmueller/synctoolbox).
