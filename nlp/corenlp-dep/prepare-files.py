import xml.etree.cElementTree as ET

import casanova
from tqdm import tqdm

from constants import DATA, DATA_DIR, INPUT_DIR_NAME


def main():
    print("counting file length...")
    file_length = casanova.reader.count(DATA)
    with open(DATA, "r") as f:
        reader = casanova.reader(f)
        id_pos = reader.headers.id
        date_pos = reader.headers.local_time
        text_pos = reader.headers.text
        for row in tqdm(reader, total=file_length, desc="Parsing files..."):
            tweet_id = row[id_pos]
            date = row[date_pos]
            text = row[text_pos]

            # Make tweet's YMD directory
            outdir = parse_date(date)
            # Make tweet's output file path
            outfile = outdir.joinpath(f"{tweet_id}.xml")

            # Write tweet XML file
            doc = ET.Element("doc", attrib={"id": tweet_id})
            b = ET.SubElement(doc, "p")
            b.text = text
            tree = ET.ElementTree(doc)
            tree.write(outfile)

    for day_dir in DATA_DIR.iterdir():
        input_dir = day_dir.joinpath(INPUT_DIR_NAME)
        files = [str(f.absolute()) for f in input_dir.iterdir()]
        outfile = day_dir.joinpath("file_list.txt")
        with open(outfile, "w") as of:
            of.writelines(files)


def parse_date(date: str):
    ymd = date.split("T")[0]
    day_dir = DATA_DIR.joinpath(ymd)
    if not day_dir.is_dir():
        day_dir.mkdir(parents=True)
    outdir = day_dir.joinpath(INPUT_DIR_NAME)
    outdir.mkdir(exist_ok=True)
    return outdir


if __name__ == "__main__":
    main()
