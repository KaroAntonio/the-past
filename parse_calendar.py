import icalendar 
import json
from icalendar import Calendar,Event
from datetime import datetime
import pytz
from dateutil.parser import parse as parse_date

def load_ics():
	fid = 'assets/karoantonio@gmail.com.ics'
	f = open(fid,'rb')
	cal = Calendar.from_ical(f.read())

	day_one = datetime(2016,11,4,tzinfo=pytz.utc)
	now = datetime.now(pytz.utc)
	t0 = datetime(1970,1,1,tzinfo=pytz.utc)

	events = []
	attrs = ['dtstart','summary','dtend','dtstamp']

	for comp in cal.walk():
		if comp.name == "VEVENT":
			evt = {e:comp.get(e) for e in attrs}
			start = evt['dtstart'].dt
			date = datetime(start.year,start.month,start.day,tzinfo=pytz.utc)
			if date > day_one and date < now:
				evt['dtstart'] = str(evt['dtstart'].dt)
				evt['dtend'] = str(evt['dtend'].dt)
				evt['dtstamp'] = str(evt['dtstamp'].dt)
				evt['lane'] = 0
				events += [evt]
	return events

def save_json(data,fid):
	with open(fid,'w') as out:
		json.dump(data,out)

def load_json(fid):
	with open(fid) as data_file:
		events = json.load(data_file)
	return events

def replace_keys(events,keymap):
	for evt in events:
		for k in keymap:
			evt[keymap[k]] = evt[k]
			del evt[k]

def as_seconds(events,keys):
	t0 = datetime(1970,1,1,tzinfo=pytz.utc)
	for evt in events:
		for k in keys:
			evt[k] = (parse_date(evt[k]) - t0).total_seconds()

def init_lane(events):
	for evt in events:
		evt['lane'] = 0

def parse_categories(evt_str):
	imp = ['eating','sleep','work','hannah']
	cats = []
	if '#' in evt_str:
		cats_str = evt_str.split('#')[1]
		cats = [e.strip().lower() for e in cats_str.split(',') if e in imp]
	if cats:	
		return cats
	else:
		return ['uncategorized']

def map_lanes(events):
	lane_map = []
	for evt in events:
		cat = parse_categories(evt['id'])[0]
		if cat not in lane_map:
			lane_map += [cat]
		evt['lane'] = lane_map.index(cat)

	return lane_map

#init_lane(events)

'''
events = load_ics()
replace_keys(events,{'dtstart':'start','dtend':'end','dtstamp':'stamp'})
replace_keys(events,{'summary':'id'})
as_seconds(events,['start','end'])
'''

events = load_json('assets/events.json')
lanes = map_lanes(events) 

#save_json(events,'assets/events.json')
save_json({'events':events,'lanes':lanes},'assets/timetable_data.json')
