class i18n(object):
    def __init__(self):
        # Default domain
        self._domain = 'idn'

    def domain(self, country):
        self._domain = country

    def translate(self, domain):
        dic = {}

        dic['idn'] = {
            # Month
            'Januari': 'January',
            'Februari': 'February',
            'Maret': 'March',
            'April': 'April',
            'Mei': 'May',
            'Juni': 'June',
            'Juli': 'July',
            'Agustus': 'August',
            'September': 'September',
            'Oktober': 'October',
            'November': 'November',
            'Desember': 'December',
            # Month abbrevation
            'Jan': 'January',
            'Feb': 'February',
            'Mar': 'March',
            'Apr': 'April',
            'Jun': 'June',
            'Jul': 'July',
            'Agt': 'August',
            'Agu': 'August',
            'Sep': 'September',
            'Okt': 'October',
            'Nov': 'November',
            'Des': 'December',
            'May': 'May',
            'Aug': 'August',
            'Oct': 'October',
            'Dec': 'December',
        }

        return dic[domain] if domain in dic else {}

    def __call__(self, string):
        t = self.translate(self._domain)

        if string in t:
            return t[string]
        return string
