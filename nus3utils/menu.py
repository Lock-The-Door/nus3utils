class Menu:
    def __init__(self, title, options = [], default = -1, description = '', question = "Choose an option by it's index (.di): "):
        self.title = title
        self.description = description
        self.question = question 
        self.default = default
        self.options = options

    def Display(self):
        if self.question == '':
            self.question = self.title

        print(self.title)
        print(self.description)
        optionsCount = len(self.options)
        for i in range(optionsCount): 
            print('['+str(i+1)+'] ' + self.options[i])
       
        isValid = False
        while(not isValid):
            choice = input(self.question.replace('.di', str(self.default)))

            if choice == '':
                choice = self.default

            try:
                choice = int(choice) - 1
                if (not choice in range(optionsCount)):
                    raise IndexError
                isValid = True
            except:
                print("Please enter a valid option by it's index.")

        return choice