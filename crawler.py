import requests
from bs4 import BeautifulSoup

from urllib.parse import urljoin, urlparse
from collections import deque
import markdownify
from urllib.robotparser import RobotFileParser
import re




def is_allowed(rp, url, user_agent="*"):
    return rp.can_fetch(user_agent, url)


def split_markdown_sections(text: str):
    sections = re.split(r"\n(?=#)", text)  # split on headers starting with "#"
    return [s.strip() for s in sections if s.strip()]

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def prepare_chunks(docs, markdown_text, path):
    for i, sec in enumerate(markdown_text):
        sec_chunks = chunk_text(sec["content"])
        for j, chunk in enumerate(sec_chunks):
            docs.append({
                "repo": "metaflow/web_doc",
                "path": path,
                "section_id": sec["title"],
                "chunk_id": i,
                "content": chunk
            })

def scrape_metaflow_docs(base_url, limit):
    visited = set()
    queue = deque([base_url])
    ROBOTS_URL = f"{base_url}/robots.txt"
    docs = []
    # Step 1: Parse robots.txt
    rp = RobotFileParser()
    rp.set_url(ROBOTS_URL)
    rp.read()

    while queue and len(visited) < limit:
        url = queue.popleft()
        # print(url)
        if url in visited:
            # print("Eror")
            continue
        visited.add(url)

        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                # print("rtt")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            headers = soup.find_all(["h2", "h3"])  # focus on mid-level 
            sections = []
            for i, header in enumerate(headers):
                section_title = header.get_text().strip()
                section_content = []

                for sibling in header.next_siblings:
                    if sibling.name in ["h2", "h3"]:
                        break
                    if sibling.name in ["p", "ul", "ol", "pre", "code"]:
                        section_content.append(sibling.get_text().strip())
                    
                    sections.append({
                        "title": section_title,
                        "content": "\n".join(section_content)
                    })

            # # Extract main content (Metaflow docs body)
            # content = " ".join([p.get_text() for p in soup.find_all("p")])  # Example: only <p> text

            # content_div = soup.find("div", {"class": "td-content"})
            if not sections:
                continue
            # print(content)
            # Convert HTML to markdown for consistency
            # text = markdownify.markdownify(str(content_div))
            prepare_chunks(docs, sections, url)
            # docs.append({
            #     "path": url,
            #     "content": text
            # })

            # Extract links within docs.metaflow.org
            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"])
                if base_url in link and link not in visited:
                    queue.append(link)

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            continue
    # print(docs)
    return docs

# # Run
# docs_data = scrape_metaflow_docs(limit=10)
# for d in docs_data[:2]:
#     print("URL:", d["url"])
#     print("Content preview:", d["content"][:300], "...\n")

# if __name__ == "__main__":
#     simple_crawl("https://docs.metaflow.org/")