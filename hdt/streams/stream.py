
class Stream:
    """
    Represents the flow of materials or signals between unit operations.
    Tracks origin, destination, and content of the stream.
    """

    def __init__(self, origin, destination, contents=None):
        """
        Args:
            origin (str): Name of the originating unit (e.g., 'GutReactor')
            destination (str): Name of the target unit (e.g., 'LiverMetabolicRouter')
            contents (dict): Dictionary of data being transferred (e.g., glucose, SCFA, signals)
        """
        self.origin = origin
        self.destination = destination
        self.contents = contents or {}

    def update(self, new_contents):
        """
        Update the contents of the stream.

        Args:
            new_contents (dict): New data to update the stream with
        """
        self.contents.update(new_contents)

    def clear(self):
        """
        Clear the contents of the stream.
        """
        self.contents = {}

    def __repr__(self):
        return f"<Stream {self.origin} → {self.destination} | {self.contents}>"
