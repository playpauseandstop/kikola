import datetime

from kikola.core.decorators import render_to_json
from kikola.utils import TimedeltaJSONEncoder


@render_to_json(cls=TimedeltaJSONEncoder)
def timedelta_json_encoder(request):
    now = datetime.datetime.now()
    return {'date': now.date(),
            'datetime': now,
            'time': now.time(),
            'timedelta': datetime.timedelta(hours=now.hour,
                                            minutes=now.minute,
                                            seconds=now.second)}
