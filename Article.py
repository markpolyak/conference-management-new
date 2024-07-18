import Author


class Article:
    author: Author
    title: str
    presentation_quality: int
    advisor_confirmation: bool

    def __init__(self, author, title, presentation_quality=0,
                 advisor_confirmation=False):
        self.author = author
        self.title = title
        self.presentation_quality = presentation_quality
        self.advisor_confirmation = advisor_confirmation
