import pymupdf
import os
import yaml
import argparse


def main(filename, days_period, articles_per_day):
    doc = pymupdf.open(filename)  # or pymupdf.Document(filename)
    toc = doc.get_toc()
    chapters = [
        [item[2], item[1]] for item in toc if item[0] == 1
    ]  # [[page, name], [page, name], ...]
    print(chapters)

    output_dir = "feeds/" + os.path.splitext(filename)[0]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    chapter_list = ""
    # Iterate through the chapters and save each one as a separate PDF
    for i, (page, title) in enumerate(chapters):
        new_doc = pymupdf.open()
        final_page = chapters[i + 1][0] - 2 if i + 1 < len(chapters) else -1
        new_doc.insert_pdf(doc, from_page=page - 1, to_page=final_page)

        new_doc.save(f"{output_dir}/{title}.pdf")
        new_doc.close()
        print(f"Saved chapter '{title}'")
        chapter_list += title + ".pdf\n"

    with open(f"{output_dir}/unread_chapters.txt", "w") as f:
        f.write(chapter_list)

    with open(f"{output_dir}/read_chapters.txt", "w") as f:
        pass  # just make an empty file

    print(
        f"done. Saved {len(chapters)} chapters to {output_dir}. their list is saved as unread_chapters.txt"
    )

    with open(f"{output_dir}/config.yaml", "w") as f:
        yaml.dump({"days_period": days_period, "articles_per_day": articles_per_day}, f)

    doc.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process a PDF file and split it into chapters."
    )
    parser.add_argument("filename", type=str, help="The PDF file name to process")
    parser.add_argument(
        "--days_period",
        type=int,
        default=1,
        help="Number of days between chapter additions (default: 1)",
    )
    parser.add_argument(
        "--articles_per_day",
        type=int,
        default=1,
        help="Number of articles to receive simultaneously (default: 1)",
    )

    args = parser.parse_args()

    main(args.filename, args.days_period, args.articles_per_day)
