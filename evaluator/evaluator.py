from evaluator.Social import *
from evaluator.TA import *


class Evaluator:
    def __init__(self):
        self.config = None
        self.symbol = None
        self.history_time = None
        self.data = None
        self.symbol = None

        self.social_eval_list = []
        self.ta_eval_list = []

        self.final_eval = START_EVAL_NOTE
        self.social_final_eval = START_EVAL_NOTE
        self.ta_final_eval = START_EVAL_NOTE
        self.state = EvaluatorStates.NEUTRAL

    def set_config(self, config):
        self.config = config

    def set_data(self, data):
        self.data = data

    def set_symbol(self, symbol):
        self.symbol = symbol

    def set_state(self, state):
        if state != self.state:
            self.state = state
            # TODO Add notify change

    def get_state(self):
        return self.state

    def set_history_time(self, history_time):
        self.history_time = history_time

    def get_final_eval(self):
        return self.final_eval

    def social_eval(self):
        self.social_eval_list = []
        for social_type in SocialEvaluator.__subclasses__():
            for social_eval_class_type in social_type.__subclasses__():
                social_eval_class = social_eval_class_type()
                social_eval_class.set_config(self.config)
                social_eval_class.set_history_time(self.history_time)
                social_eval_class.set_symbol(self.symbol)

                social_eval_class.get_data()
                social_eval_class.eval()
                self.social_eval_list.append(social_eval_class)

        return self.social_eval_list

    def ta_eval(self):
        self.ta_eval_list = []
        for ta_type in TAEvaluator.__subclasses__():
            for ta_eval_class_type in ta_type.__subclasses__():
                ta_eval_class = ta_eval_class_type()
                ta_eval_class.set_config(self.config)
                ta_eval_class.set_data(self.data)
                ta_eval_class.eval()

                self.ta_eval_list.append(ta_eval_class)

        return self.ta_eval_list

    def finalize(self):
        ta_analysis_note_counter = 0
        # TA analysis
        for evaluated in self.ta_eval_list:
            self.ta_final_eval += evaluated.get_eval_note() * evaluated.get_pertinence()
            ta_analysis_note_counter += evaluated.get_pertinence()

        if ta_analysis_note_counter > 0:
            self.ta_final_eval /= ta_analysis_note_counter
        else:
            self.ta_final_eval = START_EVAL_NOTE

        # Social analysis
        social_analysis_note_counter = 0
        for evaluated in self.social_eval_list:
            self.social_final_eval += evaluated.get_eval_note() * evaluated.get_pertinence()
            social_analysis_note_counter += evaluated.get_pertinence()

        if social_analysis_note_counter > 0:
            self.social_final_eval /= social_analysis_note_counter
        else:
            self.social_final_eval = START_EVAL_NOTE

        # TODO
        self.final_eval = (self.ta_final_eval * EvaluatorsPertinence.TAEvaluator.value
                           + self.social_final_eval * EvaluatorsPertinence.SocialEvaluator.value)
        self.final_eval /= (EvaluatorsPertinence.TAEvaluator.value + EvaluatorsPertinence.SocialEvaluator.value)

        # TODO : temp
        if self.final_eval < 0.2:
            self.set_state(EvaluatorStates.VERY_LONG)
        elif self.final_eval < 0.4:
            self.set_state(EvaluatorStates.LONG)
        elif self.final_eval < 0.6:
            self.set_state(EvaluatorStates.NEUTRAL)
        elif self.final_eval < 0.8:
            self.set_state(EvaluatorStates.SHORT)
        else:
            self.set_state(EvaluatorStates.VERY_SHORT)
