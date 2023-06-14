from typing import List
from arxiv import Search, SortCriterion, Result
from typing import Union
from pathlib import Path
from tqdm.auto import tqdm
import fitz  # from PyMuPDF
import re
import requests
from loguru import logger
import requests
from typing import List


def search_arxiv(query: str, max_results: int) -> List[Result]:
    """
    Search the arXiv API for papers based on a given query string and return a list of Result objects.

    Parameters:
    query (str): The query string to search for in the arXiv database.
    max_results (int): The maximum number of results to return.

    Returns:
    List[Result]: A list of Result objects representing the search results.
    """
    search = Search(
        query=query, max_results=max_results, sort_by=SortCriterion.SubmittedDate
    )

    return list(search.results())


def download_and_scan_papers(
    results: List[Result],
    directory: Union[str, Path],
    trigger_archive: bool = True,
) -> None:
    """
    Download the PDFs of papers from a list of Result objects to a specified directory
    and scan each PDF for links to GitHub repositories.

    Parameters:
    results (List[Result]): The list of Result objects whose PDFs are to be downloaded.
    directory (Union[str, Path]): The directory where the PDFs are to be saved.
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)

    github_url_pattern = re.compile(r"https?://github\.com/[^\s,]+")

    for result in tqdm(results, disable=True):
        file_path = dir_path / f"{result.entry_id.split('/')[-1]}.pdf"
        if not file_path.exists():
            result.download_pdf(filename=str(file_path))

        # Open the PDF file
        doc = fitz.open(file_path)

        print()
        logger.info(f"Paper: {result.title}")
        logger.info(f"arXiv ID: {result.entry_id.split('/')[-1]}")

        # Iterate over each page and extract the text
        for page in doc:
            text = page.get_text()
            github_urls = github_url_pattern.findall(text)

            # If GitHub URLs are found, print the paper info and the URLs
            if github_urls:
                logger.info("GitHub URLs found:")
                for url in github_urls:
                    if trigger_archive:
                        archive_urls([url])
                        logger.info(f"  (archive triggered)")
                    else:
                        logger.info(url)
                print()


import requests
from typing import List


def archive_urls(urls: List[str]) -> None:
    """
    Trigger the Wayback Machine to archive a list of URLs.

    Parameters:
    urls (List[str]): The list of URLs to be archived.
    """
    for url in urls:
        response = requests.get(f"http://archive.org/wayback/available?url={url}")
        data = response.json()

        if data.get("archived_snapshots"):
            print(f"The URL {url} is already archived.")
            print(f"Archived URL: {data['archived_snapshots']['closest']['url']}")
        else:
            print(f"The URL {url} is not yet archived. Archiving now...")
            save_response = requests.post(
                f"https://web.archive.org/save/{url}",
                data={"url": url, "capture_all": "on"},
            )
            if save_response.status_code == 200:
                print(f"Successfully archived {url}")
            else:
                print(
                    f"Failed to archive {url}. Status code: {save_response.status_code}"
                )


if __name__ == "__main__":
    keyword: str = "open-source"
    limit: int = 10
    config_trigger_archive: bool = True

    # --
    search_results = search_arxiv(keyword, limit)
    for result in search_results:
        logger.info(result.entry_id)
    download_and_scan_papers(search_results, "./pdfs", config_trigger_archive)
    logger.info("done")
