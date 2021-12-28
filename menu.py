class Menu:
    def __init__(self, title, options = [], default = -1, description = '', question = "Choose an option by it's index (.di)"):
        self.title = title
        self.description = description
        self.question = question 
        self.default = default
        self.options = options

    def showMenu():
        if question == '':
            question = title

        print(title)
        print(description)
        optionsCount = len(options) - 1
        for i in range(optionsCount): 
            print('['+(i+1)+']' + options[i])
       
        isValid = False
        while(not isValid):
            choice = input(question.replace('.df', default + 1))

            if choice == '':
                choice = default

            try:
                choice = int(choice)
                if (not choice in range(optionsCount)):
                    raise IndexError
                isValid = True
            except:
                print("Please enter a valid option by it's index.")

        return choice