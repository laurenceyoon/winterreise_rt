import argparse
import csv
import shutil
from collections import defaultdict
from pathlib import Path

import librosa
import soundfile as sf
from tqdm import tqdm

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

# Audio parameters
SAMPLE_RATE = 16000
HOP_LENGTH = 640  # 40ms


def make_empty_directory(dest_dir):
    (dest_dir / AUDIO_DIR).mkdir(parents=True, exist_ok=True)
    (dest_dir / SCORE_DIR).mkdir(parents=True, exist_ok=True)
    (dest_dir / LYRICS_DIR).mkdir(parents=True, exist_ok=True)
    (dest_dir / NOTE_ANN_DIR).mkdir(parents=True, exist_ok=True)
    (dest_dir / AUDIO_KEY_ANN_DIR).mkdir(parents=True, exist_ok=True)


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
def filter_voice_note_ann(src_dir, dest_dir):
    print("Filtering voice note annotation...")
    for song_id in tqdm(SONG_IDS):
        for singer, role in SINGERS.items():
            annots = []
            source_file = (
                src_dir / NOTE_ANN_DIR / f"{FILENAME_PREFIX}{song_id}_{singer}.csv"
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
                dest_dir / NOTE_ANN_DIR / f"ann_{FILENAME_PREFIX}{song_id}_{role}.csv"
            )
            with open(out_file.as_posix(), "w") as file:
                fieldnames = ["start", "pitch", "pitchclass", "instrument"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(annots)


def get_semitone_difference(key1, key2):
    midi_num1 = librosa.note_to_midi(key1.split(":")[0])
    midi_num2 = librosa.note_to_midi(key2.split(":")[0])
    return midi_num1 - midi_num2


def transpose_audio_keys(dest_dir):
    # Read the CSV file & filter out the ref & target rows
    audio_key_info = {}
    key_ann_csv_file = dest_dir / AUDIO_KEY_ANN_DIR / "ann_audio_globalkey-tuning.csv"
    with open(key_ann_csv_file, mode="r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        for row in reader:
            song_id = row["WorkID"][-2:]
            if row["PerformanceID"] == "HU33":
                if song_id not in audio_key_info.keys():
                    audio_key_info[song_id] = {"ref": {}, "target": {}}
                audio_key_info[song_id]["ref"] = row
            elif row["PerformanceID"] == "SC06":
                if song_id not in audio_key_info.keys():
                    audio_key_info[song_id] = {"ref": {}, "target": {}}
                audio_key_info[song_id]["target"] = row

    # transpose target audio keys to ref audio key
    print("\nTransposing target audio keys to ref audio key...")
    for song_id in tqdm(SONG_IDS):
        target_audio = dest_dir / AUDIO_DIR / f"{FILENAME_PREFIX}{song_id}_target.wav"
        target_y, _ = librosa.load(target_audio.as_posix(), sr=SAMPLE_RATE)
        ref_info, target_info = (
            audio_key_info[song_id]["ref"],
            audio_key_info[song_id]["target"],
        )
        semitone_diff = get_semitone_difference(ref_info["Key"], target_info["Key"])
        print(
            f"[{song_id}] semitone_diff: {semitone_diff}, ref_info: {ref_info}, target_info: {target_info}"
        )

        # Transpose the target audio
        y_transposed = librosa.effects.pitch_shift(
            target_y, sr=SAMPLE_RATE, n_steps=semitone_diff
        )

        # Save the transposed audio
        sf.write(target_audio.as_posix(), y_transposed, SAMPLE_RATE)


def normalize_audio_rms(dest_dir):
    print(f"\nNormalizing audio RMS...")
    for song_id in tqdm(SONG_IDS):
        # load audio files
        ref_audio_path = dest_dir / AUDIO_DIR / f"{FILENAME_PREFIX}{song_id}_ref.wav"
        target_audio_path = (
            dest_dir / AUDIO_DIR / f"{FILENAME_PREFIX}{song_id}_target.wav"
        )
        audio_file1, _ = librosa.load(ref_audio_path.as_posix(), sr=SAMPLE_RATE)
        audio_file2, _ = librosa.load(target_audio_path.as_posix(), sr=SAMPLE_RATE)

        # calculate RMS values
        rms1 = librosa.feature.rms(
            y=audio_file1, frame_length=HOP_LENGTH * 2, hop_length=HOP_LENGTH
        )[0].max()
        rms2 = librosa.feature.rms(
            y=audio_file2, frame_length=HOP_LENGTH * 2, hop_length=HOP_LENGTH
        )[0].max()

        # normalize target audio file with ref audio file
        audio_file2_normalized = audio_file2 * (rms1 / rms2)

        # save normalized target audio file
        sf.write(
            target_audio_path.as_posix(), audio_file2_normalized, samplerate=SAMPLE_RATE
        )


def copy_from_orig_dataset(src_dir, dest_dir):
    copy_audio_wav(src_dir, dest_dir)
    copy_audio_key_ann(src_dir, dest_dir)
    copy_score_musicxml(src_dir, dest_dir)
    copy_lyrics_txt(src_dir, dest_dir)
    copy_voice_note_ann(src_dir, dest_dir)


def main(src_dir, dest_dir):
    make_empty_directory(dest_dir)
    copy_from_orig_dataset(src_dir, dest_dir)

    # filter only voice notes from the note annotation files
    filter_voice_note_ann(src_dir, dest_dir)

    # transpose target audio keys to ref audio key
    transpose_audio_keys(dest_dir)

    # Normalize the RMS of the audio files
    normalize_audio_rms(dest_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--src",
        type=str,
        default=SWD_PATH,
        help="Path to the original dataset directory",
    )
    parser.add_argument(
        "--dest",
        type=str,
        default=WINTERREISE_RT_PATH,
        help="Path to the reconstructed dataset directory",
    )
    args = parser.parse_args()
    print(args)

    main(Path(args.src), Path(args.dest))
