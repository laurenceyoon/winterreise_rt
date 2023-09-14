import argparse
from pathlib import Path
import shutil
import os
from tqdm import tqdm
import csv

SWD_PATH = Path("./winterreise")
WINTERREISE_RT_PATH = Path("./winterreise_rt")
AUDIO_DIR = "01_RawData/audio_wav/"
SCORE_DIR = "01_RawData/score_musicxml/"
LYRICS_DIR = "01_RawData/lyrics_txt/"
NOTE_ANN_DIR = "02_Annotations/ann_audio_note/"
AUDIO_KEY_ANN_DIR = "03_ExtraMaterial/"
FILENAME_PREFIX = "Schubert_D911-"
SINGERS = {
    "HU33": "ref",
    "SC06": "target",
}  # singer_name: role
SONG_IDS = ["{:02d}".format(i) for i in range(1, 25)]  # 01 ~ 24


def make_empty_directory(dest_dir=WINTERREISE_RT_PATH):
    (dest_dir / AUDIO_DIR).mkdir(parents=True)
    (dest_dir / SCORE_DIR).mkdir(parents=True)
    (dest_dir / LYRICS_DIR).mkdir(parents=True)
    (dest_dir / NOTE_ANN_DIR).mkdir(parents=True)
    (dest_dir / AUDIO_KEY_ANN_DIR).mkdir(parents=True)


# Copy audio_wav, score_musicxml, lyrics_txt from Schubert_Winterreise_Dataset_v2-0 to winterreise_rt
def copy_audio_wav(src_dir, dest_dir):
    print("Copying audio_wav...")
    for song_id in tqdm(SONG_IDS):
        for singer, role in SINGERS.items():
            src_audio = src_dir / AUDIO_DIR / f"{FILENAME_PREFIX}{song_id}_{singer}.wav"
            dest_audio = dest_dir / AUDIO_DIR / f"{FILENAME_PREFIX}{song_id}_{role}.wav"
            shutil.copy(src_audio, dest_audio)


def copy_audio_key_ann(src_dir, dest_dir):
    print("Copying audio key annotation...")
    shutil.copy(
        src_dir / AUDIO_KEY_ANN_DIR / "ann_audio_globalkey-tuning.csv",
        dest_dir / AUDIO_KEY_ANN_DIR / "ann_audio_globalkey-tuning.csv",
    )


def copy_score_musicxml(src_dir, dest_dir):
    print("Copying score...")
    for song_id in tqdm(SONG_IDS):
        src_score = src_dir / SCORE_DIR / f"{FILENAME_PREFIX}{song_id}.xml"
        dest_score = dest_dir / SCORE_DIR / f"{FILENAME_PREFIX}{song_id}.xml"
        shutil.copy(src_score, dest_score)


def copy_lyrics_txt(src_dir, dest_dir):
    print("Copying lyrics...")
    for song_id in tqdm(SONG_IDS):
        src_lyrics = src_dir / LYRICS_DIR / f"{FILENAME_PREFIX}{song_id}.txt"
        dest_lyrics = dest_dir / LYRICS_DIR / f"{FILENAME_PREFIX}{song_id}.txt"
        shutil.copy(src_lyrics, dest_lyrics)


def copy_voice_note_ann(src_dir, dest_dir):
    print("Copying voice note annotation...")
    for song_id in tqdm(SONG_IDS):
        for singer, role in SINGERS.items():
            src_ann = (
                src_dir / NOTE_ANN_DIR / f"{FILENAME_PREFIX}{song_id}_{singer}.csv"
            )
            dest_ann = dest_dir / LYRICS_DIR / f"{FILENAME_PREFIX}{song_id}_{role}.txt"
            shutil.copy(src_ann, dest_ann)


# Filter out the non-voice notes from the note annotation files
def filter_voice_note_ann():
    print("Copying & filtering voice note annotation...")
    for song_id in tqdm(SONG_IDS):
        for singer, role in SINGERS.items():
            annots = []
            source_file = (
                SWD_PATH / NOTE_ANN_DIR / f"{FILENAME_PREFIX}{song_id}_{singer}.csv"
            )
            with open(source_file.as_posix()) as file:
                reader = csv.DictReader(file, delimiter=";")
                for row in reader:
                    start, pitch, pitchclass, instrument = (
                        row["start"],
                        row["pitch"],
                        row["pitchclass"],
                        row["instrument"],
                    )
                    if instrument != "voice":
                        continue
                    annots.append(
                        {
                            "start": start,
                            "pitch": pitch,
                            "pitchclass": pitchclass,
                            "instrument": instrument,
                        }
                    )
            out_file = (
                WINTERREISE_RT_PATH
                / NOTE_ANN_DIR
                / f"ann_{FILENAME_PREFIX}{song_id}_{role}.csv"
            )
            with open(out_file.as_posix(), "w") as file:
                fieldnames = ["start", "pitch", "pitchclass", "instrument"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(annots)


def copy_from_orig_dataset(src_dir, dest_dir):
    copy_audio_wav(src_dir, dest_dir)
    copy_audio_key_ann(src_dir, dest_dir)
    copy_score_musicxml(src_dir, dest_dir)
    copy_lyrics_txt(src_dir, dest_dir)
    copy_voice_note_ann(src_dir, dest_dir)


def main(src_dir, dest_dir):
    make_empty_directory(dest_dir)
    copy_from_orig_dataset(src_dir, dest_dir)
    filter_voice_note_ann()

    # TBD
    # transpose_audio_key()


if "__main__" == "__name__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--src_dir",
        type=str,
        default=SWD_PATH,
        help="Path to the original dataset directory",
    )
    parser.add_argument(
        "--dest_dir",
        type=str,
        default=WINTERREISE_RT_PATH,
        help="Path to the reconstructed dataset directory",
    )
    args = parser.parse_args()

    main(args.src_dir, args.dest_dir)
