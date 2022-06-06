import sys, os, argparse
from gpt2_zeroshot import main

sys.path.append(os.getcwd())

parser = argparse.ArgumentParser()

parser.add_argument("--GPT2_MODEL", type=str, default='skt/kogpt2-base-v2',
                    choices=['skt/kogpt2-base-v2', "conceptnet"])
parser.add_argument("--OUTPUT_TYPE", type=str, defautl = 'xlsx',
                   choices=['csv', 'xlsx', 'jsonl'])

parser.add_argument("--DATA_PATH", type=str)
parser.add_argument("--OUTPUT_DIR", type=str, default = './output/')
parser.add_argument("--OUTPUT_LEN", type=int, default = 3)
parser.add_argument("--SEED", type=int, default = 42)
parser.add_argument("--STOP_TOKEN", type=str, default = ".")

parser.add_argument("--TOP_K", type=int, default = 1)
parser.add_argument("--TOP_P", type=int, default = 0.9)
parser.add_argument("--NUM_BEAMS", type=int, default = 10)
parser.add_argument("--NUM_SEQUENCES", type=int, default = 10)

args = parser.parse_args()

main(args)
