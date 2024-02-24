
import pandas as pd
from pathlib import Path
from typing import Callable, Optional, TextIO
import re
def format_timestamp(seconds: float, always_include_hours: bool = False, decimal_marker: str = '.'):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"            

def rev_format_timestamp(st:str, decimal_marker: str = ','):
    st = st.lstrip("0:").rstrip("0")
    st = st.replace(decimal_marker,".")
    return float(st)



class Load_Alignment_From_file:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "dir": ("STRING", {"default": "X://insert/path/here.xsls",}), 
                 
            }
        }

    RETURN_TYPES = ("whisper_alignment",)
    RETURN_NAMES = ("whisper alignment")
    FUNCTION = "load_from_file"
    CATEGORY = "whisper"

    def load_from_file(self,dir):
        file_ext = dir[dir.rfind("."):]
        if not file_ext:
            assert "file does not exist"
            return (None,)
        if file_ext == ".xlsx":        
            try:
                alignment_df = pd.read_excel(dir, index_col=None, header=None)  
            except Exception as e:
                    assert "there was a problem" , e
                    return (None,)
            i = 0
            lst = []
            for _,t,s,e in alignment_df.itertuples(index=False):
                if i == 0:
                    i+=1
                    continue
                else:
                    lst.append({'value':t, 'start': float(s), 'end': float(e)})

        elif file_ext == ".srt":
            subtitles = []
            with open(dir, "r", encoding="utf-8") as sourceFile:
                lines = sourceFile.readlines()
                
            subs = []
            for line in lines:
                line = line.strip()
                if re.match(r'^\d+$', line):
                    if subs:
                        subtitles.append({
                            'value': ' '.join(subs[2:]),
                            'start': rev_format_timestamp(subs[0]),
                            'end': rev_format_timestamp(subs[1])
                        })
                        subs = []
                elif re.match(r'^\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+$', line):
                    times = line.split(' --> ')
                    subs.extend(times)
                elif line:
                    subs.append(line)
            
            # Add the last subtitle
            if subs:
                subtitles.append({
                    'value': ' '.join(subs[2:]),
                    'start': rev_format_timestamp(subs[0]),
                    'end': rev_format_timestamp(subs[1])
                })
                
        return (subtitles,)
        



class save_Alignment_to_file:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "alignment" : ("whisper_alignment",),
                "dir": ("STRING", {"default": "X://insert/path/here.xsls",}),
                "save_srt": ("BOOLEAN", {"default": True}),
                "save_excel": ("BOOLEAN", {"default": False}),  

            }
        }

    RETURN_TYPES = ("whisper_alignment",)
    RETURN_NAMES = ("whisper alignment")
    FUNCTION = "write_result"
    CATEGORY = "whisper"


    def write_result(
        self, alignment: dict, dir,save_srt:bool, save_excel: bool ):
        # handle file path and name
        file_ext =""
        if dir.rfind(".") == -1:
            if not dir.endswith("\\"):   # if the path isnt a file, make sure it ends with a backslash
                dir += "\\"
        else:        
            file_ext = dir[dir.rfind("."):]


       # save to excel file
        if save_excel:
            if file_ext == ".xlsx":
                 sourceFile = dir
            else:
                sourceFile = f"{dir}subtitle.xlsx"
            try:
                print("trying to write to excel file")
                df = pd.DataFrame(alignment)
                df.to_excel(sourceFile)
            except Exception as e:
                assert "there was a problem", e


        # save to srt file
        if save_srt: 
            if file_ext == ".srt":
                 sourceFile = dir
            else:
                sourceFile = f"{dir}subtitle.srt"
            #print("source file is : ",sourceFile)
            with open(sourceFile, "w", encoding="utf-8") as sourceFile:
                t = 0
                for i in sorted([*alignment],key =lambda key: key.get("start", -1)):
                    t+=1
                    start = format_timestamp(i.get("start", -1),always_include_hours=True, decimal_marker=',')
                    end =   format_timestamp(i.get("end", -1),always_include_hours=True, decimal_marker=',')
                    value = i.get("value", "")
                    #print(f"{t}\n{start} --> {end}\n{value}\n")
                    print(f"{t}\n{start} --> {end}\n{value}\n" , file=sourceFile, flush=True)
        return (alignment,)




   