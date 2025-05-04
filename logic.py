from PyQt6.QtWidgets import *
from gui import *
import csv


class Logic(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Connect the submit button to the function submit_scores. This function will take some inputs
        self.button_submit.clicked.connect(self.submit_scores)

    def submit_scores(self):
        """
        Collects the inputs, converts run time to seconds, updates score label.
        """
        dod_id = self.input_dodid.text()
        if not dod_id.isdigit() or len(dod_id) != 6:
            self.label_validation.setStyleSheet("color: red;")
            self.label_validation.setText("DoD ID must be 6 digits.")
            return

        pushups = self.spinbox_pushups.value()
        situps = self.spinbox_situps.value()
        run_time = self.timebox_input_run_time.time()
        run_seconds = run_time.minute() * 60 + run_time.second()  # Google/gemini to find PyQT6 built in methods for .second/.minute

        # Stores the final score here
        final_score = self.calculate_scores(pushups, situps, run_seconds)

        # Updates the score label
        self.label_score.setText(f'Your Score: {final_score:.1f}%')

        # Checks to see if DoD id already exists before writing final scores.
        try:
            with open("pt_scores.csv", "r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == dod_id:
                        self.label_validation.setStyleSheet("color: red;")
                        self.label_validation.setText("This DoD ID has already been recorded.")
                        return
        except FileNotFoundError: # If the file does not exist, it is ok; a new one will be created.
            pass

        # Creates a csv file that appends user id and final score.
        with open("pt_scores.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([dod_id, final_score])

            self.input_dodid.clear()  # Resets the ID field after recording data to csv.

    def score_pushups(self, pushups: int) -> float:
        """
        A dictionary for number of pushups and their corresponding points awards.
        :param pushups: Number of pushups.
        :return: Score depending on the number of pushups.
        """
        pushup_scores = {
            67: 20.0, 66: 19.8, 65: 19.6, 64: 19.4, 63: 19.2, 62: 19.0, 61: 18.8,
            60: 18.6, 59: 18.4, 58: 18.2, 57: 18.0, 56: 17.8, 55: 17.7, 54: 17.6,
            53: 17.6, 52: 17.2, 51: 17.0, 50: 16.8, 49: 16.4, 48: 16.2, 47: 16.0,
            46: 15.6, 45: 15.4, 44: 15.0, 43: 14.6, 42: 14.2, 41: 14.0, 40: 13.8,
            39: 13.0, 38: 12.6, 37: 12.0, 36: 11.6, 35: 11.2, 34: 11.0, 33: 10.8,
            32: 7.0, 31: 4.0, 30: 1.0
        }

        # Cap the maximum score at 20.0 even if reps exceed max of 67. Then returns the value of the dictionary key.
        if pushups >= 67:
            return 20.0
        elif pushups < 30:
            return 0.0  # Below the minimum standard, awards no points.
        else:
            return pushup_scores.get(pushups,
                                     0.0)  # Google/gemini for defaulting to 0.0 due to crashing if the value did not exist

    def score_situps(self, situps: int) -> float:
        """
        A dictionary for number of situps and their corresponding points awards.
        :param situps: Number of situps.
        :return: Score depending on the number of situps.
        """
        situp_scores = {
            58: 20.0, 57: 19.7, 56: 19.4, 55: 19.0, 54: 18.8, 53: 18.4,
            52: 18.0, 51: 17.6, 50: 17.4, 49: 17.0, 48: 16.6, 47: 16.0,
            46: 15.0, 45: 14.0, 44: 13.0, 43: 12.6, 42: 12.0, 41: 9.0,
            40: 6.0, 39: 3.0  # 39 situps is minimum
        }

        # Sets max and min point awards
        if situps >= 58:
            return 20.0
        elif situps < 39:
            return 0.0
        else:
            return situp_scores.get(situps, 0.0)  # Defaults to 0.0 if no valid value

    def score_run_time(self, run_seconds: int) -> float:
        """
        A tuple list with run time in seconds and their corresponding points awards.
        :param run_seconds: Input for run time in seconds.
        :return:
        """
        # Google/gemini for converting run times in format from minutes:seconds into seconds
        run_score_table = [
            (552, 60.0),  # ≤ 9:12, this is the best
            (574, 59.5),  # 9:13 - 9:34
            (585, 59.0),  # 9:35 - 9:45
            (598, 58.5),  # 9:46 - 9:58
            (610, 58.0),  # 9:59 - 10:10
            (623, 57.5),  # 10:11 - 10:23
            (637, 57.0),  # 10:24 - 10:37
            (651, 56.5),  # 10:38 - 10:51
            (666, 56.0),  # 10:52 - 11:06
            (682, 55.5),  # 11:07 - 11:22
            (698, 55.0),  # 11:23 - 11:38
            (716, 54.5),  # 11:39 - 11:56
            (734, 54.0),  # 11:57 - 12:14
            (753, 53.5),  # 12:15 - 12:33
            (773, 52.0),  # 12:34 - 12:53
            (794, 50.5),  # 12:54 - 13:14
            (816, 49.0),  # 13:15 - 13:36
            (840, 46.5),  # 13:37 - 14:00
            (865, 44.0),  # 14:01 - 14:25
            (892, 41.0),  # 14:26 - 14:52
            (920, 38.0),  # 14:53 - 15:20
            (950, 35.0),  # 15:21 - 15:50, this is the worst
        ]

        # Loop: finds the first range where run time is less than or eq to the max allowed time (15:50).
        for max_time, score in run_score_table:
            if run_seconds <= max_time:
                return score
        return 0.0

    def calculate_scores(self, pushups: int, situps: int, run_seconds: int) -> float:
        """
        :param pushups: Number of pushups.
        :param situps: Number of situps.
        :param run_seconds: Amount of run time in seconds.
        :return: Add the three scores together.
        """
        pushup_score = self.score_pushups(pushups)
        situp_score = self.score_situps(situps)
        run_score = self.score_run_time(run_seconds)

        total_score = pushup_score + situp_score + run_score
        return total_score
