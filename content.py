import sys, html, random, requests, json
import PyQt5.QtWidgets as py
from PyQt5.QtCore import QThread, pyqtSignal
from deep_translator import GoogleTranslator

class QuestionWorker(QThread):
    question_ready = pyqtSignal(list)
    
    def __init__(self, count=5):
        super().__init__()
        self.count = count
    
    def run(self):
        batch = []
        url = f"https://opentdb.com/api.php?amount={self.count}&category=9&difficulty=medium&type=multiple"
        try:
            response = requests.get(url)
            # print("khs")
            if response.status_code == 200:
                data = response.json()["results"]
                # print(data)
                for item in data:
                    # print(item)
                    question_eng = html.unescape(item["question"])
                    incorrect = html.unescape(item["incorrect_answers"])
                    correct_eng =  html.unescape(item["correct_answer"])
                    correct = GoogleTranslator(source="en", target="it").translate(correct_eng)
                    options = [correct_eng] + incorrect
                    question = GoogleTranslator(source="en", target="it").translate(question_eng)
                    shuffled = random.sample(options, k=len(options))
                    translated_options = []
                    for _, d in enumerate(shuffled):
                        translated_options.append(GoogleTranslator(source="en", target="it").translate(d))
                    batch.append({"question": question, "options": translated_options, "answer": correct, "answered": False})
        except Exception as e:
            print(f"Worker error {e}")
        # print("batch")
        self.question_ready.emit(batch)

class QuizApp(py.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz app")
        self.setGeometry(600, 600, 400, 300)
        
        self.index = 0
        self.score = 0
        self.questions = []
        self.prev_answer = []

        self.layout = py.QVBoxLayout()
        self.setLayout(self.layout)
        
        self.label = py.QLabel("")
        self.layout.addWidget(self.label)
        
        self.result_label = py.QLabel("")
        self.layout.addWidget(self.result_label)
        
        self.correct_count = 0
        self.wrong_count = 0
        
        self.correct_count_text = py.QLabel("")
        self.layout.addWidget(self.correct_count_text)
        self.wrong_count_text = py.QLabel("")
        self.layout.addWidget(self.wrong_count_text)
        self.option_buttons = [] 
        self.right_answer = py.QLabel("")
        self.layout.addWidget(self.right_answer)
        
        self.next_btn = py.QPushButton("Next")
        self.next_btn.setStyleSheet("color: black; background-color: orange")
        self.next_btn.setFixedWidth(60)
        
        self.prev_btn = py.QPushButton("Previous")
        self.prev_btn.setStyleSheet("color: black; background-color: orange")
        self.prev_btn.setFixedWidth(70)
        
        
        self.next_btn.clicked.connect(self.next_question)
        self.layout.addWidget(self.next_btn)
        
        self.prev_btn.clicked.connect(self.prev_question)
        self.layout.addWidget(self.prev_btn)
        
        self.is_fetching = False
        self.call_load_question_again = False
        
        self.fetch_question(6)
        
        # self.question_option = self.get_question()
        self.load_question()
    
    def fetch_question(self, count=5):
        if not self.is_fetching:
            self.is_fetching = True
            self.worker = QuestionWorker(count)
            self.worker.question_ready.connect(self.add_question)
            self.worker.question_ready.connect(lambda: setattr(self, "is_fetching", False))
            self.worker.start()
        else:
            print("non entroooooooo")
    
    def add_question(self, batch):
        # print(batch)
        self.questions.extend(batch)
        if self.index == 0 and len(self.questions) > 0 or self.call_load_question_again:
            self.call_load_question_again = False
            self.load_question()
   
    def load_question(self, from_go_back=False):
        # print(self.questions)
        if self.index >= len(self.questions):
            self.label.setText("Loading question")
            self.call_load_question_again = True
            return
        
        q = self.questions[self.index]["question"]
        options = self.questions[self.index]["options"]
        self.label.setText(q)
        self.label.setStyleSheet("font-size: large; font-weight: bold")
        #set the font to be bigger
        if len(self.option_buttons) > 0:
            for _, btt in enumerate(self.option_buttons):
                self.layout.removeWidget(btt)
            self.option_buttons = []

        for _ in range(len(self.questions[self.index]["options"])):
            btn = py.QPushButton("")
            btn.clicked.connect(self.check_answer)
            btn.setStyleSheet("color: black")
            self.layout.addWidget(btn)
            self.option_buttons.append(btn)
        for i, option in enumerate(options):
            self.option_buttons[i].setText(option)
            
        if from_go_back:
            self.index += 1
    
    def go_back(self):
        if self.index == 0:
            return
        self.index -= 1
        self.load_question()
        
        if self.prev_answer[self.index]["wrong"]:
            for btn in self.option_buttons:
                # print(self.prev_answer[self.index]["wrong"])
                if btn.text() == self.questions[self.index]["answer"]:
                    btn.setStyleSheet("background-color: lightgreen; color: black") 
                if btn.text() == self.prev_answer[self.index]["wrong_answer"]:
                    btn.setStyleSheet("background-color: #FF7F7F; color: black")
        else:
            for btn in self.option_buttons:
                # print(self.prev_answer[self.index]["wrong"])
                if btn.text() == self.questions[self.index]["answer"]:
                    btn.setStyleSheet("background-color: lightgreen; color: black") 
                btn.setEnabled(False)     
    
    def next_question(self):
        # print("djfj")
        self.result_label.setText("")
        self.load_question()
        
    def prev_question(self):
        self.result_label.setText("")
        self.go_back()

    def check_answer(self):
        sender = self.sender()
        # print(sender)
        if self.index > len(self.questions):
            self.label.setText("Loading question")
            self.call_load_question_again = True
            return
        if self.questions[self.index]["answered"]:
            return
        
        if sender.text() == self.questions[self.index]["answer"]:
            self.score += 1
            # self.result_label.setText("Correct!")
            # self.result_label.setStyleSheet("color: green; font-size: 19px; font-weight: bold")
            self.correct_count += 1
            self.correct_count_text.setText(f"You have answered {self.correct_count} correctly")
            self.wrong_count_text.setText(f"You have answered {self.wrong_count} wrongly")
            self.right_answer.setText("")
            for btn in self.option_buttons:
                if btn.text() == self.questions[self.index]["answer"]:
                    btn.setStyleSheet("background-color: lightgreen; color: black")
            # sender.
            self.prev_answer.append({"wrong": False, "wrong_answer": ""})
            self.questions[self.index]["answered"] = True
        else:
            self.wrong_count += 1
            self.correct_count_text.setText(f"You have answered {self.correct_count} correctly")
            self.wrong_count_text.setText(f"You have answered {self.wrong_count} wrongly")
            # self.result_label.setText("Wrong!")
            # self.right_answer.setText(f"The correct answer was {self.questions[self.index]["answer"]}")
            self.right_answer.setStyleSheet("color: orange; font-size: 10px; font-weight: bold")
            # self.result_label.setStyleSheet("color: red; font-size: 19px; font-weight: bold")
            for btn in self.option_buttons:
                if btn.text() == self.questions[self.index]["answer"]:
                    btn.setStyleSheet("background-color: lightgreen; color: black") 
                if btn.text() == sender.text():
                    btn.setStyleSheet("background-color: #FF7F7F; color: black")
            self.prev_answer.append({"wrong": True, "wrong_answer": f"{sender.text()}"})
            self.questions[self.index]["answered"] = True
        self.index += 1

        for btn in self.option_buttons:
            btn.setEnabled(False)
        
        if len(self.questions) - self.index <= 5:
            self.fetch_question(2)
            
        # self.load_question()
        
if __name__ == "__main__":
    app = py.QApplication(sys.argv)
    window = QuizApp()
    window.show()
    sys.exit(app.exec_())
    
# put a next button so that so the user clicks it to go the next question
# if the answer is wrong color the answer with red and the right answer in green
# but if correct color the option chosen in green
# also add a previous button to go back
# change the app icon

#https://github.com/StanleyAnyas/traity.git