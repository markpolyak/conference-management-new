from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConferencesFilter:
    filter_type: str = 'active'
    conferences: list = field(default_factory=[])
    f: callable = None

    def exec(self):
        return self.f()

    def _all_filter(self):
        return self.conferences

    def _active_filter(self):
        res = []
        for c in self.conferences:
            if c.registration_start_date < datetime.now() and datetime.now() < c.registration_end_date:
                res.append(c)
        return res

    def _past_filter(self):
        res = []
        for c in self.conferences:
            if datetime.now() > c.registration_end_date:
                res.append(c)
        return res

    def _future_filter(self):
        res = []
        for c in self.conferences:
            if c.registration_start_date > datetime.now():
                res.append(c)
        return res

    def __post_init__(self):
        self.f = {
            'all': self._all_filter,
            'active': self._active_filter,
            'past': self._past_filter,
            'future': self._future_filter,
        }.get(self.filter_type, self._active_filter)
