from bs4 import BeautifulSoup
import requests
import re
import time
import json


AUTHORS_PATTERN = re.compile('author={(.*)}')


class Paper:
    def __init__(self, Id, title, authors, date, abstract, references, related_topics, reference_count, citation_count):
        self.Id = Id
        self.title = title
        self.authors = authors
        self.date = date
        self.abstract = abstract
        self.references = references
        self.related_topics = related_topics
        self.reference_count = reference_count
        self.citation_count = citation_count

    def __str__(self):
        return f'Paper(Id={self.Id}, title={self.title}, authors={self.authors}, date={self.date}, abstract={self.abstract}, references={self.references})'

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            'Id': self.Id,
            'title': self.title,
            'authors': self.authors,
            'date': self.date,
            'abstract': self.abstract,
            'references': self.references,
            'related_topics': self.related_topics,
            'reference_count': self.reference_count,
            'citation_count': self.citation_count
        }

    @staticmethod
    def from_dict(d):
        return Paper(
            Id=d['Id'],
            title=d['title'],
            authors=d['authors'],
            date=d['date'],
            abstract=d['abstract'],
            references=d['references'],
            related_topics=d['related_topics'],
            reference_count=d['reference_count'],
            citation_count=d['citation_count']
        )


class ScholarSpider:

    def __init__(self, name, start_urls=None, allowed_domains=None, max_crawled=1000, max_ref=10, **kwargs):
        self.name = name
        self.start_urls = start_urls
        self.allowed_domains = allowed_domains
        self.kwargs = kwargs
        self.name = name

        if start_urls is None:
            self.start_urls = [
                'https://www.semanticscholar.org/paper/The-Lottery-Ticket-Hypothesis%3A-Training-Pruned-Frankle-Carbin/f90720ed12e045ac84beb94c27271d6fb8ad48cf',
                'https://www.semanticscholar.org/paper/Attention-is-All-you-Need-Vaswani-Shazeer/204e3073870fae3d05bcbc2f6a8e263d9b72e776',
                'https://www.semanticscholar.org/paper/BERT%3A-Pre-training-of-Deep-Bidirectional-for-Devlin-Chang/df2b0e26d0599ce3e70df8a9da02e51594e0e992'
            ]

        if allowed_domains is None:
            self.allowed_domain = 'https://www.semanticscholar.org'

        self.max_crawled = max_crawled
        self.max_ref = max_ref
        self.crawled_set = set()

    def get_next_url(self):
        try:
            next_url = self.frontier_queue.pop(0)
            self.crawled_set.add(next_url)
            return next_url
        except:
            return None

    def get_page_urls(self):
        """
        get all urls in the page
        """
        new_urls = []
        soup = BeautifulSoup(self.page.text, "html.parser")
        soup.find('div', {'data-test-id': 'cited-by'})
        for reference in soup.find_all('div', {'class': 'cl-paper-row citation-list__paper-row'})[:self.max_ref]:
            try:
                url = self.allowed_domain + \
                    reference.find(
                        'a', {'class': 'link-button--show-visited'}).get('href')
                if url not in self.crawled_set:
                    new_urls.append(url)
            except:
                pass

        return new_urls

    def parse_page(self):
        """
        get all content in the page
        """
        soup = BeautifulSoup(self.page.content, "html.parser")
        if soup.find('div', {'class': 'verify-robot'}):
            raise Exception('Robot Verification')

        def find_text(element, attr, default=""):
            found = soup.find(element, attr)
            return found.text if found else default

        paper_id = self.page_url.split('/')[-1]
        title = find_text('h1', {'data-test-id': 'paper-detail-title'})
        head = soup.findAll('head')
        meta_tag = head[0].find('meta', {'name': 'description'})
        abstract = meta_tag['content'] if meta_tag else 'Content not found'

        year = find_text('span', {'data-test-id': 'paper-year'})
        citation_refs = soup.find_all(
            'h2', {'class': 'dropdown-filters__result-count__header dropdown-filters__result-count__citations'})
        citation_count = citation_refs[0].text.split(
            ' ')[0] if len(citation_refs) > 0 else '0'
        reference_count = citation_refs[1].text.split(
            ' ')[0] if len(citation_refs) > 1 else '0'

        # Extract authors using regex
        authors_match = AUTHORS_PATTERN.findall(self.page.text)
        authors = authors_match.pop().split(' and ') if authors_match else []

        card = soup.find('div', {'data-test-id': 'reference'})
        refs = []
        if card:
            for reference in card.find_all('div', {'class': 'cl-paper-row citation-list__paper-row'}):
                ref_link = reference.find(
                    'a', {'class': 'link-button--show-visited'})
                if ref_link:
                    ref_id = ref_link.get('href').split('/')[-1]
                    refs.append(ref_id)

        related_topics_container = soup.find(
            'div', {'class': 'card-content-main paper-topics__container'})
        related_topics = []
        if related_topics_container:
            related_topics = [link.contents[0] for link in related_topics_container.findAll(
                'a', {'data-heap-id': 'paper_topic_link'})]

        paper = Paper(
            Id=paper_id,
            title=title,
            authors=authors,
            date=year,
            abstract=abstract,
            references=refs,
            related_topics=related_topics,
            reference_count=reference_count,
            citation_count=citation_count
        )

        return paper

    def get_page(self, url):
        API_KEY = 'aabf5a9a9fb633aa6943d5f04fa9b398'
        payload = {'api_key': API_KEY, 'url': url}
        r = requests.get('http://api.scraperapi.com', params=payload)
        return r

    def start(self):
        """
        start crawling
        """
        self.frontier_queue = self.start_urls
        crawled_pages = []
        current_url = self.get_next_url()
        while current_url is not None and len(self.crawled_set) < self.max_crawled:
            print(current_url)
            self.page_url = current_url
            self.page = self.get_page(current_url)
            try:
                paper = self.parse_page()
                crawled_pages.append(paper)
                self.frontier_queue.extend(self.get_page_urls())
            except Exception as e:
                print(e)
                pass
            current_url = self.get_next_url()
        return crawled_pages


if __name__ == '__main__':
    profs = ['Kasaei', 'Sharifi', 'Soleymani']
    for prof in profs:
        start_urls = []
        with open('Profs/' + prof + '.txt', 'r') as f:
            for line in f.readlines():
                start_urls.append(line.strip())

        spider = ScholarSpider(prof, start_urls=start_urls,
                               max_crawled=200, max_ref=10)
        papers = spider.start()
        with open('Papers/' + prof + '.json', 'w') as f:
            json.dump([paper.to_dict() for paper in papers], f, indent=4)
