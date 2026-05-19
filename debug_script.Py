import os
import datetime
import subprocess

def log_and_push():
    print("--- Assistant de Log Technique ---")
    log_file = "DEBUG_LOG.md"
    
    # On demande le contenu (tu colles ce que je te donne)
    print("Colle le bloc Markdown ici (Termine par 'FIN' sur une nouvelle ligne) :")
    lines = []
    while True:
        line = input()
        if line.strip() == "FIN":
            break
        lines.append(line)
    
    content = "\n".join(lines)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 1. Écriture dans le fichier
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n\n### Ajouté le {date_str}\n")
        f.write(content)
        f.write("\n" + "-"*40)

    # 2. Automatisation Git
    try:
        subprocess.run(["git", "add", log_file], check=True)
        subprocess.run(["git", "commit", "-m", f"docs: update debug log {date_str}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("\n✅ Journal mis à jour et poussé sur le Cloud !")
    except Exception as e:
        print(f"\n❌ Erreur Git : {e}")

if __name__ == "__main__":
    log_and_push()