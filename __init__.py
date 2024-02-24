from .apply_whisper import ApplyWhisperNode
from .add_subtitles_to_frames import AddSubtitlesToFramesNode
from .add_subtitles_to_background import AddSubtitlesToBackgroundNode
from .resize_cropped_subtitles import ResizeCroppedSubtitlesNode
from .localedit import   Load_Alignment_From_file,save_Alignment_to_file



NODE_CLASS_MAPPINGS = { 
    "Apply Whisper" : ApplyWhisperNode,
    "Add Subtitles To Frames": AddSubtitlesToFramesNode,
    "Add Subtitles To Background": AddSubtitlesToBackgroundNode,
    "Resize Cropped Subtitles": ResizeCroppedSubtitlesNode,
    "save Alignments to file " :save_Alignment_to_file,
    "load Alignments from file " :Load_Alignment_From_file,
    
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "Apply Whisper" : "Apply Whisper", 
     "Add Subtitles To Frames": "Add Subtitles To Frames",
     "Add Subtitles To Background": "Add Subtitles To Background",
     "Resize Cropped Subtitles": "Resize Cropped Subtitles",
     "save Alignments to file" : "save Alignments to file", 
    "load Alignments from file " :"load Alignments from file ",
  
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']