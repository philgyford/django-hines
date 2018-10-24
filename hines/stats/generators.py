from spectator.reading.utils import annual_reading_counts


class ReadingGenerator:
    """
    For things about Books, Periodicals etc.
    """

    def __init__(self, kind):
        """
        kind is either 'book' or 'periodical'.
        """
        self.kind = kind

    def get_reading_per_year(self):
        data = {
            'data': [],
            'title': '{}s read per year'.format(self.kind).capitalize(),
            'description': "Determined by date finished."
        }

        # The first years we have complete data for each kind:
        if self.kind == 'periodical':
            min_year = 2005
        else:
            min_year = 1998

        # counts will be like
        # [ {'year': date(2005, 1, 1), 'book': 37}, ... ]
        counts = annual_reading_counts(kind=self.kind)
        max_year = counts[-1]['year'].year

        # Make it like
        # {'2005': 37, '2006': 23'}
        counts = {str(c['year'].year):c[self.kind] for c in counts}

        # In case the counts have a missing year, we manually go through from
        # first to last year so we cover all years, even if there's no
        # readings.
        for year in range(min_year, max_year+1):
            syear = str(year)
            if syear in counts:
                year_data = {
                    'label': syear,
                    'value': counts[syear]
                }
            else:
                year_data = {
                    'label': syear,
                    'value': 0
                }
            data['data'].append(year_data)

        return data


class StaticGenerator:
    """
    For all kinds of hard-coded data.
    """

    def get_headaches_per_year(self):
        data = {
            'data': [
                {'label': '2006', 'value': 29},
                {'label': '2007', 'value': 22},
                {'label': '2008', 'value': 18},
                {'label': '2009', 'value': 8},
                {'label': '2010', 'value': 10},
                {'label': '2011', 'value': 14},
                {'label': '2012', 'value': 12},
                {'label': '2013', 'value': 34},
                {'label': '2014', 'value': 47},
                {'label': '2015', 'value': 51},
                {'label': '2016', 'value': 59},
                {'label': '2017', 'value': 53},
            ],
            'title': 'Headaches per year',
            'description': "Those that require, or are defeated by, prescription medication."
        }

        return data
