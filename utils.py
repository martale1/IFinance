import re

def read_last_line_content_in_brackets():
    file_path = "/home/developer/PycharmProjects/learningProjects/IFinance/run_log.txt"
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            # Prendiamo l'ultima riga se disponibile
            last_line = lines[-1] if lines else ""
            # Trova il contenuto tra le parentesi quadre
            match = re.search(r'\[(.*?)\]', last_line)
            return match.group(1) if match else None
    except FileNotFoundError:
        return "Log file not found."

def read_last_lines_of_log():
    file_path="/home/developer/PycharmProjects/learningProjects/IFinance/run_log.txt"
    num_lines=3
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return lines[-num_lines:] if len(lines) >= num_lines else lines
    except FileNotFoundError:
        return ["Log file not found."]
