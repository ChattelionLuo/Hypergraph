import json
import argparse


def extract_player_links(input_path, output_path):
    unique_players = {}

    with open(input_path, "r", encoding="utf-8") as fin:
        for line in fin:
            data = json.loads(line)
            name1, link1 = data.get("player1_name", ""), data.get("player1_link", "")
            if name1 and link1 and link1 != "error":
                unique_players[name1] = link1
            name2, link2 = data.get("player2_name", ""), data.get("player2_link", "")
            if name2 and link2 and link2 != "error":
                unique_players[name2] = link2

    with open(output_path, "w", encoding="utf-8") as fout:
        for name, link in sorted(unique_players.items()):
            fout.write(
                json.dumps(
                    {"player_name": name, "player_link": link},
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(f"共提取{len(unique_players)}位独特球员，结果已保存为 {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract unique player links")
    parser.add_argument("--input", default="all_match_information.jsonl")
    parser.add_argument("--output", default="all_players_link.jsonl")
    args = parser.parse_args()
    extract_player_links(args.input, args.output)
