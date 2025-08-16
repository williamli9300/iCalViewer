# iCalViewer by Will Li | https://github.com/williamli9300/iCalViewer | v0.1.0

from zoneinfo import ZoneInfo
import datetime as dt
import operator, os


#### CONFIG ####

earliest_date = 0
write_file_ = True
print_outp = True
alt_location = "TBD"
include_repeats = True
include_description = True

in_path = './Calendar.ics'

################

def get_file(file_path): 
    if os.path.isfile(file_path) == False:
        print("File \"" + file_path + "\" does not exist! Please ensure that this executable \
is in the same folder as the start list file.\nPlease press \"Enter\" to close this window.")
        sys.exit()
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        f.close()
    print("opening \"" + file_path + "\"...")
    return lines

def process_lines(lines, earliest_date, include_repeats, include_description):
    cal_name = ""
    timezone = ""
    is_event = False
    prev_line_type = ""
    all_events = []
    exdate = []
    #current_event = ['', '', '', '', '', '', '', ''] [0:start_date, 1: start_time, 2:end_date, 3:end_time, 4:event_name, 3:location, 4:repeat_freq, 5:repeat_day, 6:repeat_end, 7:description]
    current_event = {'start_date':'', 'start_time':'', 'start_tz':'',
                     'end_date':'', 'end_time':'', 'end_tz':'',
                     'event_name':'', 'location':'',
                     'repeat_freq':'', 'repeat_day':'',
                     'repeat_end':'', 'repeat_exceptions':'',
                     'description':''}
    for line in lines:
        line_contents = line.split(":")
        if is_event == False:
            if line_contents[0] == 'X-WR-CALNAME':
                cal_name = line_contents[1]
            elif line_contents[0] == 'TZID':
                timezone = line_contents[1]
            elif line == 'BEGIN:VEVENT':
                is_event = True
        elif is_event == True:
            #print(line_contents)
            if 'DTSTART' in line_contents[0]:
                start_date = (line_contents[1].split('T'))[0]
                current_event['start_date'] = start_date
                if 'TZID' in line:
                    start_time = (line_contents[1].split('T'))[1]
                    current_event['start_time'] = start_time
                    tz_line = line_contents[0].split(';')
                    tz = tz_line[1].replace('TZID=', '')
                    current_event['start_tz'] = tz
            elif 'DTEND' in line_contents[0]:
                end_date = (line_contents[1].split('T'))[0]
                current_event['end_date'] = end_date
                if 'TZID' in line:
                    end_time = (line_contents[1].split('T'))[1]
                    current_event['end_time'] = end_time
                    tz_line = line_contents[0].split(';')
                    tz = tz_line[1].replace('TZID=', '')
                    current_event['end_tz'] = tz
            elif line_contents[0] == 'SUMMARY':
                event_name = (line_contents[1]).replace('\\', '')
                current_event['event_name'] = event_name
                prev_line_type = "event_name"
            elif line_contents[0] == 'LOCATION':
                location = (line_contents[1]).replace('\\', '')
                if 'http' in location:
                    location = location + ':' + line_contents[2]
                current_event['location'] = location
                prev_line_type = "location"
            elif line[0] == " ":
                if prev_line_type == "event_name":
                    remaining_text = (line[1:]).replace('\\', '')
                    last_line_text = current_event['event_name']
                    joined_text = last_line_text + remaining_text
                    current_event['event_name'] = joined_text
                elif prev_line_type == "location":
                    remaining_text = (line[1:]).replace('\\', '')
                    last_line_text = current_event['location']
                    joined_text = last_line_text + remaining_text
                    current_event['location'] = joined_text
                elif prev_line_type == "description":
                    remaining_text = (line[1:]).replace('\\n', '; ')
                    remaining_text = remaining_text.replace('\\', '')
                    last_line_text = current_event['description']
                    joined_text = last_line_text + remaining_text
                    current_event['description'] = joined_text
            elif line == "END:VEVENT":
                if int(current_event['start_date']) >= earliest_date:
                    all_events.append(current_event)
                    #print(current_event)
                current_event = {'start_date':'', 'start_time':'', 'start_tz':'',
                                 'end_date':'', 'end_time':'', 'end_tz':'',
                                 'event_name':'', 'location':'',
                                 'repeat_freq':'', 'repeat_day':'',
                                 'repeat_end':'', 'repeat_exceptions':'',
                                 'description':''}
                is_event = False
            elif 'RRULE' in line:
                if include_repeats == True:
                    repeat_line = (line.replace('RRULE:', '')).split(';')
                    #print(repeat_line)
                    for elem in repeat_line:
                        if 'FREQ' in elem:
                            repeat_freq = elem.replace('FREQ=', '')
                        elif 'WKST' in elem:
                            repeat_day = elem.replace('WKST=', '')
                        elif 'UNTIL' in elem:
                            repeat_end = (elem.replace('UNTIL=', ''))[:8]
                    current_event['repeat_freq'] = repeat_freq.title()
                    current_event['repeat_day'] = repeat_day.title()
                    current_event['repeat_end'] = repeat_end
            elif 'EXDATE' in line:
                if include_repeats == True:
                    ex_datetime = line_contents[1].split('T')
                    ex_date = ex_datetime[0]
                    ex_date_time_tz = [ex_date, '', '']
                    if 'TZID' in line:
                        ex_time = ex_datetime[1][:4]
                        ex_date_time_tz[1] = ex_time
                        tz_line = line_contents[0].split(';')
                        tz = tz_line[1].replace('TZID=', '')
                        ex_date_time_tz[2] = tz
                    exdate.append(ex_date_time_tz)
                    prev_line_type = 'exdate'
            elif line_contents[0] == 'DESCRIPTION':
                if include_description == True:
                    description = (line_contents[1]).replace('\\n', '; ')
                    description = description.replace('\\', '')
                    current_event['description'] = description
                    prev_line_type = "description"
            else:
                prev_line_type = ""
            if exdate != []:
                if prev_line_type != 'exdate':
                    exdate.sort()
                    current_event['repeat_exceptions'] = exdate
                    exdate = []
    output_events = sorted(all_events, key=operator.itemgetter('start_date'))
    return output_events, cal_name, timezone

def format_output(events, cal_name, timezone, alt_location, include_repeats, include_description):
    output = []
    output.append("Calendar Name: " + cal_name)
    output.append("Default Timezone: " + timezone)
    output.append("")
    for event in events:
        #print(event)
        event_name = event['event_name']
        
        start_date_raw = event['start_date']
        start_year = int(start_date_raw[0:4])
        start_month = int(start_date_raw[4:6])
        start_day = int(start_date_raw[6:])
        start_date_dt = dt.datetime(start_year, start_month, start_day)
        start_date = start_date_dt.strftime("%a. %d %b, %Y")
        if event['start_time'] != '':
            start_time = event['start_time'][0:4]
            if event['start_tz'] != '':
                tz_dt = dt.datetime(start_year, start_month, start_day, int(start_time[:2]), int(start_time[2:]), tzinfo=ZoneInfo(event['start_tz']))
                tz = tz_dt.tzname()
                start_date = start_date + " at " + start_time[:2] + ":" + start_time[2:] + " " + tz
            else:
                start_date = start_date + " at " + start_time[:2] + ":" + start_time[2:]
        
        end_date_raw = (event['end_date'])
        end_year = int(end_date_raw[0:4])
        end_month = int(end_date_raw[4:6])
        end_day = int(end_date_raw[6:])
        end_date_dt = dt.datetime(end_year, end_month, end_day)
        end_date = end_date_dt.strftime("%a. %d %b, %Y")
        if event['end_time'] != '':
            end_time = event['end_time'][0:4]
            if event['end_tz'] != '':
                tz_dt = dt.datetime(end_year, end_month, end_day, int(end_time[:2]), int(end_time[2:]), tzinfo=ZoneInfo(event['end_tz']))
                tz = tz_dt.tzname()
                end_date = end_date + " at " + end_time[:2] + ":" + end_time[2:] + " " + tz
            else:
                end_date = end_date + " at " + end_time[:2] + ":" + end_time[2:]
            
        
        location = event['location']
        if location == '':
            location = alt_location

        output.append(event_name)
        output.append("  > Starts:   " + str(start_date))
        output.append("  > Ends:     " + str(end_date))
        if include_repeats == True:
            repeat_freq = event['repeat_freq']
            repeat_wkday = event['repeat_day']
            repeat_end_date = ''
            if event['repeat_end'] != '':
                repeat_end_raw = event['repeat_end']
                repeat_end_year = int(repeat_end_raw[0:4])
                repeat_end_month = int(repeat_end_raw[4:6])
                repeat_end_day = int(repeat_end_raw[6:])
                repeat_end_date_dt = dt.datetime(repeat_end_year, repeat_end_month, repeat_end_day)
                repeat_end_date = repeat_end_date_dt.strftime("%a. %d %b, %Y")
            if repeat_freq != '':
                if repeat_wkday !='':
                    wkday_dict = {'Su':'Sunday', 'Mo':'Monday', 'Tu':'Tuesday', 'We':'Wednesday', 'Th':'Thursday', 'Fr':'Friday', 'Sa':'Saturday'}
                    if ',' in repeat_wkday:
                        wkdays = repeat_wkday.split(',')
                        new_wkdays = []
                        for i in range(len(wkday)):
                            if i == range(len(wkday)) -1:
                                new_wkdays.append('and ' + wkday_dict[day])
                            else:
                                new_wkdays.append(wkday_dict[day])
                        wkday = ", ".join(new_wkdays)
                    else:
                        wkday = wkday_dict[repeat_wkday]
                    if repeat_end_date != '':
                        output.append("  > Repeats:  " + repeat_freq + " every " + wkday + " until " + repeat_end_date + ".")
                    else:
                        output.append("  > Repeats:  " + repeat_freq + " every " + wkday + ".")
                else:
                    output.append("  > Repeats:  " + repeat_freq + ".")
                if event['repeat_exceptions'] != '':
                    for exception in event['repeat_exceptions']:
                        ex_year = int(exception[0][0:4])
                        ex_month = int(exception[0][4:6])
                        ex_day = int(exception[0][6:])
                        ex_date_dt = dt.datetime(ex_year, ex_month, ex_day)
                        ex_date = ex_date_dt.strftime("%a. %d %b, %Y")
                        if exception[1] != '':
                            if exception[2] != '':
                                tz_dt = dt.datetime(ex_year, ex_month, ex_day, int(exception[1][:2]), int(exception[1][2:]), tzinfo=ZoneInfo(exception[2]))
                                tz = tz_dt.tzname()
                                ex_date = ex_date + " at " + exception[1][:2] + ":" + exception[1][2:] + " " + tz
                            else:
                                ex_date = ex_date + " at " + exception[1][:2] + ":" + exception[1][2:]
                        output.append("              - except " + ex_date)
                            
        output.append("  > Location: " + location)
        if include_description == True:
            description = event['description']
            if description != '':
                output.append("  > Notes:    " + description)
        output.append("")
    #print(output)
    return output

def write_file(l, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines("\n".join(l))

def main(earliest_date, write_file_, print_outp, alt_location, include_repeats, include_description, in_path):

    out_path = in_path.replace('.ics', '.txt')
    lines = get_file(in_path)
    all_events, cal_name, timezone = process_lines(lines, earliest_date, include_repeats, include_description)
    output = format_output(all_events, cal_name, timezone, alt_location, include_repeats, include_description)

    if print_outp == True:
        for line in output:
            print(line)
    if write_file_ == False:
        #print(out_path)
        write_file(output, out_path)
        print("file written.")
    print("done.")

main(earliest_date, write_file_, print_outp, alt_location, include_repeats, include_description, in_path)
