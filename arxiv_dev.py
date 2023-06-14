from typing import List
from arxiv import Search, SortCriterion, Result
from typing import Union
from pathlib import Path
from tqdm.auto import tqdm
import fitz  # from PyMuPDF
import re


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
    results: List[Result], directory: Union[str, Path]
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

    for result in tqdm(results):
        file_path = dir_path / f"{result.entry_id.split('/')[-1]}.pdf"
        result.download_pdf(filename=str(file_path))

        # Open the PDF file
        doc = fitz.open(file_path)

        # Iterate over each page and extract the text
        for page in doc:
            text = page.get_text()
            github_urls = github_url_pattern.findall(text)

            # If GitHub URLs are found, print the paper info and the URLs
            if github_urls:
                print(f"\nPaper: {result.title}")
                print(f"arXiv ID: {result.entry_id.split('/')[-1]}")
                print("GitHub URLs found:")
                for url in github_urls:
                    print(url)
                print()


if __name__ == "__main__":
    keyword: str = "quantum"
    limit: int = 10

    # --
    search_results = search_arxiv(keyword, limit)
    for result in search_results:
        print(result.entry_id)
    download_and_scan_papers(search_results, "./pdfs")
    print("done")
