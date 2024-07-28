import tkinter as tk
import pandas as pd
import pyttsx3
import speech_recognition as sr

class ChatbotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gov Infohub")
        self.master.geometry("400x600")
        
        self.auto_read_details = True

        self.chat_frame = tk.Frame(self.master)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Adding a styled label for the heading
        heading_label = tk.Label(self.chat_frame, text="Government Infohub Assistant", font=("Helvetica", 14, "bold"), fg="#333", pady=4)
        heading_label.pack()

        self.chat_text = tk.Text(self.chat_frame, wrap=tk.WORD, spacing1=5, spacing2=5)
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        self.chat_text.config(state=tk.DISABLED)

        self.entry_frame = tk.Frame(self.master, bg="#f0f0f0")
        self.entry_frame.pack(fill=tk.X, padx=10, pady=10)

        self.user_entry = tk.Entry(self.entry_frame)
        self.user_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT)

        voice_button = tk.Button(self.entry_frame, text="Speak", command=self.toggle_voice)
        voice_button.pack(side=tk.LEFT)

        listen_button = tk.Button(self.entry_frame, text="Listen", command=self.listen_last_output)
        listen_button.pack(side=tk.LEFT)

        # back_button = tk.Button(self.entry_frame, text="Back", command=self.go_back)
        # back_button.pack(side=tk.LEFT)

        start_button = tk.Button(self.entry_frame, text="Main Menu", command=self.start_conversation)
        start_button.pack(side=tk.LEFT)

        # Load data from CSV file
        self.data = pd.read_csv("schemes.csv")
        self.insurance_data = pd.read_csv("insurance.csv")
        self.cards_data = pd.read_csv("cards.csv")
        self.scholarships_data = pd.read_csv("scholarships.csv")

        self.selected_dataset = None
        self.selected_sector = None
        self.selected_category = None
        self.selected_item = None
        self.selected_scheme = None
        self.last_output = None
        self.selected_doc = None
        self.selected_based = None
        self.selected_name = None
        self.display_dataset_selection()

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()

        # Flag to track voice mode
        self.voice_mode = False

    def start_conversation(self):

        self.selected_dataset = None
        self.selected_sector = None
        self.selected_category = None
        self.selected_item = None
        self.selected_scheme = None
        self.last_output = None
        self.selected_doc = None
        self.selected_based = None
        self.selected_name = None

        self.display_dataset_selection()

    def listen_last_output(self):
        # Check if the chatbot should automatically read the details
        if self.auto_read_details:
            # Search for the last "Chatbot:" message in the text widget
            last_chatbot_message_index = self.chat_text.search("Chatbot:", tk.END, backwards=True, regexp=True)

            if last_chatbot_message_index:
                # Get the text from the last "Chatbot:" message to the end
                last_output = self.chat_text.get(last_chatbot_message_index, tk.END).strip()

                # Read the last output using text-to-speech engine
                self.speak(last_output)
            else:
                self.display_message("Chatbot: No previous output to listen.")
        else:
            self.display_message("Chatbot: Press the 'Listen' button after a response to hear the details.")

    def display_dataset_selection(self):
        dataset_message = "Chatbot: Welcome! Please choose a domain:\n1. Government Schemes\n2. Insurance\n3. Cards\n4. Scholarships"
        self.display_message(dataset_message)

    def select_dataset(self, dataset_index):
        if dataset_index == 1:
            self.selected_dataset = 'schemes'
            self.display_initial_message()
        elif dataset_index == 2:
            self.selected_dataset = 'insurance'
            self.display_insurance_sectors()
        elif dataset_index == 3:
            self.selected_dataset = 'cards'
            self.display_cards_category()
        elif dataset_index == 4:
            self.selected_dataset = 'scholarships'
            self.display_scholarships_based()
        else:
            self.display_message("Chatbot: Invalid domain selection.")

    def send_message(self):

        user_input = self.user_entry.get()
        if user_input:

            if not self.selected_dataset:
                try:
                    dataset_index = int(user_input)
                    self.select_dataset(dataset_index)
                except (ValueError, IndexError):
                    self.display_message("Chatbot: Please enter a valid domain.")
                    
            elif self.selected_dataset == 'insurance':
                if not self.selected_sector:
                    try:
                        selected_index = int(user_input) - 1
                        self.selected_sector = self.insurance_data['Sector'].unique()[selected_index]
                        self.display_schemes_insurance()
                    except (ValueError, IndexError):
                        self.display_message("Chatbot: Please enter a valid sector for insurance.")

                elif not self.selected_scheme:
                    # Process user input to select a scheme
                    try:
                        selected_index = int(user_input) - 1
                        schemes = self.insurance_data[self.insurance_data['Sector'] == self.selected_sector]['Scheme Name'].unique()
                        self.selected_scheme = schemes[selected_index]
                        self.display_scheme_details_insurance()
                    except (ValueError, IndexError):
                        self.display_message("Chatbot: Please enter a valid scheme name for insurance.")
                
                else:
                    # Display other columns as options
                    response = self.get_response_insurance(user_input)
                    self.display_message(f"Chatbot: {response}")
                    # self.speak(response)

                    self.last_output = response
                    self.auto_read_details = True

            elif self.selected_dataset == 'scholarships':
                if not self.selected_based:
                    try:
                        selected_index = int(user_input) - 1
                        self.selected_based = self.scholarships_data['Based On'].unique()[selected_index]
                        self.display_schemes_scholarships()
                    except (ValueError, IndexError):
                        self.display_message("Chatbot: Please enter a valid category for scholarships.")

                elif not self.selected_name:
                    # Process user input to select a scheme
                    try:
                        selected_index = int(user_input) - 1
                        scholarship = self.scholarships_data[self.scholarships_data['Based On'] == self.selected_based]['Scholarship Name'].unique()
                        self.selected_name = scholarship[selected_index]
                        self.display_details_scholarships()
                    except (ValueError, IndexError):
                        self.display_message("Chatbot: Please enter a valid scholarship name.")
                
                else:
                    # Display other columns as options
                    response = self.get_response_scholarships(user_input)
                    self.display_message(f"Chatbot: {response}")
                    # self.speak(response)

                    self.last_output = response
                    self.auto_read_details = True


            elif self.selected_dataset == 'cards':
                if not self.selected_category:
                    try:
                        selected_index = int(user_input) - 1
                        self.selected_category = self.cards_data['Category'].unique()[selected_index]
                        self.display_schemes_cards()
                    except (ValueError, IndexError):
                        self.display_message("Chatbot: Please enter a valid Category for cards.")

                elif not self.selected_doc:
                    # Process user input to select a scheme
                    try:
                        selected_index = int(user_input) - 1
                        doc = self.cards_data[self.cards_data['Category'] == self.selected_category]['Type of Document'].unique()
                        self.selected_doc = doc[selected_index]
                        print("hell")
                        self.display_details_cards()
                        print("hi")
                    except (ValueError, IndexError):
                        self.display_message("Chatbot: Please enter a valid type of document for cards.")
                
                else:
                    # Display other columns as options
                    response = self.get_response_cards(user_input)
                    self.display_message(f"Chatbot: {response}")
                    # self.speak(response)

                    self.last_output = response
                    self.auto_read_details = True


            else:
                if not self.selected_sector:
                    # Process user input to select a sector
                    try:
                        selected_index = int(user_input) - 1
                        self.selected_sector = self.data['Sector'].unique()[selected_index]
                        self.display_schemes()
                    except (ValueError, IndexError):
                        self.display_message("Chatbot: Please enter a valid sector for government schemes.")
                elif not self.selected_scheme:
                    # Process user input to select a scheme
                    try:
                        selected_index = int(user_input) - 1
                        schemes = self.data[self.data['Sector'] == self.selected_sector]['Scheme Name'].unique()
                        self.selected_scheme = schemes[selected_index]
                        self.display_scheme_details()
                    except (ValueError, IndexError):
                        self.display_message("Chatbot: Please enter a valid scheme name for government schemes.")
                else:
                    # Display other columns as options
                    response = self.get_response(user_input)
                    self.display_message(f"Chatbot: {response}")
                    # self.speak(response)

                    # Update last_output after updating the display
                    self.last_output = response

                    # Set auto_read_details to False after the user has interacted
                    self.auto_read_details = True

            self.user_entry.delete(0, tk.END)  # Clear the entry field

    def speak(self, message):
        self.engine.say(message)
        self.engine.runAndWait()

    def display_schemes(self):
        schemes = self.data[self.data['Sector'] == self.selected_sector]['Scheme Name'].unique()
        scheme_message = f"Chatbot: Please choose a scheme name for '{self.selected_sector}':\n" + \
                         "\n".join([f"{i + 1}. {scheme}" for i, scheme in enumerate(schemes)])
        self.display_message(scheme_message)

    def display_schemes_insurance(self):
        schemes = self.insurance_data[self.insurance_data['Sector'] == self.selected_sector]['Scheme Name'].unique()
        scheme_message = f"Chatbot: Please choose a scheme name for '{self.selected_sector}':\n" + \
                         "\n".join([f"{i + 1}. {scheme}" for i, scheme in enumerate(schemes)])
        self.display_message(scheme_message)

    def display_schemes_cards(self):
        docs = self.cards_data[self.cards_data['Category'] == self.selected_category]['Type of Document'].unique()
        doc_message = f"Chatbot: Please choose a Type of document for '{self.selected_category}':\n" + \
                         "\n".join([f"{i + 1}. {doc}" for i, doc in enumerate(docs)])
        self.display_message(doc_message)
    
    def display_schemes_scholarships(self):
        names = self.scholarships_data[self.scholarships_data['Based On'] == self.selected_based]['Scholarship Name'].unique()
        print(names)
        name_message = f"Chatbot: Please choose a scholarship name for '{self.selected_based}':\n" + \
                         "\n".join([f"{i + 1}. {n}" for i, n in enumerate(names)])
        self.display_message(name_message)


    def display_scheme_details(self):
        scheme_details = self.data[(self.data['Sector'] == self.selected_sector) & (self.data['Scheme Name'] == self.selected_scheme)]
        columns_message = "Chatbot: Please choose an option:\n" + \
                          "\n".join([f"{i + 1}. {column}" for i, column in enumerate(scheme_details.columns[2:])])
        self.display_message(columns_message)
    
    def display_scheme_details_insurance(self):
        scheme_details = self.insurance_data[(self.insurance_data['Sector'] == self.selected_sector) & (self.insurance_data['Scheme Name'] == self.selected_scheme)]
        columns_message = "Chatbot: Please choose an option:\n" + \
                          "\n".join([f"{i + 1}. {column}" for i, column in enumerate(scheme_details.columns[2:])])
        self.display_message(columns_message)

    def display_details_cards(self):
        doc_details = self.cards_data[(self.cards_data['Category'] == self.selected_category) & (self.cards_data['Type of Document'] == self.selected_doc)]
        columns_message = "Chatbot: Please choose an option:\n" + \
                          "\n".join([f"{i + 1}. {column}" for i, column in enumerate(doc_details.columns[2:])])

        self.display_message(columns_message)

    def display_details_scholarships(self):
        name_details = self.scholarships_data[(self.scholarships_data['Based On'] == self.selected_based) & (self.scholarships_data['Scholarship Name'] == self.selected_name)]
        columns_message = "Chatbot: Please choose an option:\n" + \
                          "\n".join([f"{i + 1}. {column}" for i, column in enumerate(name_details.columns[2:])])

        self.display_message(columns_message)


    def get_response(self, user_input):
        if user_input.lower() == "back":
            self.go_back()
            return ""

        column_index = int(user_input) - 1
        scheme_details = self.data[(self.data['Sector'] == self.selected_sector) & (self.data['Scheme Name'] == self.selected_scheme)]
        column_name = scheme_details.columns[2:][column_index]
        result = scheme_details[column_name].iloc[0]
        return result
    
    def get_response_insurance(self, user_input):
        if user_input.lower() == "back":
            self.go_back()
            return ""

        column_index = int(user_input) - 1
        scheme_details = self.insurance_data[(self.insurance_data['Sector'] == self.selected_sector) & (self.insurance_data['Scheme Name'] == self.selected_scheme)]
        column_name = scheme_details.columns[2:][column_index]
        result = scheme_details[column_name].iloc[0]
        return result
    
    def get_response_cards(self, user_input):
        if user_input.lower() == "back":
            self.go_back()
            return ""

        column_index = int(user_input) - 1
        card_details = self.cards_data[(self.cards_data['Category'] == self.selected_category) & (self.cards_data['Type of Document'] == self.selected_doc)]
        column_name = card_details.columns[2:][column_index]
        result = card_details[column_name].iloc[0]
        print(result)
        return result
    
    def get_response_scholarships(self, user_input):
        if user_input.lower() == "back":
            self.go_back()
            return ""

        column_index = int(user_input) - 1
        name_details = self.scholarships_data[(self.scholarships_data['Based On'] == self.selected_based) & (self.scholarships_data['Scholarship Name'] == self.selected_name)]
        column_name = name_details.columns[2:][column_index]
        result = name_details[column_name].iloc[0]
        return result
        

    def display_message(self, message):
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"{message}\n\n", "chat_message")
        self.chat_text.tag_configure("chat_message", background="#f0f0f0")  # Light grey background
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

    def display_initial_message(self):
        sectors = self.data['Sector'].unique()
        initial_message = "Chatbot: Welcome! Please choose a sector for government schemes:\n" + "\n".join([f"{i + 1}. {sector}" for i, sector in enumerate(sectors)])
        self.display_message(initial_message)

    def display_insurance_sectors(self):
        sectors = self.insurance_data['Sector'].unique()
        initial_message = "Chatbot: Welcome! Please choose a sector for insurance:\n" + "\n".join([f"{i + 1}. {sector}" for i, sector in enumerate(sectors)])
        self.display_message(initial_message)

    def display_cards_category(self):
        category = self.cards_data['Category'].unique()
        initial_message = "Chatbot: Welcome! Please choose a category for cards:\n" + "\n".join([f"{i + 1}. {cate}" for i, cate in enumerate(category)])
        self.display_message(initial_message)

    def display_scholarships_based(self):
        based_on = self.scholarships_data['Based On'].unique()
        initial_message = "Chatbot: Welcome! Please choose a category for scholarships:\n" + "\n".join([f"{i + 1}. {based}" for i, based in enumerate(based_on)])
        self.display_message(initial_message)

    def go_back(self):
        if self.selected_scheme:
            self.selected_scheme = None
            self.display_schemes()
        elif self.selected_sector:
            self.selected_sector = None
            self.display_initial_message()

    def toggle_voice(self):
        if not self.voice_mode:
            self.display_message("Chatbot: Voice mode enabled. Say 'option 1', 'back', etc.")
            self.listen_voice_command()
        else:
            self.display_message("Chatbot: Voice mode disabled.")
        self.voice_mode = not self.voice_mode

    def listen_voice_command(self):
        with sr.Microphone() as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.display_message("Chatbot: Listening...")
                audio = self.recognizer.listen(source, timeout=5)
                self.process_voice_command(audio)
            except sr.WaitTimeoutError:
                self.display_message("Chatbot: Voice command timeout. Say 'option 1', 'back', etc.")
                self.listen_voice_command()

    def process_voice_command(self, audio):
        try:
            user_command = self.recognizer.recognize_google(audio).lower()
            self.display_message(f"User: {user_command}")
            self.handle_voice_command(user_command)
        except sr.UnknownValueError:
            self.display_message("Chatbot: Command not recognized.")
        except sr.RequestError as e:
            self.display_message(f"Chatbot: Speech recognition request failed: {e}")

    def handle_voice_command(self, user_command):
        if "option" in user_command:
            # Extract the number from the command
            try:
                number = ''.join(filter(str.isdigit, user_command))
                if number:
                    number = int(number)
                    self.user_entry.insert(tk.END, str(number))
                    self.send_message()
                else:
                    self.display_message("Chatbot: Unable to recognize the number in the command.")
            except ValueError:
                self.display_message("Chatbot: Unable to recognize the number in the command.")
        elif "back" in user_command:
            self.go_back()
        elif "stop" in user_command:
            self.display_message("Chatbot: Voice mode disabled.")
            self.voice_mode = False
        else:
            self.display_message("Chatbot: Command not recognized.")
            self.speak("Command not recognized.")  # Speak the unrecognized command

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()

