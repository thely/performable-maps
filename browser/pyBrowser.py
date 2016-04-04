import webbrowser
filename = "http://localhost:8080"
chrome_path = "open -a /Applications/Google\ Chrome.app %s"
webbrowser.get(chrome_path).open(filename);
