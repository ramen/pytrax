# pytrax

Some old code to parse Impulse Tracker files. I originally wrote it in order
to generate XML from song data so that I could make well-synchronized Flash
music videos. Making a decent video turned out to be a much harder problem. :)

## Usage

    >>> from pytrax import impulsetracker
    >>> impulsetracker.parse_file('mytrax.it')
    >>> # also try: with_samples=True, with_instruments=True, with_patterns=True
