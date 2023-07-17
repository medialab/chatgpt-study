import subprocess
from pathlib import Path

from tqdm import tqdm

from constants import ANNOTATORS, DATA_DIR, JAR_FILE_LOCATION


class CLI:
    java_command = [
        "java",
        "-cp",
        JAR_FILE_LOCATION,
        "edu.stanford.nlp.pipeline.StanfordCoreNLP",
    ]
    annotator_option = ["-annotators", ANNOTATORS]
    output_format_option = ["-outputFormat", "xml"]
    properties_option = ["-props", "cleanxml.properties"]

    def __init__(self, day_dir: Path) -> None:
        output_dir = str(day_dir.joinpath("corenlp-output").absolute())
        file_list = str(day_dir.joinpath("file_list.txt").absolute())
        self.script = (
            self.java_command
            + self.annotator_option
            + self.output_format_option
            + self.properties_option
            + ["-outputDirectory", output_dir]
            + ["-fileList", file_list]
        )


def main():
    days = len([_ for _ in DATA_DIR.iterdir()])
    for day_dir in tqdm(DATA_DIR.iterdir(), total=days):
        script = CLI(day_dir=day_dir).script
        try:
            subprocess.run(script, capture_output=True, timeout=1200)
        except Exception as e:
            raise e


if __name__ == "__main__":
    main()
