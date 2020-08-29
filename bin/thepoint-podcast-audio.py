#!/usr/bin/env python3
# pylint: disable=invalid-name

import argparse
import json
import subprocess
import sys
import time

parser = argparse.ArgumentParser(description="Normalise a podcast file.")
parser.add_argument("--low-pass", dest="low_pass", type=int, default=3000, help="low pass level")
parser.add_argument("--high-pass", dest="high_pass", type=int, default=200, help="high pass level")
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


sys.stdout.write("Analysing loudness ...")
sys.stdout.flush()
p = subprocess.run(
    (
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i",
        args.input_file,
        "-af",
        ("loudnorm=I={target_i}:" "TP={target_tp}:" "LRA={target_lra}:" "print_format=json").format(
            target_i=args.target_i, target_lra=args.target_lra, target_tp=args.target_tp
        ),
        "-f",
        "null",
        "-",
    ),
    stderr=subprocess.PIPE,
    check=True,
)
print(" done")
stats = json.loads(b"".join(p.stderr.splitlines()[-12:]).decode())
stats["lowpass"] = args.low_pass
stats["highpass"] = args.high_pass

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

subprocess.run(
    [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i",
        args.input_file,
        "-ac",
        "1",
        "-c:a",
        "libmp3lame",
        "-b:a",
        args.bit_rate,
        "-ar",
        str(args.sample_rate),
        "-af",
        (
            "loudnorm=linear=true:"
            "measured_I={input_i}:"
            "measured_LRA={input_lra}:"
            "measured_tp={input_tp}:"
            "measured_thresh={input_thresh},"
            "lowpass={lowpass},"
            "highpass={highpass}"
        ).format(**stats),
    ]
    + metadata
    + [args.output_file],
    check=False,
)
