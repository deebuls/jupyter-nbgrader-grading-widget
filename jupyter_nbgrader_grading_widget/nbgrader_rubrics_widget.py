#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path, PurePath
import glob
import json
import itertools
import pandas as pd
import numpy as np
import os
import copy
from IPython.display import display, clear_output
from ipywidgets import widgets, Label
from ipywidgets import Button, HBox, VBox, Box, Layout, Tab
from colorama import Fore, Back, Style

from .grading_widget import GradingWidget
from .single_question_answer_feedbacks import SingleQuestionAnswerFeedbacks


class NbgraderGradingTab:

    def __init__(self):

        # Constants

        self.GRADEBOOK_COLS = [
            'student_id',
            'answer_id',
            'question',
            'answer',
            'points',
            'graded_flag',
            'grade',
            'feedback_list',
            ]
        self.MAX_POINTS_WHEN_NOT_GIVEN = 3

        self.sample = None
        self.exam_solutions = None

        self.nbgrader_folder_path = None
        self.exam_file_name = None
        

    def display(self):

        path_selection_output = widgets.Output()
        grading_output = widgets.Output()
        summary_output = widgets.Output()
        with path_selection_output:  # info
            print ('System Overview')
            self.dashboard_path()
        with grading_output:  # Grading
            self.dashboard_grading()

        tab = widgets.Tab(children=[path_selection_output,
                          grading_output, summary_output])
        tab.set_title(0, 'Path')
        tab.set_title(1, 'Grading')
        tab.set_title(2, 'Summary')
        display(tab)

    def save_single_jupyter_notebooks(self):
        update_file_name = ''
        update_flag = False
        filenames = sorted(Path(self.nbgrader_folder_path).glob('**/'
            + self.exam_file_name+'.ipynb'))
        for student_id, filename in enumerate(filenames):
            if (student_id == self.sample.student):
                with open(filename) as f:
                    data = json.load(f)

                for index,cell in enumerate(data['cells']):
                    if 'nbgrader' in cell['metadata'] and (cell['metadata'
                        ]['nbgrader']['solution'])==True :
                        if (index == self.sample.index):
                            update_file_name = filename
                            data['cells'][index]['metadata'
                                ]['nbgrader']['grade'] = str(self.sample.grade)
                            data['cells'][index]['metadata'
                                ]['nbgrader']['graded_flag'] = True
                            data['cells'][index]['metadata'
                                ]['nbgrader']['feedback'] = self.sample.feedback
                            update_flag = True
                            break

            if update_flag:
                #break outer loop
                break
        if update_flag:
            with open(update_file_name, "w") as f:
                json.dump(data, f, indent=4)

    def check_folder_structure(self, nbgrader_submitted_folder_path,
                               exam_file_name):

        filenames = list(Path(nbgrader_submitted_folder_path).glob('**/'
                          + exam_file_name + '*.ipynb'))

    # TODO
    # Do rigiourous folder structre checking and question answer checking
    # if all question are present in all notebooks
    # if found error susggest the solutions

        if filenames:
            print (Fore.GREEN + 'Jupyter notebooks found')
            print ('Number of ipynb files: ', len(filenames))
            return True

        else:
            print (Fore.RED \
                + 'No files in folder!! please check folder and exam name')
            print (Style.RESET_ALL)
            return False

    def parse_jupyter_notebooks(self, nbgrader_submitted_folder_path,
                                exam_file_name):
        ''' parses jupyter notebooks based on some assumptions


        ....|grade | solution | points | cell type|
        ....|------|----------|--------|----------|
        ....|True  |True      |present |answer  |
        ....|True  |False     |present |test    |
        ....|False |True      |None    |code    |
        ....|False |False     |None    |question|

        '''

        lst = []

        for (student_id, filename) in \
            enumerate(sorted(Path(nbgrader_submitted_folder_path).glob('**/'
                       + exam_file_name + '.ipynb'))):
            with open(filename) as f:
                data = json.load(f)

            previous_question = None
            for (index, cell) in enumerate(data['cells']):
                if 'nbgrader' in cell['metadata'] and cell['metadata'
                        ]['nbgrader']['solution'] == False \
                    and cell['metadata']['nbgrader']['grade'] == False:
                    # This is a question cell
                    previous_question = (cell['source'
                            ][0] if cell['source'] else None)  # check if question is present

                if 'nbgrader' in cell['metadata'] and cell['metadata'
                        ]['nbgrader']['solution'] == True:

                    try:
                        if cell['source']:
                           answer = ""
                           for text in cell['source']:
                              answer += text 
                        else:
                           answer = None  # check if answer is present

                        question = previous_question
                    except:
                        print ('ERROR: Cannot parse the exam. Parser needs to be debugged')
                        continue

                    try:
                        point = int(cell['metadata']['nbgrader']['points'])
                    except:
                        point = self.MAX_POINTS_WHEN_NOT_GIVEN

                    try:
                        graded_points = int(cell['metadata']['nbgrader'
                                ]['graded_points'])
                        graded_flag = True
                    except:
                        graded_points = point
                        graded_flag = False
                    try:
                        feedbacks = cell['metadata']['nbgrader'
                                ]['feedback']
                    except:
                        feedbacks = []

                    lst.append([
                        student_id,
                        index,
                        question,
                        answer,
                        point,
                        graded_flag,
                        graded_points,
                        feedbacks,
                        ])

        self.exam_solutions = pd.DataFrame(lst, columns=self.GRADEBOOK_COLS)
        self.exam_solutions = self.exam_solutions.astype(dtype={'points': 'int8',
                'student_id': 'int8', 'answer_id': 'int8'})


    def create_rubrics_feedback(self, answer_sample_object,
                                grade_button):

        def on_feedback_change(name, change):
            answer_sample_object.update(name, change)
            grade_button.description = 'grade : ' \
                + str(answer_sample_object.grade)

        def on_feedback_text_change(name, change):
            answer_sample_object.feedback_update(name, change)

        items_layout = Layout(width='auto')

        box_layout = Layout(display='flex', flex_flow='column',
                            align_items='stretch')
        row_layout = Layout(display='flex', flex_flow='row',
                            align_items='stretch')
        combined_list = []
        for point in range(answer_sample_object.points):
            c = \
                widgets.Checkbox(name=answer_sample_object.feedback_checkbox[point],
                                 value=False, description='-1',
                                 disabled=False, layout=items_layout)
            c.observe(lambda x, point=point: on_feedback_change(point,
                      x), names='value')

            d = widgets.Text(name=point,
                             value=answer_sample_object.feedback[point],
                             placeholder='Type something',
                             layout=items_layout)
            d.observe(lambda x, point=point: \
                      on_feedback_text_change(point, x), names='value')
            combined_list.append(Box([c, d], layout=row_layout))

        return Box(combined_list, layout=box_layout)


    def get_exam_to_grade(self, direction=None):
        exam = self.exam_solutions
        if not self.sample:
            df = exam[exam['graded_flag'] == False]
            selection = df.iloc[0] if not df.empty else None
        else:
            previous = self.sample

            if not direction or ('next' == direction):
                df = exam[(exam['question'] == previous.question_text) & \
                        (exam['student_id'] == previous.student + 1)]
                if not df.empty:
                    selection = df.iloc[0] #first in selection
                else:
                    #Reached last answer of current question
                    #Now go to first student next question
                    df = exam[(exam['question'] == previous.question_text) & \
                            (exam['student_id'] == 0)]#First student
                    if not df.empty:
                        if (df.iloc[0].name + 1) in exam.index:
                            selection = exam.iloc[df.iloc[0].name + 1]
                        else:
                            df = exam[exam['graded_flag'] == False]
                            selection = df.iloc[0] if not df.empty else None
                    else:
                        df = exam[exam['graded_flag'] == False]
                        selection = df.iloc[0] if not df.empty else None
            elif 'previous' == direction:
                df = exam[(exam['question'] == previous.question_text) & \
                        (exam['student_id'] == previous.student - 1)]
                if not df.empty:
                    selection = df.iloc[0] #first in selection
                else:
                    #reached first student answer
                    #Now go to last student next question
                    last_student_id = exam.iloc[-1].student_id
                    df = exam[(exam['question'] == previous.question_text) & \
                            (exam['student_id'] == last_student_id)]
                    if not df.empty:
                        if (df.iloc[0].name - 1) in exam.index:
                            selection = exam.iloc[df.iloc[0].name - 1]
                        else:
                            df = exam[exam['graded_flag'] == False]
                            selection = df.iloc[0] if not df.empty else None
                    else:
                        df = exam[exam['graded_flag'] == False]
                        selection = df.iloc[0] if not df.empty else None
            elif 'next_question' == direction:
                if (previous.name + 1) in exam.index:
                    selection = exam.iloc[previous.name + 1]
                else:
                    df = exam[exam['graded_flag'] == False]
                    selection = df.iloc[0] if not df.empty else None

            elif 'previous_question' == direction:
                if (previous.name - 1) in exam.index:
                    selection = exam.iloc[previous.name - 1]
                else:
                    df = exam[exam['graded_flag'] == False]
                    selection = df.iloc[0] if not df.empty else None
            else:
                df = exam[exam['graded_flag'] == False]
                selection = df.iloc[0] if not df.empty else None

        one_sample = SingleQuestionAnswerFeedbacks(selection)
        return one_sample

    def single_question_grading_view(self, direction=None):

        self.sample = self.get_exam_to_grade(direction)

        row_layout = Layout(display='Flex', flex_flow='row',
                            align_items='stretch', width='100%')
        col_layout = Layout(display='flex', flex_flow='column',
                            align_items='stretch', border='solid',
                            width='100%')

        question = widgets.Textarea(value=self.sample.question_text,
                                    placeholder='Type something',
                                    disabled=True,
                                    layout=Layout(width='90%'),
                                    continuous_update=True)

        answer = widgets.Textarea(value=self.sample.answer_text,
                                  placeholder='Answer missing',
                                  disabled=True,
                                  layout=Layout(width='60%',
                                  height='200px',
                                  continuous_update=True))

    # TODO Fix this 100px to auto

        zero_button = Button(description='zero points',
                             layout=Layout(width='20%'))
        grade_button = Button(description='grade : '
                              + str(self.sample.grade),
                              layout=Layout(width='20%'),
                              continuous_update=True)
        increase_button = Button(description='add points',
                                 layout=Layout(width='20%'))
        next_button = Button(description='next',
                             layout=Layout(width='20%'))
        previous_button = Button(description='previous',
                                 layout=Layout(width='20%'))

        feedback = widgets.Output(description='feedback output')
        with feedback:
            fd = self.create_rubrics_feedback(self.sample, grade_button)
            display(fd)
        row_1 = Box([answer, feedback], layout=row_layout)
        row_2 = Box([previous_button, zero_button, grade_button,
                    next_button], layout=row_layout)
        complete = Box([question, row_1, row_2], layout=col_layout)

        def on_save_button(change):
            self.save_single_jupyter_notebooks()
            self.sample = self.get_exam_to_grade()
            question.value = self.sample.question_text
            answer.value = self.sample.answer_text
            with feedback:
                clear_output()
                fd = self.create_rubrics_feedback(self.sample,
                        grade_button)
                display(fd)
            grade_button.value = 'grade : ' + str(self.sample.grade)

        def on_zero_button(change):
            self.sample.grade = 0
            self.save_single_jupyter_notebooks()
            self.sample = self.get_exam_to_grade()
            question.value = self.sample.question_text
            answer.value = self.sample.answer_text
            with feedback:
                clear_output()
                fd = self.create_rubrics_feedback(self.sample,
                        grade_button)
                display(fd)
            grade_button.description = 'grade : ' \
                + str(self.sample.grade)

        def on_increase_button(change):
            self.sample.grade += 1
            grade_button.description = 'grade : ' \
                + str(self.sample.grade)

        def on_next_button(change):
            self.sample = self.get_exam_to_grade('next')
            question.value = self.sample.question_text
            answer.value = self.sample.answer_text
            with feedback:
                clear_output()
                fd = self.create_rubrics_feedback(self.sample,
                        grade_button)
                display(fd)
            grade_button.value = 'grade : ' + str(self.sample.grade)

        def on_previous_button(change):
            self.sample = self.get_exam_to_grade('previous')
            question.value = self.sample.question_text
            answer.value = self.sample.answer_text
            with feedback:
                clear_output()
                fd = self.create_rubrics_feedback(self.sample,
                        grade_button)
                display(fd)
            grade_button.value = 'grade : ' + str(self.sample.grade)

        grade_button.on_click(on_save_button)
        zero_button.on_click(on_zero_button)
        increase_button.on_click(on_increase_button)
        next_button.on_click(on_next_button)
        previous_button.on_click(on_previous_button)
        return complete

    def dashboard_grading(self):
        single_question_output = \
            widgets.Output(description='Single Question')
        if self.check_folder_structure(self.nbgrader_folder_path,
            self.exam_file_name):
            self.parse_jupyter_notebooks(self.nbgrader_folder_path,
                            self.exam_file_name)
        else:
            print ('Please select the proper folder')
            pass

        clear_output()
        row_layout = Layout(display='Flex', flex_flow='row',
                            align_items='stretch', width='100%')
        col_layout = Layout(display='flex', flex_flow='column',
                            align_items='stretch', border='solid',
                            width='100%')
        previous_question_button = \
            Button(description='Previous Question',
                   layout=Layout(width='50%'))
        next_question_button = Button(description='Next Question',
                layout=Layout(width='50%'))

        with single_question_output:
            clear_output()
            question_view = self.single_question_grading_view()
            display(question_view)
        row_2 = Box([previous_question_button, next_question_button],
                    layout=row_layout)

        complete = Box([row_2, single_question_output],
                       layout=col_layout)
        display(complete)

        def on_next_question_button(change):
            with single_question_output:
                clear_output()
                question_view = self.single_question_grading_view('next_question')
                display(question_view)

        def on_previous_question_button(change):
            with single_question_output:
                clear_output()
                question_view = self.single_question_grading_view('previous_question')
                display(question_view)

        next_question_button.on_click(on_next_question_button)
        previous_question_button.on_click(on_previous_question_button)




    def dashboard_path(self):
        layout = {
            'width': '90%',
            'height': '50px',
            'border': 'solid',
            'fontcolor': 'lightgreen',
            }
        layout_two = {
            'width': '100%',
            'height': '200px',
            'border': 'solid',
            'fontcolor': 'lightgreen',
            }
        style_green = {'handle_color': 'green', 'readout_color': 'red',
                       'slider_color': 'blue'}
        style_blue = {'handle_color': 'blue', 'readout_color': 'red',
                      'slider_color': 'blue'}

        nbgrader_folder_path = widgets.Text(value='./nn-2019-dataset',
                placeholder='Type something', description='Path:',
                disabled=False, layout=layout)
        exam_file_name = widgets.Text(value='NN_Exam_WS18',
                placeholder='Type something', description='Path:',
                disabled=False, layout=layout)  # value='/path/to/nbgrader/folder/submission',
        self.nbgrader_folder_path = nbgrader_folder_path.value
        self.exam_file_name = exam_file_name.value
        display(nbgrader_folder_path)
        display(exam_file_name)

        print ('Press button to check if folder is in correct format')
        button = widgets.Button(description='Check', style=style_blue)

        display(button)
        out = widgets.Output()
        display(out)

        def on_button_clicked(b):
            with out:
                clear_output()
                print ('checking folder: ', nbgrader_folder_path.value)
                if self.check_folder_structure(nbgrader_folder_path.value,
                    exam_file_name.value):
                    button.button_style = 'success'
                else:
                    button.button_style = 'danger'

        button.on_click(on_button_clicked)

