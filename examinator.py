"""průběh aplikace - načtu otázky -> uživatel zadá jméno a kolik chce otázek(nesmí překročit limit dostupných otázek) 
-> poté se náhodně promíchají otázky a jejich odpovědi v nich a uživatel řeší test 
-> po vyřešení mu vyskočí report zpráva, kde je počet správných a špatných odpovědí, jaké odpovědi byly špatné, 
čas řešení testu a tento report se uloží do souboru, pak menu s pokračováním neb ukončením

otázky   - udělat aspoň 2 soubory otázek - první autor, pak dycky otázka a odpovědi zvlášť na řádek - 0 = špatně, 1 = správně, pouze 1 správná odpověď
         - apliakce musí vypisovat u každé otázky v testu autora a z jakého souboru to tu otázku bere
         - prázdný soubor to má přeskočit
         - dát .lower u 
         - ošetřit limit max otázek
průběh testu - napíšu jméno - ten student je buď do ukončení aplikace nebo startu testu s novým studentem "přihlášen"
             - vyberu kolik otázek - náhodně to vybere otázky a zamíchá to řešení
funkce - load_all_questions() - načtu všechny otázky na začátku
       - prepare_test() - výběr počtu otázek, "přihlášení" studenta
       - run_test() - samotný test
       - evaluate_test() - report testu
       - save_result() - uložení reportu do nového souboru, v názvu je i čas řešení
co předělat - kontrola správnosti .txt otázkového souboru
- nastavit si určité věci přes True / False - current student, index správnosti otázky
- zkusit předělat listy - možná zapracovat dict

"""
import random
import os
from datetime import datetime
from pathlib import Path


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_QUESTIONS = os.path.join(BASE_DIR, "Testy_zdroj_otazek")
DIR_RESULTS = os.path.join(BASE_DIR, "Vysledky_testu")

MIN_QUESTIONS_TOTAL = 10
GRADE_SCALE = [
    (90, 1),
    (75, 2),
    (60, 3),
    (45, 4),
    (0, 5)
]
LETTERS = ['a', 'b', 'c', 'd']


def load_all_questions():
    all_questions = []
    stats = {}

    if not os.path.exists(DIR_QUESTIONS):
        print(f"Složka {DIR_QUESTIONS} neexistuje!")
        return all_questions, stats

    for filename in os.listdir(DIR_QUESTIONS):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(DIR_QUESTIONS, filename)
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f if line.strip()]

        if not lines or not lines[0].startswith("Autor:"):
            print(f"Soubor {filename} přeskočen (chybný formát)")
            continue

        author = lines[0].replace("Autor:", "").strip()
        i = 1
        while i < len(lines):
            if lines[i].startswith("Otázka:"):
                question_text = lines[i].replace("Otázka:", "").strip()
                answers = []
                for j in range(1, 5):
                    try:
                        mark, text = lines[i + j].split(";", 1)
                        answers.append({
                            "text": text.strip(),
                            "correct": mark.strip() == "1"
                        })
                    except IndexError:
                        print(f"Chybný formát odpovědi v {filename}, otázka: {question_text}")
                        continue

                
                for idx, ans in enumerate(answers):
                    if ans['correct']:
                        correct_index = idx
                        break

                all_questions.append({
                    "text": question_text,
                    "answers": answers,
                    "author": author,
                    "source": filename,
                    "correct_index": correct_index
                })

                stats.setdefault(filename, {})
                stats[filename][author] = stats[filename].get(author, 0) + 1

                i += 5
            else:
                i += 1

    print(f"Načteno celkem {len(all_questions)} otázek.\n")
    for src, authors in stats.items():
        print(f"Ze souboru {src}:")
        for author, count in authors.items():
            print(f"  {count} otázky od autora {author}")
    print("\n")
    return all_questions, stats


def prepare_test(all_questions):
    if len(all_questions) < MIN_QUESTIONS_TOTAL:
        print(f"Nedostatek otázek (min {MIN_QUESTIONS_TOTAL}).")
        return None, None

    while True:
        student_name = input("Zadejte své jméno: ").strip()
        if student_name:
            break
        print("Jméno nesmí být prázdné.")

    while True:
        try:
            num_questions = int(input(f"Počet otázek (max {len(all_questions)}): "))
            if 1 <= num_questions <= len(all_questions):
                break
            print("Počet otázek mimo povolený rozsah.")
        except ValueError:
            print("Neplatný vstup. Zadejte číslo.")

    selected_questions = random.sample(all_questions, num_questions)

  
    for q in selected_questions:
        random.shuffle(q['answers'])
        for i, ans in enumerate(q['answers']):
            if ans['correct']:
                q['correct_index'] = i
                correct_text = ans['text']
                break

    return student_name, selected_questions


def generate_new_test(all_questions):
    while True:
        try:
            num_questions = int(input(f"Počet otázek pro nový test (max {len(all_questions)}): "))
            if 1 <= num_questions <= len(all_questions):
                break
            print("Počet otázek mimo povolený rozsah.")
        except ValueError:
            print("Neplatný vstup. Zadejte číslo.")

    selected_questions = random.sample(all_questions, num_questions)

    for q in selected_questions:
        random.shuffle(q['answers'])
        for i, ans in enumerate(q['answers']):
            if ans['correct']:
                q['correct_index'] = i
                break

    return selected_questions


def run_test(student_name, selected_questions):
    user_answers = []
    start_time = datetime.now()

    for idx, q in enumerate(selected_questions, start=1):
        print(f"\nOtázka {idx}: {q['text']}")
        print(f"(Autor: {q['author']}, Zdroj: {q['source']})")

        for i, ans in enumerate(q['answers']):
            print(f"  {LETTERS[i]}. {ans['text']}")

        while True:
            choice = input("Odpověď: ").strip().lower()
            if choice in LETTERS:
                user_index = LETTERS.index(choice)
                chosen_text = q["answers"][user_index]["text"]
                correct_text = q["answers"][q["correct_index"]]["text"]
                is_correct = user_index == q["correct_index"]

                user_answers.append({
    "question": q['text'],
    "chosen_text": chosen_text,
    "correct": is_correct,
    "correct_text": correct_text
})



                os.system("cls")
                break
            else:
                print("Neplatná volba. Zadej a, b, c nebo d.")

    end_time = datetime.now()
    total_time = end_time - start_time
    correct_count = sum(1 for a in user_answers if a['correct'])
    incorrect_answers = [a for a in user_answers if not a['correct']]

    print(f"\nTest dokončen! Čas řešení: {total_time}")
    return student_name, user_answers, total_time, correct_count, incorrect_answers, end_time


def evaluate_test(student_name, user_answers):
    total_questions = len(user_answers)
    if total_questions == 0:
        print("Žádné otázky nebyly zodpovězeny, test nelze vyhodnotit.")
        return "", 0, None  

    correct_count = sum(1 for ans in user_answers if ans['correct'])
    incorrect_answers = [ans for ans in user_answers if not ans['correct']]

    percent = (correct_count / total_questions) * 100
    for threshold, g in GRADE_SCALE:
        if percent >= threshold:
            grade = g
            break

    report_lines = [
        f"=== Report testu pro {student_name} ===",
        f"Počet otázek      : {total_questions}",
        f"Správné odpovědi  : {correct_count}",
        f"Špatné odpovědi   : {total_questions - correct_count}",
        f"Známka            : {grade}",
        f"Čas řešení        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    ]

    if incorrect_answers:
        report_lines.append("Špatně zodpovězené otázky:")
        
        for ans in user_answers:
            if not ans['correct']:
                report_lines.append(f"- {ans['question']}")
                report_lines.append(f"  Tvoje odpověď : {ans['chosen_text']}")
                report_lines.append(f"  Správná odpověď: {ans['correct_text']}")

    else:
        report_lines.append("Všechny otázky byly zodpovězeny správně!")

    report_text = "\n".join(report_lines)
    print("\n" + report_text)
    return report_text, correct_count, grade



def save_result(student_name, report_text, total_questions, grade):
    Path(DIR_RESULTS).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parts = student_name.strip().split()
    if len(parts) >= 2:
        filename_name = f"{parts[1]}_{parts[0]}"  
    else:
        filename_name = parts[0]

    filename = f"{filename_name}_{timestamp}_{total_questions}_{grade}.txt"
    filepath = os.path.join(DIR_RESULTS, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"\nReport uložen do souboru: {filepath}")
    return filepath

def new_test(all_questions, student_name=None, selected_questions=None):
    while True:
        choice = input("""
1 - nový test s novým studentem
2 - nový test se stejným studentem
3 - ukončit aplikaci
Volba: """).strip()

        if choice == "1":
            student_name, selected_questions = prepare_test(all_questions)
            if not selected_questions:
                print("Test nelze spustit - nedostatek otázek.")
                continue
            student_name, user_answers, *_ = run_test(student_name, selected_questions)
        elif choice == "2":
            selected_questions = generate_new_test(all_questions)
            student_name, user_answers, *_ = run_test(student_name, selected_questions)

            
        elif choice == "3":
            print("Konec aplikace.")
            break
        else:
            print("Neplatná volba. Zadej 1, 2 nebo 3.")
            continue

        
        report_text, correct_count, grade = evaluate_test(student_name, user_answers)
        save_result(student_name, report_text, len(selected_questions), grade)


   





