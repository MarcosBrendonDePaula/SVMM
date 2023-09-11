from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
from src.infos import Infos
import i18n
class ContributorsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(i18n.t('contributors.title'))
        self.setGeometry(100, 100, 400, 250)

        layout = QVBoxLayout()

        contributors_container = QWidget()
        contributors_layout = QVBoxLayout()  # Usamos QVBoxLayout para organizar verticalmente

        for contributor in Infos.contributors:
            contributor_name = contributor['name']
            contributor_github = contributor['github']
            contributor_linkedin = contributor['linkedin']

            contributor_widget = QWidget()
            contributor_widget_layout = QHBoxLayout()  # Usamos QHBoxLayout para organizar horizontalmente
            
            contributor_name_label = QLabel(contributor_name)
            contributor_widget_layout.addWidget(contributor_name_label)

            # Use QSpacerItem para ajustar os elementos horizontalmente
            spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            contributor_widget_layout.addSpacerItem(spacer)

            if contributor_github:
                github_link = QLabel(f"<a href=\"{contributor_github}\">GitHub</a>")
                github_link.setTextFormat(Qt.TextFormat.RichText)
                github_link.setOpenExternalLinks(True)
                contributor_widget_layout.addWidget(github_link)

            if contributor_linkedin:
                linkedin_link = QLabel(f"<a href=\"{contributor_linkedin}\">LinkedIn</a>")
                linkedin_link.setTextFormat(Qt.TextFormat.RichText)
                linkedin_link.setOpenExternalLinks(True)
                contributor_widget_layout.addWidget(linkedin_link)

            contributor_widget.setLayout(contributor_widget_layout)
            contributors_layout.addWidget(contributor_widget)

        contributors_container.setLayout(contributors_layout)

        # Adicione a lista de contribuidores a um QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(contributors_container)

        layout.addWidget(scroll_area)

        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)
