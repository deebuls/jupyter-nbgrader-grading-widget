

class SingleQuestionAnswerFeedbacks:
    """Class for storing single Question with its Answer and Feedbacks

       Its provides callback for the checkbox feeback and feedback comments
       per question
    """
    def __init__(self, one_answer_series):
        """__init__ method initializes the values

        Args:
            one_answer_series(pandas.Series) : 1 sample from the dataset
        """
        self.name = one_answer_series.name
        self.index = one_answer_series.answer_id
        self.student = one_answer_series.student_id
        self.question_text = one_answer_series.question
        self.answer_text = one_answer_series.answer
        self.points = one_answer_series.points
        self.grade = one_answer_series.points
        self.feedback_checkbox = [False for i in range(self.points)]
        self.feedback = ["No feedback" for i in range(self.points)]

        for fb, checkbox_index in zip(one_answer_series.feedback_list, range(self.points)):
            self.feedback_checkbox[checkbox_index] = True #with feedback make it true
            self.feedback[checkbox_index] = fb

    def update(self, feedback_index, change) -> None:
        """ update method is callback for checkbox widget

	updates the grade value bases on checkbox
	"""
        print(change)
        self.feedback_checkbox[feedback_index] = change['new']
        if (False == change['old'] and True == change['new']):
            self.grade -= 1
        elif (True == change['old'] and False == change['new']):
            self.grade += 1
        else:
            #no change it was clicked again
            pass

    def feedback_update(self, feedback_index, change) -> None:
        """ feedback_update method is callback for text change in feedback

	updates the feedback text  value bases on textbox widget
	"""
        self.feedback[feedback_index] = change['new']
