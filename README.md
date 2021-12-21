# Extract plan from pdf, png, jpf format files.

if you face error about poppler just download poppler-21.11.0 in ScissorsGUI "Folder"

pyinstaller --noconsole --add-binary "scissors.png";"." --add-binary "scissors.ui";"." --add-binary "scissorsPKG";"." --icon=./icons/scissors.ico ScissorsGUI.py
