import datetime as dt
import os

def get_file(file_path): 
    if os.path.isfile(file_path) == False:
        print("File \"" + file_path + "\" does not exist! Please ensure that this executable is in the same folder as the start list file.\nPlease press \"Enter\" to close this window.")
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
    current_event = ['', '', '', '', '', '', '', ''] # [0:start_date, 1:end_date, 2:event_name, 3:location, 4:repeat_rule, 5:repeat_day, 6:repeat_end, 7:description]
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
                current_event[0] = start_date
            elif 'DTEND' in line_contents[0]:
                end_date = (line_contents[1].split('T'))[0]
                current_event[1] = end_date
            elif line_contents[0] == 'SUMMARY':
                event_name = (line_contents[1]).replace('\\', '')
                current_event[2] = event_name
                prev_line_type = "event_name"
            elif line_contents[0] == 'LOCATION':
                location = (line_contents[1]).replace('\\', '')
                if 'http' in location:
                    location = location + ':' + line_contents[2]
                current_event[3] = location
                prev_line_type = "location"
            elif line[0] == " ":
                if prev_line_type == "event_name":
                    remaining_text = (line[1:]).replace('\\', '')
                    last_line_text = current_event[2]
                    joined_text = last_line_text + remaining_text
                    current_event[2] = joined_text
                elif prev_line_type == "location":
                    remaining_text = (line[1:]).replace('\\', '')
                    last_line_text = current_event[3]
                    joined_text = last_line_text + remaining_text
                    current_event[3] = joined_text
                elif prev_line_type == "description":
                    remaining_text = (line[1:]).replace('\\n', '; ')
                    remaining_text = remaining_text.replace('\\', '')
                    last_line_text = current_event[7]
                    joined_text = last_line_text + remaining_text
                    current_event[7] = joined_text
                prev_line_type = ""
            elif line == "END:VEVENT":
                if int(current_event[0]) >= earliest_date:
                    all_events.append(current_event)
                    #print(current_event)
                current_event = ['', '', '', '', '', '', '', '']
                is_event = False
            else:
                prev_line_type = ""
            if include_repeats == True:
                if 'RRULE' in line:
                    repeat_line = (line.replace('RRULE:', '')).split(';')
                    #print(repeat_line)
                    for elem in repeat_line:
                        if 'FREQ' in elem:
                            repeat_freq = elem.replace('FREQ=', '')
                        elif 'WKST' in elem:
                            repeat_day = elem.replace('WKST=', '')
                        elif 'UNTIL' in elem:
                            repeat_end = (elem.replace('UNTIL=', ''))[:8]
                    current_event[4] = repeat_freq.title()
                    current_event[5] = repeat_day.title()
                    current_event[6] = repeat_end
            if include_description == True:
                if line_contents[0] == 'DESCRIPTION':
                    description = (line_contents[1]).replace('\\n', '; ')
                    description = description.replace('\\', '')
                    current_event[7] = description
                    prev_line_type = "description"
                
                
    all_events.sort()
    return all_events, cal_name, timezone

def format_output(events, cal_name, timezone, alt_location, include_repeats, include_description):
    output = []
    output.append("Calendar Name: " + cal_name)
    output.append("Default Timezone: " + timezone)
    output.append("")
    for event in events:
        #print(event)
        event_name = event[2]
        start_date_raw = event[0]
        start_year = int(start_date_raw[0:4])
        start_month = int(start_date_raw[4:6])
        start_day = int(start_date_raw[6:])
        start_date_dt = dt.datetime(start_year, start_month, start_day)
        start_date = start_date_dt.strftime("%a. %d %b, %Y")
        end_date_raw = (event[1])
        end_year = int(end_date_raw[0:4])
        end_month = int(end_date_raw[4:6])
        end_day = int(end_date_raw[6:])
        end_date_dt = dt.datetime(end_year, end_month, end_day)
        end_date = end_date_dt.strftime("%a. %d %b, %Y")
        location = event[3]
        if location == '':
            location = alt_location

        output.append(event_name)
        output.append("  > Starts: " + str(start_date))
        output.append("  > Ends:   " + str(end_date))
        if include_repeats == True:
            repeat_freq = event[4]
            repeat_wkday = event[5]
            repeat_end_date = ''
            if event[6] != '':
                repeat_end_raw = event[6]
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
                        output.append("  > Repeats " + repeat_freq + " every " + wkday + " until " + repeat_end_date + ".")
                    else:
                        output.append("  > Repeats " + repeat_freq + " every " + wkday + ".")
                else:
                    output.append("  > Repeats " + repeat_freq + ".")
        output.append("  > Location: " + location)
        if include_description == True:
            description = event[7]
            if description != '':
                output.append("  > Description: " + description)
        output.append("")
    #print(output)
    return output

def write_file(l, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines("\n".join(l))

def main():
    earliest_date = 0

    write_file_ = True
    print_outp = True
    alt_location = "TBD"
    include_repeats = True
    include_description = True
    
    in_path = './ICALENDARFILE.ics'
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

main()
