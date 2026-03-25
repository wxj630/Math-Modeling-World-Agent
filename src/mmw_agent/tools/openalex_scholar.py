from __future__ import annotations

from typing import Any

import requests


class OpenAlexScholar:
    def __init__(self, email: str | None = None):
        self.base_url = "https://api.openalex.org"
        self.email = email

    def _get_request_url(self, endpoint: str) -> str:
        endpoint = endpoint[1:] if endpoint.startswith("/") else endpoint
        return f"{self.base_url}/{endpoint}"

    @staticmethod
    def _get_abstract_from_index(abstract_inverted_index: dict) -> str:
        if not abstract_inverted_index:
            return ""

        max_position = 0
        for positions in abstract_inverted_index.values():
            if positions and max(positions) > max_position:
                max_position = max(positions)

        words = [""] * (max_position + 1)
        for word, positions in abstract_inverted_index.items():
            for position in positions:
                words[position] = word
        return " ".join(words).strip()

    def search_papers(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        if not self.email:
            raise ValueError("OPENALEX_EMAIL is required for search_papers")

        base_url = self._get_request_url("works")
        params = {
            "search": query,
            "per_page": limit,
            "mailto": self.email,
            "select": "id,title,display_name,authorships,cited_by_count,doi,publication_year,biblio,abstract_inverted_index",
        }
        headers = {"User-Agent": f"OpenAlexScholar/1.0 (mailto:{self.email})"}

        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        results = response.json()

        papers = []
        for work in results.get("results", []):
            abstract = self._get_abstract_from_index(work.get("abstract_inverted_index", {}))
            authors = []
            for authorship in work.get("authorships", []):
                author = authorship.get("author", {})
                if author:
                    authors.append(
                        {
                            "name": author.get("display_name"),
                            "position": authorship.get("author_position"),
                            "institution": authorship.get("institutions", [{}])[0].get("display_name")
                            if authorship.get("institutions")
                            else None,
                        }
                    )

            biblio = work.get("biblio", {})
            citation = {
                "volume": biblio.get("volume"),
                "issue": biblio.get("issue"),
                "first_page": biblio.get("first_page"),
                "last_page": biblio.get("last_page"),
            }

            papers.append(
                {
                    "title": work.get("display_name") or work.get("title", ""),
                    "abstract": abstract,
                    "authors": authors,
                    "citations_count": work.get("cited_by_count"),
                    "doi": work.get("doi"),
                    "publication_year": work.get("publication_year"),
                    "citation_info": citation,
                    "citation_format": self._format_citation(work),
                }
            )

        return papers

    def papers_to_str(self, papers: list[dict[str, Any]]) -> str:
        result = ""
        for paper in papers:
            result += "\n" + "=" * 80
            result += f"\n标题: {paper['title']}"
            result += f"\n摘要: {paper['abstract']}"
            result += "\n作者:"
            for author in paper["authors"]:
                result += f"- {author['name']}"
            result += f"\n引用次数: {paper['citations_count']}"
            result += f"\n发表年份: {paper['publication_year']}"
            result += f"\n引用格式:\n{paper['citation_format']}"
            result += "\n" + "=" * 80
        return result

    @staticmethod
    def _format_citation(work: dict[str, Any]) -> str:
        authors = [
            authorship.get("author", {}).get("display_name")
            for authorship in work.get("authorships", [])
            if authorship.get("author")
        ]
        if len(authors) > 3:
            authors_str = f"{authors[0]} et al."
        else:
            authors_str = ", ".join(authors)

        title = work.get("display_name") or work.get("title", "")
        year = work.get("publication_year", "")
        doi = work.get("doi", "")

        citation = f"{authors_str} ({year}). {title}."
        if doi:
            citation += f" DOI: {doi}"
        return citation
