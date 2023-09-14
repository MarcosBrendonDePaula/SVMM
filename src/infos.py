import i18n
class Infos():
    version = "0.3.2-beta"
    contributors = [
        {
            "name"    : "Marcos Brendon",
            "github"  : "https://github.com/MarcosBrendonDePaula",
            "linkedin": "https://www.linkedin.com/in/marcosbrendon/",
            "website" : "https://marcosbrendon.com/"
        },
        {
            "name"    : "Henri Eduardo",
            "github"  : "https://github.com/Henrixss",
            "linkedin": "https://www.linkedin.com/in/henri-eduardo-prieto-nunes-13a036187/",
            "website" : None
        },
        {
            "name"    : "Mateus Henrique",
            "github"  : "https://github.com/MateusHnr1",
            "linkedin": None,
            "website" : None
        },
        {
            "name"    : "Eric Tierre",
            "github"  : "https://github.com/EricTierre",
            "linkedin": "https://www.linkedin.com/in/erictierre/",
            "website" : "https://erictierre.com/"
        },
        {
            "name"    : "ChatGPT",
            "github"  : None,
            "linkedin": None,
            "website" : "https://openai.com/chatgpt"
        },
    ]
    about = i18n.t('about.text')
    limit_connections = 50
    pass