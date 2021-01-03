#!/usr/bin/env python3
# pylint: disable=invalid-name

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

parser = argparse.ArgumentParser(description="Normalise a podcast file.")
parser.add_argument("--noise-start", dest="noise_start", default="00:00:00", help="noise sample start")
parser.add_argument("--noise-length", dest="noise_length", default="00:00:01", help="noise sample length")
parser.add_argument("--noise-level", dest="noise_level", type=float, default=0.21, help="noise level")
parser.add_argument("--i", dest="target_i", type=float, default=-16.0, help="target I")  # -24.0
parser.add_argument("--tp", dest="target_tp", type=float, default=-1.5, help="target TP")  # -2.0
parser.add_argument("--lra", dest="target_lra", type=float, default=11.0, help="target LRA")
parser.add_argument("--bit-rate", dest="bit_rate", default="24k", help="output audio bitrate")
parser.add_argument("--sample-rate", dest="sample_rate", type=int, default=22050, help="output audio sample rate")
parser.add_argument("--genre", dest="genre", default="Podcast")
parser.add_argument("--collection", dest="collection", default="The Point Church Sermons")
parser.add_argument("--date", dest="date", default=str(time.localtime().tm_year))
parser.add_argument("--title", dest="title")
parser.add_argument("--speaker", dest="speaker")
parser.add_argument("input_file")
parser.add_argument("output_file")
args = parser.parse_args()


sys.stdout.write("Analysing noise ...")
sys.stdout.flush()
_, noise_profile = tempfile.mkstemp()
ffmpeg = subprocess.Popen(
    (
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-y",
        "-i",
        args.input_file,
        "-ss",
        args.noise_start,
        "-t",
        args.noise_length,
        "-f",
        "aiff",
        "-",
    ),
    stdout=subprocess.PIPE,
)
sox = subprocess.Popen(("sox", "-q", "-t", "aiff", "-", "-n", "noiseprof", noise_profile,), stdin=ffmpeg.stdout,)
sox.communicate()
print(" done")


sox_cmd = (
    "sox",
    "-q",
    args.input_file,
    "-t",
    "aiff",
    "-",
    "noisered",
    noise_profile,
    str(args.noise_level),
)
sys.stdout.write("Analysing loudness ...")
sys.stdout.flush()
sox = subprocess.Popen(sox_cmd, stdout=subprocess.PIPE)
ffmpeg = subprocess.Popen(
    (
        "ffmpeg",
        "-hide_banner",
        "-nostdin",
        "-y",
        "-i",
        args.input_file,
        "-af",
        (
            "loudnorm=linear=true:"
            "dual_mono=true:"
            "I={target_i}:"
            "TP={target_tp}:"
            "LRA={target_lra}:"
            "print_format=json"
        ).format(target_i=args.target_i, target_lra=args.target_lra, target_tp=args.target_tp),
        "-f",
        "null",
        "-",
    ),
    stdin=sox.stdout,
    stderr=subprocess.PIPE,
)
_, loudness_stats = ffmpeg.communicate()
print(" done")
stats = json.loads(b"".join(loudness_stats.splitlines()[-12:]).decode())

metadata = [
    "-metadata",
    "album=%s" % args.collection,
    "-metadata",
    "genre=%s" % args.genre,
    "-metadata",
    "date=%s" % args.date,
]
if args.title:
    metadata += ["-metadata", "title=%s" % args.title]
if args.speaker:
    metadata += ["-metadata", "artist=%s" % args.speaker]

codec = {"mp3": "libmp3lame", "m4a": "libfdk_aac"}[args.output_file.split(".")[-1]]

sox = subprocess.Popen(sox_cmd, stdout=subprocess.PIPE)
ffmpeg = subprocess.Popen(
    [
        "ffmpeg",
        "-hide_banner",
        "-nostdin",
        "-y",
        "-i",
        "-",
        "-ac",
        "1",
        "-c:a",
        codec,
        "-b:a",
        args.bit_rate,
        "-ar",
        str(args.sample_rate),
        "-af",
        (
            "loudnorm=linear=true:"
            "dual_mono=true:"
            "I={target_i}:"
            "TP={target_tp}:"
            "LRA={target_lra}:"
            "offset={target_offset}:"
            "measured_I={input_i}:"
            "measured_LRA={input_lra}:"
            "measured_tp={input_tp}:"
            "measured_thresh={input_thresh}"
        ).format(target_i=args.target_i, target_lra=args.target_lra, target_tp=args.target_tp, **stats),
    ]
    + metadata
    + [args.output_file],
    stdin=sox.stdout,
)
ffmpeg.communicate()

os.unlink(noise_profile)
