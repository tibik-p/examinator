from examinator import *

if __name__ == "__main__":

    all_questions, stats = load_all_questions()
    if not all_questions:
        print("Žádné otázky nebyly načteny. Aplikaci nelze spustit.")
        exit()

    new_test(all_questions)
