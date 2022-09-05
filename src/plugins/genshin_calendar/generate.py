import re
from datetime import datetime, timedelta
from pathlib import Path

import jinja2

from .event import get_events
from ...utils.browser import get_new_page

body = []
weeks = []
weekList = ['一', '二', '三', '四', '五', '六', '日']
template_path = Path(__file__).parent / 'template'
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path), enable_async=True)

temp_path = Path() / 'Temp' / 'calendar.html'
temp_img_path = Path() / 'Temp' / 'calendar.png'


async def generate_day_schedule(server='cn'):
    events = await get_events(server, 0, 15)
    has_prediction = False
    body.clear()
    weeks.clear()
    t = datetime.now()

    for i in range(7):
        d2 = (t + timedelta(days=i)).strftime("%Y-%m-%d")
        """ 分割 [年|月|日]"""
        date_full = str(d2).split("-")

        current = 'm-events-calendar__table-header-current' if t.strftime("%d") == date_full[2] else ""
        date = re.search(r'0\d+', date_full[1]).group(0).replace('0', '') if re.search(r'0\d+', date_full[1]) else \
            date_full[1]

        week = datetime(int(date_full[0]), int(date_full[1]), int(date_full[2])).isoweekday()
        weeks.append({
            'week': f'星期{weekList[week - 1]}',
            'date': f'{date}.{date_full[2]}',
            'current': current
        })

    for event in events:
        if event['start_days'] > 0:
            has_prediction = True

    template = env.get_template('calendar.html')
    for event in events:
        if event['start_days'] <= 0:
            time = '即将结束' if event["left_days"] == 0 else f'{str(event["left_days"])}天后结束'
            body.append({
                'title': event['title'],
                'time': time,
                'online': f'{datetime.strftime(event["start"], r"%m-%d")} ~ {datetime.strftime(event["end"], r"%m-%d")}',
                'color': event['color'],
                'banner': event['banner']
            })
    if has_prediction:
        for event in events:
            if event['start_days'] > 0:
                time = '即将开始' if event["start_days"] == 0 else f'{str(event["start_days"])}天后开始'
                body.append({
                    'title': event['title'],
                    'time': time,
                    'online': f'{datetime.strftime(event["start"], r"%m-%d")} ~ {datetime.strftime(event["end"], r"%m-%d")}',
                    'color': event['color'],
                    'banner': event['banner']
                })

    content = await template.render_async(body=body, css_path=template_path, week=weeks)
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return await to_pic(viewport={"width": 600, "height": 10})


async def to_pic(wait: int = 0, **kwargs):
    async with get_new_page(**kwargs) as page:
        await page.goto(f'file://{temp_path.absolute()}')
        await page.wait_for_timeout(wait)
        img_raw = await page.screenshot(full_page=True)
    return img_raw
