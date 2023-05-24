import glob


def separate_atf():
    tablets = {}
    with open('github_repository/cdliatf_unblocked.atf', encoding='utf-8') as file:
        text = file.read()
        text = text.split('\n')
        text = [t.strip() for t in text]
        text = [t for t in text if len(t)]
        starts = [i for i in range(len(text)) if text[i][:2] == '&P'] + [len(text)]
        for i in range(len(starts) - 1):
            tablets[text[starts[i]][1:8]] = '\n'.join(text[starts[i]:starts[i + 1]])
    for tablet in tablets:
        with open('cdli_artefact_transliterations/full/' + tablet + '.txt', 'w', encoding='utf-8') as file:
            file.write(tablets[tablet])


def check_line(line):
    if line[0].isdigit():
        return ' '.join(line.split(' ')[1:])
    elif line[0] == '@':
        return ''
    return None


def check_line_translation(line, lan):
    if line[:6+len(lan)] == '#tr.'+lan+': ':
        return ' '.join(line.split(' ')[1:])
    elif line[0] == '@':
        return ''
    return None


def extract_text(full):
    lines = full.split('\n')
    lines = [check_line(line) for line in lines if check_line(line) is not None]
    lines = [lines[i] for i in range(len(lines)) if lines[i] + lines[i-1] != '']
    return '\n'.join(lines)


def extract_languages(full):
    lines = full.split('\n')
    languages = []
    for line in lines:
        if line[:4] == '#tr.':
            languages.append(line[4:].split(' ')[0][:-1])
    return list(set(languages))


def extract_translation(full, lan):
    lines = full.split('\n')
    lines = [check_line_translation(line, lan) for line in lines if check_line_translation(line, lan) is not None]
    lines = [lines[i] for i in range(len(lines)) if lines[i] + lines[i-1] != '']
    return '\n'.join(lines)


def extract_all_texts():
    for f in glob.glob('cdli_artefact_transliterations/full/*'):
        name = f.split('\\')[-1].split('.')[0]
        with open(f, encoding='utf-8') as file:
            fr = file.read()
            text = extract_text(fr)
            with open('cdli_artefact_transliterations/text/' + name + '_text.txt', 'w', encoding='utf-8') as ft:
                ft.write(text)
            languages = extract_languages(fr)
            translations = {lan: extract_translation(fr, lan) for lan in languages}
            for translation in translations:
                with open('cdli_artefact_transliterations/translations/' + name + '_translation_' + translation + '.txt', 'w', encoding='utf-8') as ft:
                    ft.write(translations[translation])


# separate_atf()
extract_all_texts()
