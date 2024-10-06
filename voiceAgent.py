from baseAnnotationApp import BaseAnnotationApp
import tkinter as tk
from utils import RequireRewriteCheckBox, NeedsClarificationCheckBox, EnoughContext


class VoiceAgentApp(BaseAnnotationApp):

    def is_turn_empty(self, dialog_id, turn_id):
        pass

    def are_all_fields_filled(self):
        return True
    
    def setup_special_classes(self):
        pass
    def init_turn_special_classes(self):
        pass

    def update_json(self):
        return True